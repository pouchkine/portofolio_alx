from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from flask_login import UserMixin

Base = declarative_base()

# Table d'association pour la relation many-to-many entre User et Course
user_course = Table('user_course', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

class UserCourse(Base): 
    __tablename__ = 'course_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

class Score(Base):
    __tablename__ = 'score_user'
    id = Column(Integer, primary_key=True)
    course_user_id = Column(Integer, ForeignKey('course_users.id'), nullable=False)
    score =  Column(Integer, nullable=False)

class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)
    courses = relationship('Course', secondary=user_course, back_populates='users')

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher = relationship('User', backref='courses_taught')
    users = relationship('User', secondary=user_course, back_populates='courses')
    levels = relationship('Level', backref='course', lazy=True)

class Level(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True)
    difficulte = Column(String(50), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    chapters = relationship('Chapter', backref='level', lazy=True)

class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    video = Column(String(100), nullable=False)
    article = Column(Text, nullable=True)
    level_id = Column(Integer, ForeignKey('levels.id'), nullable=False)
    qcms = relationship('Question', backref='chapter', lazy=True)

class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    question_text = Column(String(250), nullable=False)
    first = Column(String(250), nullable=False)
    second = Column(String(250), nullable=False)
    tirth = Column(String(250), nullable=False)
    correct_answer = Column(String(250), nullable=False)
    rang = Column(Integer, nullable=False)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)

# Créer l'engine et la session
engine = create_engine('mysql+pymysql://florian:Mot2passe_@localhost/PixelDb')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
#
