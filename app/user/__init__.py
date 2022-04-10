from flask import Blueprint
import warnings

user_bp = Blueprint('user_bp_in', __name__, static_folder='static',
                    static_url_path='/static/css/customUser.css',
                    template_folder="templates/user")


from . import views
