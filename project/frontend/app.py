from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://backend-auth:8000")
TASKS_SERVICE_URL = os.getenv("TASKS_SERVICE_URL", "http://backend-tasks:8001")

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        data = {"username": username, "password": password}
        try:
            response = requests.post(f"{AUTH_SERVICE_URL}/login", json=data)
            if response.status_code == 200:
                session['user'] = username
                return redirect(url_for('tasks'))
            else:
                flash("Invalid credentials", "error")
        except Exception as e:
            flash("Authentication service unreachable", "error")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Add a new task
        title = request.form.get("title")
        description = request.form.get("description")
        data = {"title": title, "description": description}
        try:
            response = requests.post(f"{TASKS_SERVICE_URL}/tasks", json=data)
            if response.status_code != 200:
                flash("Failed to add task", "error")
        except Exception as e:
            flash("Tasks service unreachable", "error")
        return redirect(url_for('tasks'))
    
    # Fetch tasks
    try:
        response = requests.get(f"{TASKS_SERVICE_URL}/tasks")
        tasks_list = response.json() if response.status_code == 200 else []
    except Exception as e:
        tasks_list = []
        flash("Tasks service unreachable", "error")
    return render_template("tasks.html", tasks=tasks_list, user=session.get('user'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        response = requests.delete(f"{TASKS_SERVICE_URL}/tasks/{task_id}")
        if response.status_code != 200:
            flash("Failed to delete task", "error")
    except Exception as e:
        flash("Tasks service unreachable", "error")
    return redirect(url_for('tasks'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
