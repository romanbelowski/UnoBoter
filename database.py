from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)
    is_teacher = Column(Boolean, default=False)
    full_name = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_user(db, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db, telegram_id: int, username: str, full_name: str, is_teacher: bool):
    db_user = User(telegram_id=telegram_id, username=username, full_name=full_name, is_teacher=is_teacher)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
