#!/usr/bin/env python3

from flask import Flask, request
from flask import render_template
from flask import redirect
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)

    def __init__(self, content):
        self.content = content
        self.done = False

    def __repr__(self):
        return '<Content {0}>'.format(self.content)

    def md(self):
        return '* {0}\n'.format(self.content)

    def dict(self):
        return {'id': self.id,
                'content': self.content,
                'done': self.done}


db.create_all()


def render_tasks_json(tasks):
    tasks = [t.dict() for t in tasks]
    return jsonify(tasks)


@app.route('/')
def tasks_list():
    fmt = request.args.get('format')
    tasks = Task.query.all()
    if fmt == 'json':
        return render_tasks_json(tasks)
    return render_template('list.html', tasks=tasks)


@app.route('/list')
def task_list_txt():
    rv = "# TODO\n"
    for task in Task.query.all():
        rv += task.md()
    return rv


@app.route('/task', methods=['POST'])
def add_task():
    content = request.form['content']
    if not content:
        return 'Error'

    task = Task(content)
    db.session.add(task)
    db.session.commit()
    return redirect('/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/')

    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@app.route('/done/<int:task_id>')
def resolve_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return redirect('/')
    if task.done:
        task.done = False
    else:
        task.done = True

    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

