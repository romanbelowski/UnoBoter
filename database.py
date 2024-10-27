from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./tutor_bot.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"  # Виправлено з tablename на __tablename__

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)
    full_name = Column(String)
    is_teacher = Column(Boolean, default=False)

    bookings = relationship("Booking", back_populates="student")
    lessons = relationship("Lesson", back_populates="teacher")


class Lesson(Base):
    __tablename__ = "lessons"  # Виправлено з tablename на __tablename__

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    date_time = Column(DateTime, index=True)
    is_booked = Column(Boolean, default=False)

    teacher = relationship("User", back_populates="lessons")
    booking = relationship("Booking", back_populates="lesson", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"  # Виправлено з tablename на __tablename__

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="confirmed")

    lesson = relationship("Lesson", back_populates="booking")
    student = relationship("User", back_populates="bookings")


class NotificationSetting(Base):
    __tablename__ = "notification_settings"  # Виправлено з tablename на __tablename__

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminders_on = Column(Boolean, default=True)

    user = relationship("User")


# Функції для роботи з користувачами
def get_user(db, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(db, telegram_id: int, username: str, full_name: str, is_teacher: bool):
    db_user = User(telegram_id=telegram_id, username=username, full_name=full_name, is_teacher=is_teacher)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Функції для роботи з уроками
def create_lesson(db, teacher_id: int, date_time: datetime):
    db_lesson = Lesson(teacher_id=teacher_id, date_time=date_time)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


def get_available_lessons(db, teacher_id: int = None):
    query = db.query(Lesson).filter(Lesson.is_booked == False)
    if teacher_id:
        query = query.filter(Lesson.teacher_id == teacher_id)
    return query.all()


# Функції для роботи з бронюваннями
def create_booking(db, lesson_id: int, student_id: int):
    db_booking = Booking(lesson_id=lesson_id, student_id=student_id)
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson:
        lesson.is_booked = True
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def get_user_bookings(db, user_id: int, is_teacher: bool = False):
    if is_teacher:
        return db.query(Booking).join(Lesson).filter(Lesson.teacher_id == user_id).all()
    return db.query(Booking).filter(Booking.student_id == user_id).all()


# Функції для роботи з налаштуваннями нагадувань
def get_notification_settings(db, user_id: int):
    return db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()


def create_notification_settings(db, user_id: int, reminders_on: bool = True):
    db_settings = NotificationSetting(user_id=user_id, reminders_on=reminders_on)
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


def init_db():
    Base.metadata.create_all(bind=engine)