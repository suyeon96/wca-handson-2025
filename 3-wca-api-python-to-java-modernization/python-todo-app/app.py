from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__, template_folder="templates")

# Load tasks from a JSON file
def load_tasks():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as file:
            return json.load(file)
    return []

# Save tasks to JSON file
def save_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)

# Route to serve the frontend HTML page
@app.route("/")
def home():
    return render_template("index.html")

# API to get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

# API to add a task
@app.route("/tasks", methods=["POST"])
def add_task():
    tasks = load_tasks()
    new_task = request.json
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify({"message": "Task added successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)
