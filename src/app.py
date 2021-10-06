import os

# from flask_mail import Mail, Message
from flask import Flask, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from flask_migrate import Migrate
from flask_cors import CORS
from models.notes import Note
from models.calendar import Fecha
from models.profile import Profile
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

# or other relevant config var
uri = os.getenv("DATABASE_URL", "sqlite:///database.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`
app.config['SQLALCHEMY_DATABASE_URI'] = uri

jwt = JWTManager(app)
db.init_app(app)
MIGRATE = Migrate(app, db)

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

    if user is None or not check_password_hash(user.password, password):

        return jsonify(message="Mal nombre de usuario o contraseña."), 400

    token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(weeks=1)
    )

    return jsonify(access_token=token)


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

    if nombre_usuario is None and password is None and email is None:
        return jsonify(message="Debes incluir un nombre de usuario, email y contraeña.", status="error"), 400

    if nombre_usuario == "" and password == "" and email == "":
        return jsonify(message="Debes incluir un nombre de usuario, email y contraeña.", status="error"), 400

    newProfile = Profile()
    newProfile.avatar = user_img
    user = User(
        nombre_usuario=nombre_usuario,
        password=generate_password_hash(password),
        email=email,
        perfil=newProfile)

    user.save()

    return jsonify(email=email,
                   nombre_usuario=nombre_usuario,
                   status="ok"
                   )


@app.route('/api/users')
def get_users():
    return jsonify(users=[user.serialize() for user in User.query.all()])


@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    nombre = request.json.get('nombre')
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    user.perfil.nombre = nombre
    user.save()

    return jsonify(user.serialize())


@app.route('/api/profile')
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify(user.serialize())


@app.route('/api/note', methods=['POST'])
@jwt_required()
def create_note():
    nota = Note()
    nota.titulo = request.json.get('titulo')
    nota.contenido = request.json.get('contenido')
    nota.categoria = request.json.get('categoria')

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    nota.perfil = user.perfil
    nota.save()

    return jsonify(nota.serialize())


@app.route('/api/calendar', methods=['POST'])
@jwt_required()
def save_calendar():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    user.perfil.calendario = []
    for fecha, category in request.get_json().items():
        newFecha = Fecha(fecha=fecha, category=category)
        user.perfil.calendario.append(newFecha)
    user.save()

    return jsonify(message="added_calendar")


@app.route('/api/tokencheck', methods=['POST'])
@jwt_required()
def check_token():
    user_id = get_jwt_identity()
    token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(weeks=1)
    )
    return jsonify(access_token=token)


@app.route('/api/note/<int:_id>', methods=['DELETE'])
@jwt_required()
def delete_note(_id):
    note = Note.query.get(_id)
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    user.perfil.notas.remove(note)
    user.save()

    return jsonify(user.serialize())


if __name__ == '__main__':
    app.run()
