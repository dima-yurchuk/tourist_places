from flask import Blueprint
import warnings

user_bp = Blueprint('user_bp_in', __name__, template_folder="templates/user")


def create_module(app, **kwargs):
    pass


from . import views
