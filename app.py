from flask import Flask,render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    time_worked = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String())
    tasks = db.relationship('Task', backref='subject')
    def __repr__(self):
        return '<Subject %r>' % self.id

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name_task = db.Column(db.String(), nullable = False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods = ['GET', 'POST'])

def index():
    if request.method == "POST":
        subject_content = request.form["content"]
        subject_color = request.form["color"]
        new_subject = Subject(name = subject_content, color=subject_color)
        try:
           db.session.add(new_subject)
           db.session.commit()
           return redirect('/')
        except:
            return("Error Creating Subject")
    else:
        subjects = Subject.query.all()
        return render_template("index.html", subjects = subjects)

@app.route('/delete_subject/<int:id>')
def delete_subject(id):
    subject_to_delete = Subject.query.get_or_404(id)

    try:
        db.session.delete(subject_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update_subject/<int:id>', methods=["GET", "POST"])
def update_subject(id):
    subject = Subject.query.get_or_404(id)
    if request.method == "POST":
        subject.name = request.form["content"]
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update_subject.html', subject=subject)

@app.route('/add_task/<int:id>',methods = ['GET', 'POST'])
def subject_page(id):
    if request.method == "POST":
        subject = Subject.query.get_or_404(id)
        task_content = request.form["content"]
        new_task = Task(name_task = task_content, subject = subject)
        try:
           db.session.add(new_task)
           db.session.commit()
           return redirect('/add_task/'+str(id))
        except:
            return("Error Creating Task on Subject")
    else:
        tasks = Task.query.where(Task.subject_id == id).all()
        return render_template("subject.html", tasks=tasks, s_id = id)

@app.route("/complete/<int:s_id>/<int:t_id>", methods=["GET", "POST"])
def complete(s_id,t_id):
    task = Task.query.get_or_404(t_id)
    if request.method == "POST":
        task.end_time = datetime.utcnow()
        try:
            db.session.commit()
            return redirect('/add_task/'+str(s_id))
        except:
            return 'There was an issue deleting your task'
    else:
        return redirect("/add_task/"+str(s_id))

@app.route("/delete/<int:s_id>/<int:t_id>", methods=["GET", "POST"])
def delete(s_id, t_id):
    task_to_delete = Task.query.get_or_404(t_id)
    if request.method == "POST":
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect('/add_task/'+str(s_id))
        except:
            return 'There was an issue completing your task'
    else:
        return redirect("/add_task/"+str(s_id))

if __name__ == "__main__":
    app.run(debug=True)