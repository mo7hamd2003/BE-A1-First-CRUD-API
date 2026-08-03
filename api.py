from fastapi import FastAPI

app = FastAPI()

# Stage-0: Hello, server
@app.get("/")
def read_root():
    return {'Hello' : "World"}



