# database.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, create_engine, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# User


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    joined_at = Column(DateTime, default=datetime.utcnow)

# Group


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    join_code = Column(String(10), unique=True)
    created_by = Column(Integer, ForeignKey('users.id'))

# User-qroup connection


class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

# Recs


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String(50))  # "Фильм", "Книга", "Место", "Музыка"
    title = Column(String(200))
    author = Column(String(200))  # или Адрес, если место
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Ratings


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    score = Column(Float)  # Например: 8.5/10

# Reminders


class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))
    day_of_week = Column(Integer)  # 0 = Понедельник, 6 = Воскресенье
    time_of_day = Column(String(5))  # Часы:Минуты ("18:00")


# Database connections
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
