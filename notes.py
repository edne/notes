#!/usr/bin/env python3
from flask import Flask, request, jsonify, abort, g
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __iter__(self):
        yield 'id', self.id
        yield 'content', self.content


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __iter__(self):
        yield 'id', self.id
        yield 'username', self.username


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@app.route('/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).one_or_none()
    if user:
        return jsonify(dict(user))
    else:
        abort(404)


@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']

    if User.query.filter_by(username=username).one_or_none():
        app.logger.info('Username {} already taken'.format(username))
        abort(400)

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(dict(user))


@app.route('/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/add', methods=['POST'])
def add_note():
    content = request.form['content']
    note = Note(content=content)

    db.session.add(note)
    db.session.commit()

    app.logger.info('Added note: ' + str(note))
    return jsonify(dict(note))


@app.route('/note/<int:note_id>')
def show_note(note_id):
    note = Note.query.filter_by(id=note_id).one_or_none()
    if note:
        return jsonify(dict(note))
    else:
        abort(404)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
