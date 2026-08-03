# Task API

A simple REST API for managing a to-do list, built with **FastAPI** and **Pydantic**.

- Tasks live in an in-memory list, so they reset every time the server restarts
- Full CRUD: create, read, update, and delete tasks
- Filter tasks by search text and completion status
- Interactive API docs (Swagger UI) served automatically at `/docs`

## Requirements

- Python 3.10+ (the code uses `bool | None` unions and Pydantic v2's `field_validator`)

## Install & Run

One command — creates a virtual environment, installs the dependencies, and starts the server:

```bash
python -m venv .venv && .venv/Scripts/pip install fastapi uvicorn && .venv/Scripts/python -m uvicorn api:app --reload
```

> On macOS/Linux, use `.venv/bin/pip` and `.venv/bin/python` instead of `.venv/Scripts/...`.

The server starts on `http://localhost:8000`. Open `http://localhost:8000/docs` for the Swagger UI, which lets you try every endpoint from the browser.

## Endpoints

| Method | Endpoint           | Description                             | Response                                                                  |
| ------ | ------------------ | --------------------------------------- | ------------------------------------------------------------------------- |
| GET    | `/`                | API info (name, version, endpoints)     | `200` — `{"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}` |
| GET    | `/health`          | Health check                            | `200` — `{"status": "ok"}`                                                |
| GET    | `/tasks`           | List all tasks (supports query filters) | `200` — JSON array of tasks                                               |
| GET    | `/tasks/stats`     | Task statistics                         | `200` — `{"total": 3, "done": 1, "open": 2}`                              |
| GET    | `/tasks/{task_id}` | Get a single task by id                 | `200` — `{"task": {...}}`, `404` if not found                             |
| POST   | `/tasks`           | Create a task (`{"title": "..."}`)      | `201` — created confirmation, `422` if the title is empty                 |
| PUT    | `/tasks/{task_id}` | Update a task's `title` and/or `done`   | `200` — updated task, `404` if not found, `422` if the title is empty     |
| DELETE | `/tasks/{task_id}` | Delete a task                           | `204` — no body (task removed), `404` if not found                        |

## Example Request

```bash
curl -i http://localhost:8000/tasks
```

```http
HTTP/1.1 200 OK
date: Sun, 03 Aug 2026 10:15:32 GMT
server: uvicorn
content-length: 137
content-type: application/json

[{"id":1,"title":"Buy groceries","done":false},{"id":2,"title":"Walk the dog","done":true},{"id":3,"title":"Write API docs","done":false}]
```

## Swagger UI

![Swagger UI](https://github.con/mo7hamd2003/BE-A1-First-CRUD-API/FastAPI - Swagger UI.png)

## Query & Filter Options

`GET /tasks` accepts two optional query parameters:

| Parameter | Type           | Effect                                                  |
| --------- | -------------- | ------------------------------------------------------- |
| `search`  | string         | Case-insensitive substring match against the task title |
| `done`    | `true`/`false` | Exact match on the task's completion status             |

Examples:

```bash
curl -i "http://localhost:8000/tasks?search=groceries"
curl -i "http://localhost:8000/tasks?done=true"
curl -i "http://localhost:8000/tasks?search=walk&done=false"
```

### What happens and why

- **No parameters** — the full task list is returned.
- **`search` only** — tasks whose title contains the search text (case-insensitive) are returned.
- **`done` only** — tasks are filtered by an exact match on `done`.
- **Both `search` and `done`** — only the `search` filter applies. The handler checks `search` first and returns its result before the `done` filter is reached, so the two filters cannot be combined yet. This is a limitation of the current implementation order, not an error: if you send both, expect search results only.
