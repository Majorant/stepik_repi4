import os

from flask import Flask, render_template, request, abort
import json
from flask_wtf.csrf import CSRFProtect
from random import sample
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON



DB = 'data.json'
CLIENT_BOOKING_FILE = 'booking.json'
CLIENT_REQUEST_FILE = ' request.json'


app = Flask(__name__)
# Настраиваем приложение
app.config["DEBUG"] = True
# - URL доступа к БД берем из переменной окружения DATABASE_URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    # goals_booking = db.relationship('Booking', back_populates='teachers')

    with open('data.json', 'r') as jf:
        data = json.load(jf)


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    teachers = db.relationship('Teacher', secondary=teachers_goals_association, back_populates='goals')
    # client_goal = db.relationship('ClientRequest', back_populates='clients_request')


class Booking(db.Model):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_dow = db.Column(db.String, nullable=False)
    client_time = db.Column(db.String, nullable=False)
    teacher = db.relationship('Teacher')
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))


class ClientRequest(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_days = db.Column(db.String, nullable=False)
    # client_goal = db.relationship('Goal', back_populates='goal')


@app.route('/')
def index():
    with open(DB, 'r') as jf:
        data = json.load(jf)
    samples = list()
    if request.endpoint == 'index' or request.endpoint == '/':
        samples=sample(range(0,len(data['teachers'])), 6)


    return render_template('index.html',
                            samples=samples,
                            goals=data['goals'],
                            teachers=data['teachers'],
                            goals_pic=data['goals_pic'],
                            )


@app.route('/all_teachers/')
def all_teachers_view():
    with open(DB, 'r') as jf:
        data = json.load(jf)
    return render_template('index.html',
                            samples=range(len(data['teachers'])),
                            goals=data['goals'],
                            teachers=data['teachers'],
                            goals_pic=data['goals_pic'],
                            )


@app.route('/goals/<goal>/')
def goals(goal):
    g = db.session.query(Goal).filter(Goal.goal == goal).first()
    t = db.session.query(Teacher).filter(Teacher.goals in g)
    print(t.first)
    with open(DB, 'r') as jf:
        data = json.load(jf)

    try:
        t_goal = data['goals'][goal]
    except KeyError as e:
        abort(404)

    teachers = list()
    for teacher in data['teachers']:
        if goal in teacher['goals']:
            teachers.append(teacher)
    return render_template('goal.html', teachers=teachers, t_goal=t_goal, goal_pic=data['goals_pic'][goal])


@app.route('/profiles/<id>/')
def profiles(id):
    teacher = db.session.query(Teacher).get_or_404(id)
    profile_info = {'id': str(id),
                    'name' : teacher.name,
                    'goals' : [goal.name for goal in teacher.goals],
                    'rating' : teacher.rating,
                    'price' : teacher.price,
                    'about' : teacher.about,
                    'image_url' : teacher.picture,
    }
    return render_template('profile.html', info=profile_info, schedule=json.loads(teacher.free), goals=[])


@app.route('/request/', methods=['GET'])
def request_view():
    with open(DB, 'r') as jf:
        goals = json.load(jf)['goals']
    return render_template('request.html', goals=goals)


@app.route('/request_done/', methods=['POST'])
def request_done_view():
    client_name=request.form.get('clientName')
    client_phone=request.form.get('clientPhone')
    client_time=request.form.get('time')
    client_goal=request.form.get('goal')

    with open(DB, 'r') as jf:
        goals = json.load(jf)['goals']

    try:
        with open(CLIENT_REQUEST_FILE, "r") as jf:
            client_requests = json.load(jf) or []
    except FileNotFoundError:
        client_requests = []

    client_requests.append({'client_name': client_name,
                            'client_phone': client_phone,
                            'client_time': client_time,
                            'client_goal': client_goal,
        })

    with open(CLIENT_REQUEST_FILE, 'w') as jf:
        json.dump(client_requests, jf, ensure_ascii=False)

    return render_template('request_done.html',
                            client_name=client_name,
                            client_phone=client_phone,
                            client_time=client_time,
                            client_goal=client_goal,
                            goals=goals,
                            )


@app.route('/booking/<id>/<dow>/<time>')
def booking(id, dow, time):
    profile_info = dict()
    schedule = dict()

    with open(DB, 'r') as jf:
        data = json.load(jf)

    for teacher in data['teachers']:
        if teacher['id'] == int(id):
            profile_info = {'id': id,
                            'name' : teacher['name'],
                            'image_url' : teacher['picture'],
            }
            break
    t_time = time + ':00'
    return render_template('booking.html', info=profile_info, dow=dow, time=t_time)


@app.route('/booking_done/', methods=["POST"])
def booking_done():
    teacher_id=request.form.get('clientTeacher')
    client_name=request.form.get('clientName')
    client_phone=request.form.get('clientPhone')
    client_dow=request.form.get('clientWeekday')
    client_time=request.form.get('clientTime')

    try:
        with open(CLIENT_BOOKING_FILE, "r") as jf:
            client_requests = json.load(jf) or []
    except FileNotFoundError:
        client_requests = []

    client_requests.append({'teacher': teacher_id,
                            'client_name': client_name,
                            'client_phone': client_phone,
                            'client_dow': client_dow,
                            'client_time': client_time,
        })
    with open(CLIENT_BOOKING_FILE, 'w') as jf:
        json.dump(client_requests, jf, ensure_ascii=False)

    return render_template('booking_done.html',
                            client_name=request.form.get('clientName'),
                            client_phone=request.form.get('clientPhone'),
                            client_dow=request.form.get('clientWeekday'),
                            client_time=request.form.get('clientTime'),
                            )


@app.errorhandler(500)
def render_server_error(error):
    return "Что-то не так, но мы все починим. Error 500", 500


@app.errorhandler(404)
def render_server_error(error):
    print(error)
    return "Что-то не так, но мы все починим:\n\n{}".format(error), 404


if __name__ == 'main':
    app.run()
