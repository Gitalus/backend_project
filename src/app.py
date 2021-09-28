import os

from flask_mail import Mail, Message
from flask import Flask, jsonify, request, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from flask_migrate import Migrate
from flask_cors import CORS
from models.user import User
from datetime import timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired


# app config
app = Flask(__name__)
app.url_map.slashes = False
app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY', 'development_only')

# or other relevant config var
uri = os.getenv("DATABASE_URL", "sqlite:///database.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`
app.config['SQLALCHEMY_DATABASE_URI'] = uri

MIGRATE = Migrate(app, db)
jwt = JWTManager(app)
db.init_app(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['JWT_SECRET_KEY'])

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

    return jsonify(access_token=token)


@app.route('/api/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify(message=f"User '{username}' already exists.", status="error"), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(message=f"E-mail '{email}' already in use.", status="error"), 400

    if username is None and password is None and email is None:
        return jsonify(message="You must include a username, a password and an email.", status="error"), 400

    if username == "" and password == "" and email == "":
        return jsonify(message="You must include a username, a password and an email.", status="error"), 400

    user = User(
        username=username,
        password=generate_password_hash(password),
        email=email)

    user.save()
    emailToken = s.dumps(email, salt='email-confirm')
    msg = Message('Confirm Email',
                  sender=app.config['MAIL_USERNAME'], recipients=[email])
    link = url_for('confirm_email', token=emailToken, _external=True)

    msg.body = f'Your link is: {link}'

    mail.send(msg)

    return jsonify(email=email,
                   username=username,
                   status="ok"
                   )


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=120)
    except SignatureExpired:
        return jsonify(message="The token is expired.")
    return jsonify(status="confirmed")


if __name__ == '__main__':
    app.run()
