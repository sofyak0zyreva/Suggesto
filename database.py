# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Определяем базовый класс для всех моделей
Base = declarative_base()

# Модель для пользователей


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))

    # связь с рекомендациями
    recommendations = relationship("Recommendation", backref="user", lazy=True)

# Модель для рекомендаций


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    category = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


# Создание подключения к базе данных
engine = create_engine('sqlite:///recommendations.db')

# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
