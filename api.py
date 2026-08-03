from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Write API docs", "done": False},
]

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
