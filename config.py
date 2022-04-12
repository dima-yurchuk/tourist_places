import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'supersecretkey'
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CRSF_ENAVLED = True
SQLALCHEMY_DATABASE_URI='sqlite:///places.db'
PLACE_IN_PAGE = 3

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = '*****'
MAIL_PASSWORD = '*****'
