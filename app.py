from flask import Flask, request,render_template,redirect

app = Flask(__name__)

tasks=[]
@app.route('/')
def home():
    enumerated_tasks = list(enumerate(tasks))
    return render_template('index.html',tasks=enumerated_tasks)

@app.route('/add',methods=["POST"])
def add_task():
        item = request.form.get('task')
        due_date = request.form.get('due_date')
        if item and due_date:
            task = {"item": item, "completed": False, "due_date": due_date}
            tasks.append(task)
        return redirect('/')
    
@app.route('/delete/<int:task_id>',methods=["GET","POST"])
def delete_task(task_id):
        if task_id < len(tasks):
            tasks.pop(task_id)
        return redirect('/')  
    
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    if task_id < len(tasks):
        tasks[task_id]['completed'] = True
    return redirect('/')

@app.route('/clear')
def clear_tasks():
    tasks.clear()
    return redirect('/')      

if __name__ == '__main__':
    app.run(debug=True)