from db import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.BLOB)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), unique=True, nullable=False)
    user = db.relationship('User', backref='profile', lazy='dynamic')
