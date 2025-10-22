from fastapi import FastAPI, Depends, HTTPException, Request
from sqlmodel import select
from typing import List
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import engine, init_db, get_session
from models import Todo
from sqlmodel import Session

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    init_db()
    yield
    # 終了時（必要ならクリーンアップを書く）
    # engine.dispose() など
    
app = FastAPI(title="Simple Todo with FastAPI + SQLModel", lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Session = Depends(get_session)):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todos/", response_model=List[Todo])
def read_todos(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo).order_by(Todo.id.desc())).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: Todo, session: Session = Depends(get_session)):
    db = session.get(Todo, todo_id)
    if not db:
        raise HTTPException(status_code=404, detail="Not found")
    db.title = payload.title
    db.done = payload.done
    session.add(db)
    session.commit()
    session.refresh(db)
    return db

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    db = session.get(Todo, todo_id)
    if not db:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(db)
    session.commit()
    return None
