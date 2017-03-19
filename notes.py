#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)

    def __iter__(self):
        yield 'id', self.id
        yield 'content', self.content


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
    note = Note.query.filter_by(id=note_id).first()
    return jsonify(dict(note))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
