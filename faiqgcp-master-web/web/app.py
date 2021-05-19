# import hmac
# import hashlib
"""."""

import os
# import json
# import git
import random

from flask import (Flask, render_template, jsonify, request, session, flash,
                   url_for, redirect)
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
# from flask_openid import OpenID
from werkzeug.utils import secure_filename

import pyexcel


UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'ods'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/mayaQuest_gcp.db'
db = SQLAlchemy(app)
app.secret_key = '5mr6TTSTuz7Xk53'
app.config['secret_key'] = '5mr6TTSTuz7Xk53'
app.config['SESSION_TYPE'] = 'filesystem'
SESSION_TYPE = 'filesystem'
# w_secret = os.environ['WEBHOOK_SECRET']

# oid = OpenID(app, 'store', safe_roots=[])
sess = Session()
sess.init_app(app)


class Questions(db.Model):
    __tablename__ = "Questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(String)
    choices = relationship("Choices")
    topic_id = Column(Integer, ForeignKey('Topics.id'))


class Choices(db.Model):
    __tablename__ = "Choices"
    q_id = Column(Integer, ForeignKey('Questions.id'))
    choice = db.Column(String)
    choice_type = db.Column(Integer)
    answer = db.Column(Integer)
    id = db.Column('id', Integer, primary_key=True)


class Topics(db.Model):
    __tablename__ = "Topics"
    id = db.Column('id', Integer, primary_key=True)
    Name = db.Column(String)


# def read_questions_from_file(file_name):
#     spreadsheet = pyexcel.get_sheet(
#         file_name=file_name)
#     questions = [row for row in spreadsheet]
#     return questions[1:]


# def process_data(data):
#     for d in data:
#         # print(f"d: {d}")
#         question, choices, ans = d[0], d[1:-1], d[-1]
#         yield question, choices, ans


def get_imported_questions(topic_id, file_name):
    spreadsheet = pyexcel.get_sheet(
        file_name=file_name)
    questions = [row for row in spreadsheet]
    for d in questions[1:]:
        # print(f"d: {d}")
        question, choices, ans = d[0], d[1:-1], d[-1]
        yield question, choices, ans


def import_questions(topic_id, file_name):
    for question, choices, ans in get_imported_questions(topic_id, file_name):
        # print(f"Adding: question={question}, choices={choices}, ans={ans}")
        add_question(topic_id, question, choices, ans)


"""

For Authentication and Authorization
"""


# class User(db.Model):
#     """
#     group:
#         0 - Default User
#         10 - Question Manager
#         20 - Admin
#     """
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(60))
#     email = Column(String(200))
#     group = Column(Integer)  # 0
#     openid = Column(String(200))

#     def __init__(self, name, email, openid):
#         self.name = name
#         self.email = email
#         self.openid = openid


# @app.before_request
# def lookup_current_user():
#     g.user = None
#     if 'openid' in session:
#         openid = session['openid']
#         g.user = User.query.filter_by(openid=openid).first()


# @app.route('/login', methods=['GET', 'POST'])
# @oid.loginhandler
# def login():
#     if g.user is not None:
#         return redirect(oid.get_next_url())
#     if request.method == 'POST':
#         openid = request.form.get('openid')
#         if openid:
#             return oid.try_login(openid, ask_for=['email', 'nickname'],
#                                  ask_for_optional=['fullname'])
#     return render_template('login.html', next=oid.get_next_url(),
#                            error=oid.fetch_error())


# @oid.after_login
# def create_or_login(resp):
#     session['openid'] = resp.identity_url
#     user = User.query.filter_by(openid=resp.identity_url).first()
#     if user is not None:
#         flash(u'Successfully signed in')
#         g.user = user
#         return redirect(oid.get_next_url())
#     return redirect(url_for('create_profile', next=oid.get_next_url(),
#                             name=resp.fullname or resp.nickname,
#                             email=resp.email))


# @app.route('/create-profile', methods=['GET', 'POST'])
# def create_profile():
#     if g.user is not None or 'openid' not in session:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash(u'Error: you have to provide a name')
#         elif '@' not in email:
#             flash(u'Error: you have to enter a valid email address')
#         else:
#             flash(u'Profile successfully created')
#             db_session.add(User(name, email, session['openid']))
#             db_session.commit()
#             return redirect(oid.get_next_url())
#     return render_template('create_profile.html', next=oid.get_next_url())


# @app.route('/logout')
# def logout():
#     session.pop('openid', None)
#     flash(u'You were signed out')
#     return redirect(oid.get_next_url())


"""
For Quest
"""


def add_question(topic_id, question, choices, ans):
    old_question = Questions.query.filter_by(question=question).first()
    if old_question:
        return False  # We are going to ignore duplicate questions.

    quest = Questions(question=question, topic_id=topic_id)
    if isinstance(ans, str) and "," in ans:
        ans = ans.split(",")
    else:
        ans = (ans,)
    for index, option in enumerate(choices):
        _ans = index in ans
        choice = Choices(choice=option,
                         choice_type=0, answer=_ans)
        db.session.add(choice)
        quest.choices.append(choice)
    print(quest)
    db.session.add(quest)
    db.session.commit()
    return True


@app.route("/management_console")
def manage_topics():
    topics = Topics.query.all()
    return render_template('management_console.html', topics=topics)


@app.route("/update_topics", methods=['POST'])
def update_topics():
    print("Updating the topics...", flush=True)
    print(request.form)
    try:
        for data in request.form:
            print(data)
            topic_name = request.form[data].strip()
            topic = Topics.query.filter_by(id=data).first()
            if topic_name:
                topic.Name = topic_name
            else:
                db.session.delete(topic)
            db.session.commit()
        return jsonify({"result": True, "msg": "Topics updated"})
    except Exception as e:
        return jsonify({"result": False, "msg": e})


@app.route("/add_topic", methods=['POST'])
def add_topic():
    print(request.form['topic'])
    new_quest_name = request.form['topic']
    quest_name = db.session.query(Topics).with_entities(Topics.Name).filter(
        Topics.Name.ilike("%{}%".format(new_quest_name))).all()
    # quest_name = Topics.query.with_entities(Topics.Name).filter_by(
    #     Name=new_quest_name).all()
    for q_name in quest_name:
        print(q_name[0].casefold())
        if q_name[0].casefold() == new_quest_name.casefold():

            print("Result Failed: Topic already present")
            return jsonify({"result": False, "msg": "Topic already present"})
    try:
        new_topic = Topics(Name=new_quest_name)
        db.session.add(new_topic)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": False, "msg": e})

    return jsonify({"result": True, "msg": "Topic Successfully Added"})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_questions", methods=["POST"])
def upload_questions():
    topic_id = request.form['topic_id']
    print("request.form", request.form, flush=True)
    print("request.files:", request.files, flush=True)
    if 'file_0' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file_0']
    print("file.filename:", file.filename)
    print("allowed_file(file.filename):", allowed_file(file.filename))
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_name)
        import_questions(topic_id, file_name)

    return jsonify({"result": True, "msg": "File uploaded"})


@app.route("/edit_question:<int:qid>", methods=['GET'])
def edit_question(qid):

    question = Questions.query.filter_by(
        id=qid).first()

    return render_template("edit_question.html", question=question,
                           choices=question.choices)


@app.route("/save_question", methods=['POST'])
def save_question():
    data = request.get_json()
    # print(data)
    # Lets update Question
    updated_choices = data['choices']

    # print("data['choices']: ", updated_choices)
    try:
        qid = data['question']['id']
        question = Questions.query.filter_by(
            id=qid).first()

        question.question = data['question']['question']
        # print("Expected: ", data['question']['question'])
        # print("Actual: ", question.question)
        for choice in updated_choices:
            _ch = Choices.query.filter_by(id=choice['id']).first()
            _ch.choice = choice['choice']
            _ch.answer = choice['ans']
            db.session.add(_ch)

        db.session.add(question)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": False, "msg": e})
    return jsonify({"result": True, "msg": "Data Updated"})


@app.route("/get_all_questions:<int:tid>", methods=["GET"])
def get_all_questions(tid):
    questions = Questions.query.with_entities(
        Questions.id, Questions.question).filter_by(topic_id=tid).all()

    return jsonify(questions)


@app.route("/get_quest:<qid>", methods=['GET'])
def get_quest(qid):
    if qid:
        question = Questions.query.with_entities(Questions.question).filter_by(
            id=qid).first()[0]
        q_choices = Choices.query.with_entities(Choices.id,
                                                Choices.choice).filter_by(
            q_id=qid).all()
    return jsonify(question=question, choices=q_choices)


# @app.route('/start_quest:<int:quest_id>', methods=['GET'])
@app.route("/start_quest", methods=['POST'])
def start_quest():
    print(request.form['quests'])
    quest_id = int(request.form['quests'])
    count = Questions.query.with_entities(Questions.id).filter_by(
        topic_id=quest_id).all()
    print("count:", len(count))
    lst = random.sample(count, 20)
    session['questions'] = lst
    return redirect(url_for('next_question'))


@app.route('/validate:<int:q_id>', methods=['GET'])
def validate(q_id):
    # q_id = request.form['quest_id']
    ans = Choices.query.with_entities(
        Choices.id).filter_by(q_id=q_id, answer=1).all()
    return jsonify(ans)


@app.route('/next_q')
def next_question():
    if session['questions']:
        qid = session['questions'].pop()
        if qid:
            # print(qid, session['questions'], len(session['questions']))
            return render_template('index.html', qid=qid[0])
    return redirect(url_for('select_quest'))


@app.route("/get_questions_list:<int:tid>", methods=["GET"])
def get_questions_list(tid):
    count = Questions.query.filter_by(topic_id=tid).count()
    lst = random.sample(range(1, count), 30)
    return jsonify(lst)


@app.route("/")
def select_quest():
    quests = Topics.query.all()
    return render_template('select_quest.html', quests=quests,
                           action="quests")


# Web Hook Start


# def is_valid_signature(x_hub_signature, data, private_key):
#     hash_algorithm, github_signature = x_hub_signature.split('=', 1)
#     algorithm = hashlib.__dict__.get(hash_algorithm)
#     encoded_key = bytes(private_key, 'latin-1')
#     mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
#     return hmac.compare_digest(mac.hexdigest(), github_signature)


# @app.route('/update_server', methods=['POST'])
# def webhook():
#     if request.method != 'POST':
#         return 'OK'
#     else:
#         abort_code = 418
#         # Do initial validations on required headers
#         if 'X-Github-Event' not in request.headers:
#             abort(abort_code)
#         if 'X-Github-Delivery' not in request.headers:
#             abort(abort_code)
#         if 'X-Hub-Signature' not in request.headers:
#             abort(abort_code)
#         if not request.is_json:
#             abort(abort_code)
#         if 'User-Agent' not in request.headers:
#             abort(abort_code)
#         ua = request.headers.get('User-Agent')
#         if not ua.startswith('GitHub-Hookshot/'):
#             abort(abort_code)

#         event = request.headers.get('X-GitHub-Event')
#         if event == "ping":
#             return json.dumps({'msg': 'Hi!'})
#         if event != "push":
#             return json.dumps({'msg': "Wrong event type"})

#         x_hub_signature = request.headers.get('X-Hub-Signature')
#         # webhook content type should be application/json for request.data
#         # to have the payload
#         # request.data is empty in case of x-www-form-urlencoded
#         if not is_valid_signature(x_hub_signature, request.data, w_secret):
#             print('Deploy signature failed: {sig}'.format(s
# ig=x_hub_signature))
#             abort(abort_code)

#         payload = request.get_json()
#         if payload is None:
#             print('Deploy payload is empty: {payload}'.format(
#                 payload=payload))
#             abort(abort_code)

#         if payload['ref'] != 'refs/heads/master':
#             return json.dumps({'msg': 'Not master; ignoring'})

#         repo = git.Repo('/var/www/sites/mysite')
#         origin = repo.remotes.origin

#         pull_info = origin.pull()

#         if len(pull_info) == 0:
#             return json.dumps({'msg':
# "Didn't pull any information from remote!"})
#         if pull_info[0].flags > 128:
#             return json.dumps({'msg':
# "Didn't pull any information from remote!"})

#         commit_hash = pull_info[0].commit.hexsha
#         build_commit = f'build_commit = "{commit_hash}"'
#         print(f'{build_commit}')
#         return 'Updated PythonAnywhere server to commit {commit}'.format(
    # commit=commit_hash)


if __name__ == "__main__":
    app.run(debug=True, port=8080)
