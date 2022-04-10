from flask import Blueprint

place_bp = Blueprint('place_bp_in', __name__,
                     static_folder='static',
                     static_url_path='/static/css/customTouristPlaces.css',
                     template_folder="templates/tourist_places")

from . import views
