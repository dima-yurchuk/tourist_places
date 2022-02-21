import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'supersecretkey'
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CRSF_ENAVLED = True
SQLALCHEMY_DATABASE_URI='sqlite:///places.db'
