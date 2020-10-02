#!/usr/bin/env python3
import os
from sys import argv

from flask import Flask, request
from flask import render_template
from flask import redirect
from flask import jsonify
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
password = None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


@auth.verify_password
def verify_password(uname, pword):
    if password:
        if password == pword:
            return True
        else:
            return False
    else:
        return True


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    chocolate = db.Column(db.Integer, default=0)
    board = db.Column(db.Text, default='default')

    def __init__(self, content):
        self.content = content
        self.done = False
        self.chocolate = 0
        self.board = 'default'

    def __repr__(self):
        return '<Content {0}>'.format(self.content)

    def md(self):
        return '* {0}\n'.format(self.content)

    def dict(self):
        return {'id': self.id,
                'content': self.content,
                'done': self.done,
                'chocolate': self.chocolate,
                'board': self.board}


db.create_all()


def render_tasks_json(tasks):
    tasks = [t.dict() for t in tasks]
    return jsonify(tasks)


@app.route('/')
@auth.login_required
def tasks_list():
    fmt = request.args.get('format')
    tasks = Task.query.all()
    if fmt == 'json':
        return render_tasks_json(tasks)
    return render_template('list.html', tasks=tasks)


@app.route('/list')
@auth.login_required
def task_list_txt():
    rv = "# TODO\n"
    for task in Task.query.all():
        rv += task.md()
    return rv


@app.route('/task', methods=['POST'])
@auth.login_required
def add_task():
    content = request.form['content']
    if not content:
        return 'Error'
    board = request.form['board']
    if not board:
        board = 'default'

    task = Task(content)
    task.board = board
    db.session.add(task)
    db.session.commit()
    return redirect('/')


@app.route('/delete/<int:task_id>')
@auth.login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect('/')

    db.session.delete(task)
    db.session.commit()
    return redirect('/')


@app.route('/done/<int:task_id>')
@auth.login_required
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
@auth.login_required
def kanban():
    return redirect('/static/kanban.html')


@app.route('/tasks/<int:task_id>', methods=['UPDATE'])
@auth.login_required
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
    if len(argv) > 1:
        password = argv[1]
    ssl_cert = "fullchain.pem"
    ssl_key = "privkey.pem"

    if os.path.isfile(ssl_cert) and os.path.isfile(ssl_key):
        from cheroot.wsgi import Server as WSGIServer
        from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
        from cheroot.ssl.builtin import BuiltinSSLAdapter

        my_app = WSGIPathInfoDispatcher({'/': app})
        server = WSGIServer(('0.0.0.0', 5000), my_app)

        server.ssl_adapter =  BuiltinSSLAdapter(ssl_cert, ssl_key, None)

        try:
           server.start()
        except KeyboardInterrupt:
           server.stop()
    else:
        app.run(host='0.0.0.0')
