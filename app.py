from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, date
from collections import defaultdict

from flask import Flask, request, redirect, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from ldap import init_ldap

app = Flask(__name__)
app.secret_key = "secret-key"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')

#app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///tasks.db'

db =SQLAlchemy(app)

class Task(db.Model):
    __tablename__ ="tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, default=date.today)
    completed = db.Column(db.Boolean,default=False)
    category = db.Column(db.String(50), nullable=True)
     
@app.route('/')
def home():
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
        category = task.category if task.category else "Uncategorized"
        categorized_tasks[category].append(task)

    today = date.today().strftime("%Y-%m-%d")

    return render_template(
        'index.html',
        tasks=tasks,
        categorized_tasks=categorized_tasks,
        current_today=today,
        current_filter=filter_type
    )

def add_task():
    task = request.form.get('task')
    due_date = request.form.get('due_date')
    category = request.form.get('category')
    due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    new_task = Task(title=task, due_date=due_date, category=category)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

@app.route('/delete_task/<int:task_id>', methods=['POST', 'GET'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@app.route('/complete_task/<int:task_id>', methods=['GET','POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect('/')

@app.route('/clear/')
def clear_task():
    Task.query.delete()
    db.session.commit()
    return redirect('/')
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)    
