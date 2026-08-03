import os
import sqlite3

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

# DB-Stage-1: Read from database
DB_PATH = os.environ.get("Task_DB_PATH", "task.db")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
    finally:
        con.close()

def task_from_row(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

# DB-Stage-0: Create sqlite database
# Never duplicates, idempotent only
def seed_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )"""
        )
        (count,) = con.execute("SELECT COUNT(*) FROM tasks").fetchone()
        if count == 0:
            con.executemany(
                "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
                [
                    (1, "Buy groceries", 0),
                    (2, "Walk the dog", 1),
                    (3, "Write API docs", 0),
                ],
            )

seed_db()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Write API docs", "done": False},
]

class Task(BaseModel):
    id: int | None = None
    title: str
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title is required")
        return v.strip()

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Title is required")
        return v.strip()

# # Stage-0: Hello, server
# @app.get("/")
# def read_root():
#     return {'Hello' : "Server"}

# Stage-1: first endpoint
@app.get("/")
def read_endpoint():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

# Stage-6: stats
@app.get("/tasks/stats")
def read_stats(con: sqlite3.Connection = Depends(get_db)):
    (total,) = con.execute("SELECT COUNT(*) FROM tasks").fetchone()
    (done,) = con.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()
    open_count = total - done
    return { "total": total, "done": done, "open": open_count }

# Stage-2 & 6: Read list and single task (added query & filter parameters)
@app.get("/tasks")
def read_list(
    search: str | None = None,
    done: bool | None = None,
    con: sqlite3.Connection = Depends(get_db),
):
    if search:
        rows = con.execute(
            "SELECT id, title, done FROM tasks WHERE title LIKE ? ORDER BY id",
            (f"%{search}%",),
        ).fetchall()
    elif done is not None:
        rows = con.execute(
            "SELECT id, title, done FROM tasks WHERE done = ? ORDER BY id",
            (int(done),),
        ).fetchall()
    else:
        rows = con.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [task_from_row(row) for row in rows]

@app.get("/tasks/{task_id}")
def read_item(task_id: int, con: sqlite3.Connection = Depends(get_db)):
    row = con.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"task": task_from_row(row)}

# Stage-3: Post a new task
# async not needed anymore, FasTAPI handles thread pool automatically.
# Changed on post, update, & delete
@app.post("/tasks", status_code=201)
def create_task(task: Task, con: sqlite3.Connection = Depends(get_db)):
    con.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    con.commit()
    return {"status_code": 201, "detail": "Created successfully"}

# Stage-4: Update a task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    updates: TaskUpdate,
    con: sqlite3.Connection = Depends(get_db),
):
    row = con.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    data = updates.model_dump(exclude_unset=True)
    if "title" in data:
        con.execute("UPDATE tasks SET title = ? WHERE id = ?", (data["title"], task_id))
    if "done" in data:
        con.execute("UPDATE tasks SET done = ? WHERE id = ?", (1 if data["done"] else 0, task_id))
    con.commit()
    updated = con.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    return task_from_row(updated)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, con: sqlite3.Connection = Depends(get_db)):
    cur = con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    con.commit()
