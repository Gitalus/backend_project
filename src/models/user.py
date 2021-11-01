import uuid
from db import db
from uuid import uuid4


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    confirmed_email = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex

    def __repr__(self) -> str:
        return f'Username: {self.username},\nemail: {self.email}'

    def serialize(self):
        return {
            "username": self.username,
            "email": self.email
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
