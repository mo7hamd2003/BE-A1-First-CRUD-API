from fastapi import FastAPI

app = FastAPI()

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

