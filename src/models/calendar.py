from db import db


class Fecha(db.Model):
    __tablename__ = 'fechas'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.BigInteger, unique=False)
    category = db.Column(db.String(100), unique=False)
    profile = db.Column(db.Integer, db.ForeignKey('profiles.id'))
