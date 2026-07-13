import json

from flask import Flask, jsonify

app = Flask(__name__)

with open("data.json", "r") as file:
    data = json.load(file)

def recursive_fetching(data, keys):
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, IndexError, TypeError):
        return None

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/hello")
def hello():
    return jsonify(message="Hello, World!")

@app.route("/supersquad")
def squad():
    return jsonify(squadName=data["squadName"])

@app.route("/supername")
def super_name():
    name = recursive_fetching(data, ["members", 0, "name"])
    if name is None:
        return jsonify(error="Member not found"), 404
    return jsonify(name=name)

if __name__ == "__main__":
    app.run(port=3000)
