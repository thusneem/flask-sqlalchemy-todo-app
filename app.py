from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, date
from collections import defaultdict

from flask import Flask, request, redirect, render_template, session
import json

import boto3
from werkzeug.utils import secure_filename


app = Flask(__name__)

S3_BUCKET = "to-do-file-upload-jan-2026"
S3_REGION = "us-east-1"

s3 = boto3.client("s3", region_name=S3_REGION)

app.secret_key = "secret-key"
basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')



def my_secrets(secrect_name,region):
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secrect_name)
    return json.loads(response["SecretString"])


secret = my_secrets( secrect_name="prod/rds/todo",region="us-east-1")



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{secret['username']}:{secret['password']}@{secret['host']}/{secret['dbname']}"

db =SQLAlchemy(app)

class Task(db.Model):
    __tablename__ ="tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, default=date.today)
    completed = db.Column(db.Boolean,default=False)
    category = db.Column(db.String(50), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)

#Home Route   
@app.route('/')
def home():
    if "user" not in session:
        return redirect("/login") 
    
    filter_type = request.args.get("filter", "all")

    query = Task.query

    if filter_type == "active":
        query = query.filter_by(completed=False)
    elif filter_type == "completed":
        query = query.filter_by(completed=True)

    # Apply ordering and fetch tasks
    tasks = query.order_by(Task.due_date).all()

    categorized_tasks = defaultdict(list)
    for task in tasks:
        category = task.category if task.category else "Files"
        categorized_tasks[category].append(task)

    today = date.today().strftime("%Y-%m-%d")

    return render_template(
        'index.html',
        tasks=tasks,
        categorized_tasks=categorized_tasks,
        current_today=today,
        current_filter=filter_type
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["user"] = username  
            return redirect("/")

        return render_template("login.html", error="Invalid credentials")

    # GET request → show login page
    return render_template("login.html")

# Add Task Route
@app.route('/add',methods=["POST"])
def add_task():
    task = request.form.get('task')
    due_date = request.form.get('due_date')
    category = request.form.get('category')
    due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    new_task = Task(title=task, due_date=due_date, category=category)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')
# Delete Task Route
@app.route('/delete_task/<int:task_id>', methods=['POST', 'GET'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

# Mark Task Completed Task Route
@app.route('/complete_task/<int:task_id>', methods=['GET','POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect('/')

# Clear Task Route
@app.route('/clear/')
def clear_task():
    Task.query.delete()
    db.session.commit()
    return redirect('/')

# Upload File Task Route
@app.route("/upload_task", methods=["POST"])
def upload_task():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    category = request.form.get("category")
    due_date = request.form.get("due_date")

    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)

    try:
        # Upload to S3
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

        # Create NEW task
        new_task = Task(
            title=filename,          # file name as task title
            category=category,
            due_date=date.today(),
            completed=False,
            file_name=file_url
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect("/")

    except Exception as e:
        return str(e), 500
    
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  
    return redirect("/login")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0",port=5000,debug=True)    
