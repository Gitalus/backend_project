import os

from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from flask_cors import CORS
from models.user import User
from datetime import timedelta

# app config
app = Flask(__name__)
app.url_map.slashes = False
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY', 'development_only')

uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`
app.config['SQLALCHEMY_DATABASE_URI'] = uri

jwt = JWTManager(app)
db.init_app(app)

CORS(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def get_home():
    return "<h1>Serenity REST API</h1>"


@app.route('/api/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password, password):

        return jsonify(message="Bad username or password."), 400

    token = create_access_token(
        identity=user.username,
        expires_delta=timedelta(hours=5)
    )

    return jsonify(acces_token=token)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username', None)
    password = data.get('password', None)
    email = data.get('email', None)

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify(message=f"User '{username}' already exists."), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(message=f"E-mail '{email}' already in use."), 400

    if username is None and password is None and email is None:
        return jsonify(message="You must include a username, a password and an email."), 400

    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email)

    user.save()
    return jsonify(message=f"username '{username}' created.")


if __name__ == '__main__':
    app.run()
