from flask import Flask, render_template, request, abort
import json
from flask_wtf.csrf import CSRFProtect
from random import sample

DB = 'data.json'
CLIENT_BOOKING_FILE = 'booking.json'
CLIENT_REQUEST_FILE = ' request.json'


app = Flask(__name__)
app.secret_key = "K7SrRxgSFVSnKMkO"


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
    profile_info = dict()
    schedule = dict()

    with open(DB, 'r') as jf:
        data = json.load(jf)

    for teacher in data['teachers']:
        if teacher['id'] == int(id):
            profile_info = {'id': id,
                            'name' : teacher['name'],
                            'goals' : teacher['goals'],
                            'rating' : teacher['rating'],
                            'price' : teacher['price'],
                            'about' : teacher['about'],
                            'image_url' : teacher['picture'],
            }
            schedule = teacher['free']
            break

    return render_template('profile.html', info=profile_info, schedule=schedule, goals=data['goals'])


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
    return "Что-то не так, но мы все починим", 500


@app.errorhandler(404)
def render_server_error(error):
    print(error)
    return "Что-то не так, но мы все починим:\n\n{}".format(error), 404


if __name__ == 'main':
    app.run()
