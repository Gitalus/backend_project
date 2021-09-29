from db import db
from datetime import date


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), default="")
    contenido = db.Column(db.Text, default="")
    fecha = db.Column(db.Date, default=date.today())
    categoria = db.Column(db.String(100))

    profile_id = db.Column(
        db.Integer, db.ForeignKey('profiles.id'))
    profile = db.relationship('Profile', backref='notes')

    def serialize(self):
        return {
            "title": self.titulo,
            "contenido": self.contenido,
            "fecha": self.fecha,
            "categoria": self.categoria,
            "usuario": self.profile.name
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
