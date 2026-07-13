# Simple Server API Flow

A simple Flask REST API that serves superhero squad data.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install flask

# Run the server
python api.py
```

The server starts on `http://localhost:3000`.

## Endpoints

| Method | Endpoint      | Description                        | Response                                      |
|--------|---------------|------------------------------------|-----------------------------------------------|
| GET    | `/health`     | Health check                       | `{"status": "ok"}`                            |
| GET    | `/hello`      | Returns a greeting                 | `{"message": "Hello, World!"}`                |
| GET    | `/supersquad` | Returns the squad name             | `{"squadName": "Super hero squad"}`           |
| GET    | `/supername`  | Returns the first member's name    | `{"name": "Molecule Man"}`                    |

## Testing

Run the test script to verify all endpoints:

```bash
python test_endpoints.py
```
