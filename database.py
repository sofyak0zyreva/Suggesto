import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
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
    rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(BigInteger, nullable=True)


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recommendation_id = Column(Integer, ForeignKey(
        'recommendations.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5

    user = relationship("User", backref="ratings")
    recommendation = relationship("Recommendation", backref="ratings")


load_dotenv()
# DATABASE_URL = "sqlite:///recommendations.db"
DATABASE_URL = os.getenv('DATABASE_URL') or "sqlite:///database.db"

# Создание подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
