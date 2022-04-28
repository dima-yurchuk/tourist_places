from flask import Blueprint
import warnings

from .custom_admin import MyHomeView, UserModelView, RoleModelView, \
    CategoryModelView, RegionModelView, CommentModelView, RatingModelView, \
    TypeModelView, PlaceModelView

user_bp = Blueprint('user_bp_in', __name__, static_folder='static',
                    static_url_path='/static/css/customUser.css',
                    template_folder="templates/user")

def create_module(app, **kwargs):
    from flask_admin import Admin
    from .. import db
    admin = Admin(app, name='RestInUA', index_view=MyHomeView(name='Домашня'))
    from flask_admin.contrib.sqla import ModelView
    from app.user.models import User, Role
    from app.tourist_places.models import Place, Region, Category, Comment, \
        Rating, Type

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'Fields missing from ruleset',
                                UserWarning)
        admin.add_view(UserModelView(User, db.session, name='Користувачі'))
        admin.add_view(RoleModelView(Role, db.session, name='Ролі'))
        admin.add_view(PlaceModelView(Place, db.session, name='Місця'))
        admin.add_view(CategoryModelView(Category, db.session, name='Категорії'))
        admin.add_view(RegionModelView(Region, db.session, name='Області'))
        admin.add_view(CommentModelView(Comment, db.session, name='Коментарі'))
        admin.add_view(RatingModelView(Rating, db.session, name='Оцінки'))
        admin.add_view(TypeModelView(Type, db.session, name='Типи'))

from . import views
