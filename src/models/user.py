from uuid import uuid4
from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Text, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    confirmed_email = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex

    def __repr__(self) -> str:
        return f'Username: {self.username},\nemail: {self.email}'

    perfil_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id'), unique=True)
    perfil = db.relationship('Profile', backref='usuario', uselist=False)

    def serialize(self):
        return {
            "nombre_usuario": self.nombre_usuario,
            "email": self.email,
            "perfil": self.perfil.serialize()
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
