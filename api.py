from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

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
def read_stats():
    total = len(tasks)
    done = sum(t["done"] for t in tasks)
    open = total - done
    return { "total": total, "done": done, "open": open }

# Stage-2 & 6: Read list and single task (added query & filter parameters)
@app.get("/tasks")
def read_list(search: str | None = None, done: bool | None = None):
    if search:
        return [t for t in tasks if search.lower() in t["title"].lower()]
    if done is not None:
        return [t for t in tasks if t["done"] == done]
    return tasks

@app.get("/tasks/{task_id}")
def read_item(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"task": task}

# Stage-3: Post a new task
@app.post("/tasks", status_code=201)
async def create_task(task: Task):
    task.id = max((t["id"] for t in tasks), default=0) + 1
    task.done = False
    tasks.append(task.model_dump())
    return {"status_code": 201, "detail": "Created successfully"}

# Stage-4: Update a task
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updates: TaskUpdate):
    existing = next((t for t in tasks if t["id"] == task_id), None)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    updated = {**existing, **updates.model_dump(exclude_unset=True)}
    updated["id"] = task_id
    tasks[tasks.index(existing)] = updated
    return updated

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    existing = next((t for t in tasks if t["id"] == task_id), None)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(existing)
