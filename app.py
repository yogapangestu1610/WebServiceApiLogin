from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

import jwt
import os
import datetime

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SECRET_KEY'] = "RAHASIA"

class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

class BukuModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100))
    konten = db.Column(db.Text)
    penulis = db.Column(db.String(50))

db.create_all()

def butuh_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('datatoken') 
        if not token:
            return make_response(jsonify({"msg":"TOKEN KOSONG, BUTUH TOKEN UNTUK MELANJUTKAN PROSES"}), 401)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg":"TOKEN INVALID"}), 401)
        return f(*args, **kwargs)
    return decorator

class RegisterUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        if dataUsername and dataPassword:
            dataModel = AuthModel(username=dataUsername, password=dataPassword)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg":"Berhasil"}), 200)
        return jsonify({"msg":"Username/Password tidak boleh KOSONG"})

class LoginUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword:

            token = jwt.encode(
                {
                    "username":queryUsername, 
                    "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=120)
                }, app.config['SECRET_KEY'], algorithm="HS256"
            )
            return make_response(jsonify({"msg":"Login Sukses", "token":token}), 200)
        return jsonify({"msg":"Login Gagal"})


class TambahArtikel(Resource):
    @butuh_token
    def post(self):
        dataJudul = request.form.get('judul')
        dataKonten = request.form.get('konten')
        dataPenulis = request.form.get('penulis')

        data = BukuModel(judul=dataJudul, konten=dataKonten, penulis=dataPenulis)
        db.session.add(data)
        db.session.commit()
        return({"msg":"Artikel Berhasil ditambahkan"}), 200

    @butuh_token
    def get(self):
        dataQuery = BukuModel.query.all()
        output =[
            {
                "id":data.id,
                "judul":data.judul,
                "konten":data.konten,
                "penulis":data.penulis
            }
            for data in dataQuery
        ]
        return make_response(jsonify(output), 200)        

api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(TambahArtikel, "/api/viewbuku", methods=["GET", "POST"])

if __name__ == "__main__":
    app.run(debug=True)

