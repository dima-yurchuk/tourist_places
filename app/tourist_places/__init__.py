from flask import Blueprint

place_bp = Blueprint('place_bp_in', __name__,
                     template_folder="templates/tourist_places")


def create_module(app, **kwargs):
    pass


from . import views
