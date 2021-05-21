import os
import random
import pyexcel

from flask import (Flask, render_template, jsonify, request, session, flash,
                   url_for, redirect)
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename




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
        print("i am here inside qid")
        question = Questions.query.with_entities(Questions.question).filter_by(id=qid).first()[0]
        q_choices = Choices.query.with_entities(Choices.id,Choices.choice).filter_by(q_id=qid).all()
        print("question="+str(question))
        print("choices="+str(type(q_choices)))
        list_choices=[]
        for item in q_choices:
            list_choices.append([item[0],str(item[1])])
    return jsonify({"question":question,"choices":list_choices})


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
    print(session['questions'])
    if session['questions']:
        qid = session['questions'].pop()
        if qid:
            print("____________________________________________")
            print(qid, session['questions'], len(session['questions']))
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


if __name__ == "__main__":
    app.run(debug=True, port=8080)
