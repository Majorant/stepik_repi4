import os
import json

from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import func
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired


app = Flask(__name__)
# Настраиваем приложение
app.config["DEBUG"] = True
# - URL доступа к БД берем из переменной окружения DATABASE_URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("CSRF_KEY")

# Создаем подключение к БД
db = SQLAlchemy(app)
# Создаем объект поддержки миграций
migrate = Migrate(app, db)


teachers_goals_association = db.Table(
    'teachers_goals',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
    db.Column("goal_id", db.Integer, db.ForeignKey('goals.id')),
)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture  = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    free = db.Column(JSON)
    goals = db.relationship('Goal', secondary=teachers_goals_association, back_populates='teachers')


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    picture = db.Column(db.Integer, nullable=False)
    teachers = db.relationship('Teacher', secondary=teachers_goals_association, back_populates='goals')
    client_goal = db.relationship('ClientRequest')


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    dow = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    teacher = db.relationship('Teacher')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))


class ClientRequest(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_days = db.Column(db.String, nullable=False)
    goal_id = db.Column(db.Integer,db.ForeignKey('goals.id'))
    request_goal = db.relationship('Goal')


class clientForm(FlaskForm):
    client_name = StringField('Вас зовут', [InputRequired()])
    client_phone = StringField('Ваш телефон', [InputRequired()])


@app.route('/')
def index():
    teachers = db.session.query(Teacher).order_by(func.random()).limit(6).all()
    goals = db.session.query(Goal).all()
    return render_template('index.html',
                            teachers=teachers,
                            goals=goals,
                            )


@app.route('/all_teachers/')
@app.route('/all_teachers/<sort>/')
def all_teachers_view(sort=None):
    if sort is None:
        teachers = db.session.query(Teacher).order_by(func.random()).all()
    elif sort == 'rating':
        teachers = db.session.query(Teacher).order_by(Teacher.rating).all()
    elif sort == 'rating_desc':
        teachers = db.session.query(Teacher).order_by(Teacher.rating.desc()).all()
    elif sort == 'price':
        teachers = db.session.query(Teacher).order_by(Teacher.price).all()
    elif sort == 'price_desc':
        teachers = db.session.query(Teacher).order_by(Teacher.price.desc()).all()
    else:
        teachers = db.session.query(Teacher).order_by(func.random()).all()

    goals = db.session.query(Goal).all()
    return render_template('index.html',
                            teachers=teachers,
                            goals=goals,
                            all_teachers=True,
                            )


@app.route('/goals/<goal>/')
def goals(goal):
    q_goal = db.session.query(Goal).filter(Goal.goal == goal).scalar()
    return render_template('goal.html', teachers=q_goal.teachers, t_goal=q_goal.name)


@app.route('/profiles/<id>/')
def profiles(id):
    teacher=db.session.query(Teacher).get_or_404(id)
    return render_template('profile.html',
                            teacher=teacher,
                            schedule=json.loads(teacher.free))


@app.route('/request/', methods=['GET', 'POST'])
def request_view():
    if request.method == 'POST':
        client_goal = db.session.query(Goal).get_or_404(request.form.get('goal_id'))

        client_request = ClientRequest(client_name=request.form.get('client_name'),
                                        client_phone=request.form.get('client_phone'),
                                        client_days=request.form.get('time'),
                                        goal_id=client_goal.id,
                                        )
        db.session.add(client_request)
        db.session.commit()
        return render_template('request_done.html',
                                client_request=client_request,
                                goal_name=client_goal.name,
                                )
    else:
        form = clientForm()
        return render_template('request.html',
                                form=form,
                                goals=db.session.query(Goal).all(),
                                )


@app.route('/booking/<id>/<dow>/<time>', methods=['GET', 'POST'])
def booking(id, dow, time):
    if request.method == 'POST':
        booking = Booking(client_name=request.form.get('client_name'),
                            client_phone=request.form.get('client_phone'),
                            dow=request.form.get('dow'),
                            time=request.form.get('time'),
                            teacher_id=request.form.get('teacher_id'),
                            )
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_done.html', booking=booking)
    else:
        form = clientForm()
        teacher = db.session.query(Teacher).get_or_404(id)
        return render_template('booking.html', teacher=teacher, dow=dow, time=time, form=form)


@app.errorhandler(500)
def render_server_error(error):
    return "Что-то не так, но мы все починим. Error 500", 500


@app.errorhandler(404)
def render_server_error(error):
    print(error)
    return "Что-то не так, но мы все починим:\n\r{}".format(error), 404


if __name__ == 'main':
    app.run()
