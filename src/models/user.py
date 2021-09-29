from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id'), unique=True)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def serialize(self):
        return {
            "username": self.username,
            "email": self.email,
            "profile_name": self.profile.name
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
