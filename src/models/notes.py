from db import db
from datetime import datetime


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), default="")
    contenido = db.Column(db.Text, default="")
    fecha = db.Column(db.Date, default=datetime.now())
    categoria = db.Column(db.String(100))

    perfil_id = db.Column(
        db.Integer, db.ForeignKey('profiles.id'))
    perfil = db.relationship('Profile', backref='notas')

    def serialize(self):
        return {
            "titulo": self.titulo,
            "contenido": self.contenido,
            "fecha": self.fecha,
            "categoria": self.categoria,
            "usuario": self.perfil.nombre,
            "id": self.id
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
