from sqlalchemy.orm import Session
from . import models, schemas

def get_threads(db: Session):
    return db.query(models.Thread).all()

def get_thread(db: Session, thread_id: int):
    return db.query(models.Thread).filter(models.Thread.id == thread_id).first()

def create_thread(db: Session):
    db_thread = models.Thread()
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread

def create_message(db: Session, thread_id: int, role: str, content: str):
    db_message = models.Message(thread_id=thread_id, role=role, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
def get_messages_by_thread(db: Session, thread_id: int):
    return db.query(models.Message).filter(models.Message.thread_id == thread_id).all()


def get_thread(db: Session, thread_id: int):
    return db.query(models.Thread).filter(models.Thread.id == thread_id).first()
def delete_thread(db: Session, thread_id: int):
    db_thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    if db_thread:
        db.delete(db_thread)
        db.commit()
