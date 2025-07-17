import os
from mailgun.client import Client


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///zimbos_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    # Maximum number of groups a user can checkout in one go
    GROUP_CHECKOUT_LIMIT = int(os.environ.get('GROUP_CHECKOUT_LIMIT', 3))
