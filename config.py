import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CRSF_ENAVLED = True
PLACE_IN_PAGE = 3

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


# flask-msearch will use table name as elasticsearch index name unless set
# __msearch_index__
MSEARCH_INDEX_NAME = 'msearch'
# simple,whoosh,elaticsearch, default is simple
MSEARCH_BACKEND = 'whoosh'
# auto create or update index
MSEARCH_ENABLE = True
# when backend is elasticsearch
ELASTICSEARCH = {"hosts": ["127.0.0.1:5000"]}