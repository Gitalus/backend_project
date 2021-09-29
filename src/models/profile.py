from db import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default="")
    avatar = db.Column(db.BLOB)
