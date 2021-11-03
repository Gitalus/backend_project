from flask import Flask, jsonify, request, url_for, render_template, make_response, redirect
from db import db
from flask_cors import CORS
from flask_migrate import Migrate
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash

from models.notes import Note
from models.calendar import Fecha
from models.profile import Profile
from models.user import User
from datetime import timedelta


load_dotenv('.env', verbose=True)
# app config
app = Flask(__name__)
app.url_map.slashes = False
app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')


MIGRATE = Migrate(app, db)
jwt = JWTManager(app)
db.init_app(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['JWT_SECRET_KEY'])

CORS(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def get_home():
    return "<h1>Serenity REST API</h1>"


@app.route('/api/auth', methods=['POST'])
def login():
    nombre_usuario = request.json.get('nombre_usuario', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(nombre_usuario=nombre_usuario).first()

    if user and check_password_hash(user.password, password):
        if user.confirmed_email:
            token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(weeks=1)
            )
            return jsonify(access_token=token)
        else:
            return jsonify(message='email not verified, please check your mail inbox to validate it'), 403

    else:
        return jsonify(message="Bad username or password."), 400


@app.route('/api/register', methods=['POST'])
def register():
    nombre_usuario = request.json.get('nombre_usuario', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)
    user_img = request.json.get('user_img', "")

    user = User.query.filter_by(nombre_usuario=nombre_usuario).first()

    if user:
        return jsonify(message=f"El usuario '{nombre_usuario}' ya existe.", status="error"), 400

    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify(message=f"E-mail '{email}' ya está en uso.", status="error"), 400

    if nombre_usuario is None or password is None or email is None:
        return jsonify(message="Debes incluir un nombre de usuario, email y contraeña.", status="error"), 400

    if nombre_usuario == "" or password == "" or email == "":
        return jsonify(message="Debes incluir un nombre de usuario, email y contraeña.", status="error"), 400

    newProfile = Profile()
    newProfile.avatar = user_img
    user = User(
        nombre_usuario=nombre_usuario,
        password=generate_password_hash(password),
        email=email,
        perfil=newProfile)

    user.save()
    emailToken = serializer.dumps(user.id, salt=app.config['JWT_SECRET_KEY'])
    msg = Message(
        'Confirm Email',
        sender=app.config['MAIL_USERNAME'], recipients=[email])
    link = url_for('confirm_email', token=emailToken, _external=True)

    msg.body = f'Confirm email account link: {link}'

    mail.send(msg)

    return jsonify(
        user=user.serialize(),
        status="ok"
    )


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        user_id = serializer.loads(
            token, salt=app.config['JWT_SECRET_KEY'], max_age=300)
    except SignatureExpired:
        return jsonify(message="The token is expired.")

    user = User.query.get(user_id)
    if user:
        user.confirmed_email = True
        user.save()
        # headers = {
        #     "Content-Type": "text/html"
        # }
        return redirect(f"http://localhost:3000/confirm-email/{user.email}", code=302)
        # return make_response(render_template("confirm_page.html", email=user.email), 200, headers)
    else:
        return jsonify(message="User not found"), 400


# @app.route('/api/test')
# @jwt_required()
# def test():
#     user_id = get_jwt_identity()
#     user = User.query.get(user_id)
#     if user.confirmed_email:
#         return jsonify(user.serialize())
#     else:
#         return jsonify(message='Usuario sin confimar email')


if __name__ == '__main__':
    app.run()
