#!/usr/bin/env python3

from flask import Flask, request
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    chocolate = db.Column(db.Integer, default=0)

    def __init__(self, content):
        self.content = content
        self.done = False
        self.chocolate = 0

    def __repr__(self):
        return '<Content {0}>'.format(self.content)

    def md(self):
        return '* {0}\n'.format(self.content)

    def dict(self):
        return {'id': self.id,
                'content': self.content,
                'done': self.done,
                'chocolate': self.chocolate}


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


@app.route('/kanban')
def kanban():
    return redirect('/static/kanban.html')


@app.route('/tasks/<int:task_id>', methods=['UPDATE'])
def manage_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return abort(404)

    chocolate = request.form.get('chocolate')
    if chocolate:
        task.chocolate = chocolate

    db.session.commit()

    fmt = request.args.get('format')
    if fmt == 'json':
        return jsonify(task.dict()), 200
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

