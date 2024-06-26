from pydantic import BaseModel

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    thread_id: int

class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True

class ThreadBase(BaseModel):
    pass

class ThreadCreate(ThreadBase):
    pass

class Thread(ThreadBase):
    id: int
    messages: list[Message] = []

    class Config:
        orm_mode = True
