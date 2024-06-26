import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import openai
from . import models, schemas, crud
from .db import SessionLocal, engine

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Initialize the database
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="chatbot/templates")

# Mount the static files directory
app.mount("/static", StaticFiles(directory="chatbot/static"), name="static")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request, db: Session = Depends(get_db)):
    threads = crud.get_threads(db)
    return templates.TemplateResponse("chat.html", {"request": request, "threads": threads})


@app.post("/send_message", response_class=HTMLResponse)
async def send_message(
        request: Request,
        message: str = Form(...),
        thread_id: int = Form(...),
        db: Session = Depends(get_db)
):
    # Save user message
    crud.create_message(db, thread_id=thread_id, role="user", content=message)

    # Generate assistant response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
    )
    answer = response.choices[0].message["content"].strip()

    # Save assistant response
    crud.create_message(db, thread_id=thread_id, role="assistant", content=answer)

    threads = crud.get_threads(db)
    selected_thread = crud.get_thread(db, thread_id)
    return templates.TemplateResponse("chat.html",
                                      {"request": request, "threads": threads, "selected_thread": selected_thread})


@app.post("/new_thread", response_class=HTMLResponse)
async def new_thread(request: Request, db: Session = Depends(get_db)):
    crud.create_thread(db)
    return templates.TemplateResponse("chat.html", {"request": request, "threads": crud.get_threads(db)})


@app.get("/load_thread", response_class=HTMLResponse)
async def load_thread(request: Request, thread_id: int, db: Session = Depends(get_db)):
    threads = crud.get_threads(db)
    selected_thread = crud.get_thread(db, thread_id)
    return templates.TemplateResponse("chat.html",
                                      {"request": request, "threads": threads, "selected_thread": selected_thread})


@app.post("/delete_thread", response_class=HTMLResponse)
async def delete_thread(request: Request, thread_id: int, db: Session = Depends(get_db)):
    crud.delete_thread(db, thread_id)
    threads = crud.get_threads(db)
    selected_thread = threads[-1] if threads else None
    return templates.TemplateResponse("chat.html",
                                      {"request": request, "threads": threads, "selected_thread": selected_thread})
