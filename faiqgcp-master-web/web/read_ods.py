import pyexcel

# import sqlalchemy as db
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# engine = db.create_engine('sqlite:///mayaquest.db')
# connection = engine.connect()
# Base = declarative_base()

# Session = sessionmaker(bind=engine)
# session = Session()


# class Questions(Base):
#     __tablename__ = "Questions"
#     id = Column(Integer, primary_key=True)
#     question = Column(String)
#     choices = relationship("Choices")
#     topic_id = Column(Integer, ForeignKey('Topics.id'))


# class Choices(Base):
#     __tablename__ = "Choices"
#     q_id = Column(Integer, ForeignKey('Questions.id'))
#     choice = db.Column(String)
#     choice_type = db.Column(Integer)
#     answer = db.Column(Integer)
#     id = db.Column('id', Integer, primary_key=True)


# class Topics(Base):
#     __tablename__ = "Topics"
#     id = db.Column('id', Integer, primary_key=True)
#     Name = db.Column(String)


def read_questions_from_file(file_name):
    spreadsheet = pyexcel.get_sheet(
        file_name=file_name)
    questions = [row for row in spreadsheet]
    return questions[1:]


def process_data(data):
    for d in data:
        # print(f"d: {d}")
        question, choices, ans = d[0], d[1:-1], d[-1]
        yield question, choices, ans


# def add_question(topic_id, question, choices, ans):
#     # topic = Topics().find
#     quest = Questions(question=question, topic_id=topic_id)
#     if isinstance(ans, str) and "," in ans:
#         ans = ans.split(",")
#     else:
#         ans = (ans,)
#     for index, option in enumerate(choices):
#         _ans = index in ans
#         choice = Choices(choice=option,
#                          choice_type=0, answer=_ans)
#         session.add(choice)
#         quest.choices.append(choice)
#     print(quest)
#     session.add(quest)
#     session.commit()
# data = read_questions_from_file("/home/mayank/Documents/Questions.ods")

# print(data)
# for question, choices, ans in process_data(data):
#     print(f"question={question}, choices={choices}, ans={ans}")
#     add_question(0, question, choices, ans)
