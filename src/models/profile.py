from db import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), default="")
    # avatar = db.Column(db.BLOB)

    def serialize(self):
        return {
            "nombre": self.nombre,
            "notas": [nota.serialize() for nota in self.notas]
        }
