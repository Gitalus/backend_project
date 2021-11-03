from db import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), default="")
    avatar = db.Column(db.Text, default="")

    calendario = db.relationship('Fecha', cascade="all, delete-orphan")

    def serialize(self):
        return {
            "nombre": self.nombre,
            "notas": [nota.serialize() for nota in self.notas],
            "user_img": self.avatar,
            "calendario": {fecha.fecha: fecha.category for fecha in self.calendario}
        }
