from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

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
