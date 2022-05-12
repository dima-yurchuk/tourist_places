from flask import flash, redirect, url_for
from flask_admin import BaseView, expose, AdminIndexView
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView

from .forms import check_letters, check_digits, check_symbols, check_spaces
from wtforms.validators import Length, DataRequired, Regexp, Email, \
    ValidationError

from .models import Role, User
from .. import db
from ..tourist_places.form import check_text_length
from ..tourist_places.models import Place, Category, Comment, Rating, Type


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.is_admin()):
            flash('Немає доступу до цієї сторінки',
                  'danger')
            return redirect(url_for('user_bp_in.login'))
        return self.render('admin/admin_home.html')


class UserModelView(ModelView):
    column_searchable_list = ('username',)
    column_sortable_list = ('username',)
    column_list = ('username', 'email', 'picture', 'user_br.name')
    column_labels = {
        'username': "Ім'я користувача",
        'picture': 'Фото',
        'user_br.name': 'Роль користувача'
    }
    form_edit_rules = (
        'username', 'email', 'picture', 'user_br', 'activated'
    )
    form_create_rules = (
        'username', 'email', 'password', 'user_br', 'activated'
    )
    form_create_rules_labels = {
        'user_br': 'email'
    }
    form_args = dict(
        username=dict(validators=[Length(min=3, max=30,
                                         message='Поле повинно бути довжиною '
                                                 'від 3 до 30 симолів!'),
                                  DataRequired(message='Заповніть це поле!'),
                                  Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                         "Ім'я повинно містити тільки"
                                         " англійські літери, "
                                         "цифри, крапку або нижнє "
                                         "підкреслення!")
                                  ]),
        email=dict(validators=[DataRequired(message='Заповніть це поле!'),
                               Email(message='Некоректна email адреса!')]),
        password=dict(label='Пароль',
                      validators=[Length(min=8, max=30,
                                         message='Пароль повинен бути довжиною '
                                                 'від 8 до 30 '
                                                 'симолів!'),
                                  DataRequired(message='Заповніть це поле!'),
                                  check_letters, check_digits,
                                  check_symbols, check_spaces]),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            posts = Place.query.filter_by(user_id=model.id)
            comments = Comment.query.filter_by(user_id=model.id)
            ratings = Rating.query.filter_by(user_id=model.id)
            types = Type.query.filter_by(user_id=model.id)
            users = User.query.filter_by(role_id=1)
            if posts.first():
                flash('Ви не можете видалити цього користувача, оскільки він '
                      'є автором постів', 'danger')
                False
            elif users.total < 2:
                flash('Не можливо видалити останнього адміністратора сайту!', 'danger')
                False
            else:
                if comments.first() or ratings.first() or types.first():
                    for comment in comments:
                        db.session.delete(comment)
                    for rating in ratings:
                        db.session.delete(rating)
                    for type in types:
                        db.session.delete(type)
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class RoleModelView(ModelView):
    column_searchable_list = ('name',)
    column_sortable_list = ('name',)
    column_list = ('name',)
    column_labels = {
        'name': "Роль"
    }
    form_edit_rules = (
        'name',
    )
    form_create_rules = (
        'name',
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            user = User.query.filter_by(role_id=model.id)
            if user.first():
                flash('Ви не можете видалити роль, оскільки є користувачі,'
                      ' функціонал яких прив\'язаний до даної ролі', 'danger')
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class PlaceModelView(ModelView):
    def _content_formatter(view, context, model, name):
        # Format your string here e.g show first 20 characters
        # can return any valid HTML e.g. a link to another view to
        # show the detail or a popup window
        return model.content[:50]

    can_create = False
    column_formatters = {
        'content': _content_formatter,
    }
    column_searchable_list = ('title',)
    column_sortable_list = ('title', 'created_at', 'user_br.username',
                            'category_br.name', 'region_br.name')
    column_list = ('category_br.name', 'user_br.username', 'title', 'content',
                   'coordinates', 'created_at',)
    column_labels = {
        'category_br.name': 'Категорія',
        'user_br.username': 'Користувач',
        'title': 'Заголовок',
        'content': 'Опис',
        'coordinates': 'Координати',
        'created_at': 'Дата створення',
    }
    form_edit_rules = (
        'category_br', 'region_br', 'user_br', 'title', 'content', 'coordinates'
    )
    form_create_rules = (
        'category_br', 'region_br', 'user_br', 'title', 'content', 'coordinates'
    )
    form_args = dict(
        title=dict(label='Заголовок',
                   validators=[Length(min=5, max=120,
                                      message='Заголовок повинен бути довжиною '
                                              'від 5 до 120 симолів!'),
                               DataRequired(
                                   message='Публікація '
                                           'повинна мати заголовок')]),
        content=dict(label='Опис', validators=[check_text_length]),
        coordinates=dict(label='Координати',
                         validators=[Length(min=5, max=40,
                                            message='Заголовок повинен бути '
                                                    'довжиною '
                                                    'від 5 до 120 симолів!'),
                                     DataRequired(
                                         message='Місце повинно мати'
                                                 ' координати')]),
        category_br=dict(label='Категорія', validators=[DataRequired(
            message='Публікація повинна мати категорію')]),
        region_br=dict(label='Область', validators=[DataRequired(
            message='Публікація повинна мати область')]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message='Публікація повинна мати користувача')]),
    )
    edit_template = 'admin/place_update.html'

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            comments = Comment.query.filter_by(post_id=model.id)
            ratings = Rating.query.filter_by(post_id=model.id)
            if comments.first() or ratings.first():
                for comment in comments:
                    db.session.delete(comment)
                for rating in ratings:
                    db.session.delete(rating)
                self.session.delete(model)
                self.session.commit()
                return True
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class CategoryModelView(ModelView):
    column_searchable_list = ('name',)
    column_sortable_list = ('name',)
    column_list = ('name',)
    column_labels = {
        'name': "Категорія"
    }
    form_edit_rules = (
        'name',
    )
    form_create_rules = (
        'name',
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            place = Place.query.filter_by(category_id=model.id)
            if place.first():
                flash('Ви не можете видалити категорію, оскільки є пости '
                      'з даною категорією', 'danger')
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class RegionModelView(ModelView):
    column_searchable_list = ('name',)
    column_sortable_list = ('name',)
    column_list = ('name',)
    column_labels = {
        'name': "Область"
    }
    form_edit_rules = (
        'name',
    )
    form_create_rules = (
        'name',
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))

    def delete_model(self, model):
        try:
            place = Place.query.filter_by(region_id=model.id)
            if place.first():
                flash('Ви не можете видалити регіон, оскільки є пости '
                      'з даним регіоном', 'danger')
            else:
                self.session.delete(model)
                self.session.commit()
                return True
        except:
            self.session.rollback()
            return False


class CommentModelView(ModelView):
    can_create = False
    column_list = ('user_br.username', 'place_br.title', 'text', 'created_at')
    column_sortable_list = ('user_br.username', 'place_br.title', 'created_at',)
    column_labels = {
        'user_br.username': 'Користувач',
        'place_br.title': 'Пост',
        'text': 'Текст коментаря',
        'created_at': 'Дата створення',
    }
    form_args = dict(
        place_br=dict(label='Пост', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        text=dict(label='Текст коментаря',
                  validators=[Length(
                      min=3, max=500,
                      message='Коментар має бути довжиню від 3 до 500 символів'),
                      DataRequired('Коментар не може бути пустим')]),
        created_at=dict(label='Дата створення'),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))


class RatingModelView(ModelView):
    can_create = False
    column_list = ('user_br.username', 'place_br.title', 'mark')
    column_sortable_list = ('user_br.username', 'place_br.title', 'mark')
    column_labels = {
        'user_br.username': 'Користувач',
        'place_br.title': 'Пост',
        'mark': 'Оцінка',
    }
    form_edit_rules = (
        'user_br', 'place_br'
    )
    form_args = dict(
        place_br=dict(label='Пост', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        created_at=dict(label='Дата створення'),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))


class TypeModelView(ModelView):
    can_create = False
    column_list = ('user_br.username', 'place_br.title', 'place_type')
    column_sortable_list = ('user_br.username', 'place_br.title', 'place_type')
    column_labels = {
        'user_br.username': 'Користувач',
        'place_br.title': 'Пост',
        'place_type': 'Тип пісця',
    }
    form_edit_rules = (
        'user_br', 'place_br', 'place_type'
    )
    form_args = dict(
        place_br=dict(label='Пост', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        user_br=dict(label='Користувач', validators=[DataRequired(
            message="Це поле є обов'язковим")]),
        created_at=dict(label='Дата створення'),
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, *kwargs):
        flash('Немає доступу до цієї сторінки',
              'danger')
        return redirect(url_for('home'))
