# 6C/19090034/Mohammad Prayoga Pangestu
# 6C/19090092/Hendra Estu Prasetyo

import os, random, string

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify

import json 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import QueryableAttribute

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "user.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    token = db.Column(db.String(225), unique=True, nullable=True, primary_key=False)
db.create_all()

def __repr__(self):
        return '<User %r>' % self.username

@app.route('/tambah_user', methods=['POST'])
def add_user():
    print('Enter your username:')
    username = input()
    print('Enter your password:')
    password = input()

    data = User(username=username, password=password)
    db.session.add(data)
    db.session.commit()

    return 'User baru berhasil ditambahkan'

@app.route('/api/v1/login', methods=['POST'])
def auth():
    username = request.values.get('username')
    password = request.values.get('password')
    account = User.query.filter_by(username=username, password=password).first()
    
    if account:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        User.query.filter_by(username=username, password=password).update({'token': token})
        db.session.commit()
        data = {"msg": "Login berhasil!!", "token": token}
        return jsonify(data)
    else:
        data = {'msg': 'Login gagal!!'}
        return jsonify(data)


@app.route('/api/v2/users/info', methods=['POST'])
def users_info():
    token = request.values.get('token')
    account = User.query.filter_by(token=token).first()
    if account:
        return account.username
    else:
        return 'Token anda salah'


if __name__ == '__main__':
    app.run(debug=True, port=5000)