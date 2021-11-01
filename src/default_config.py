import os

DEBUG = True
uri = os.getenv("DATABASE_URL", "sqlite:///database.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = uri
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
MAIL_SERVER = "smtp.gmail.com"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
ENV = 'development'
