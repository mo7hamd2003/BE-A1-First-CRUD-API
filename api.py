from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Write API docs", "done": False},
]

class Task(BaseModel):
    id: int
    title: str
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
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

# Stage-2: Read list and single task
@app.get("/tasks")
def read_list():
    return tasks

@app.get("/tasks/{task_id}")
def read_item(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"task": task}

# Stage-3: Post a new task
@app.post("/tasks")
async def create_task(task: Task):
    task.id = max((t["id"] for t in tasks), default=0) + 1
    task.done = False
    tasks.append(task.model_dump())
    return {"status_code": 201, "detail": "Created successfully"}
