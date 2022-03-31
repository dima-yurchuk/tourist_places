from flask import render_template, redirect, url_for, flash, request, \
    current_app, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required

from . import user_bp
from app import db
from .forms import LoginForm, RegistrationForm
from .models import User
from ..tourist_places.models import Place, Type


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_in_db = User.query.filter_by(email=form.email.data).first()
        if user_in_db:
            if user_in_db.verify_password(form.password.data):
                login_user(user_in_db, remember=form.remember.data)
                print('flash')
                flash('Користувач успішно увійшов у свій аккаунт!', 'success')
                return redirect(url_for('user_bp_in.account'))
            else:
                flash('Введено невірний пароль.', 'danger')
                return redirect(url_for('user_bp_in.login'))
        else:
            flash('Користувач із вказаним емейлом не зареєстрований на сайті.',
                  'danger')

    return render_template('login.html', form=form, title='Login')


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,
                    role_id=3)
        print(user)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'Користувач {form.username.data} успішно зареєстрований!',
                  'success')
        except:
            db.session.rollback()
            flash('Помилка при реєстрації!', 'danger')
        return redirect(url_for('user_bp_in.login'))
    return render_template('register.html', title='Register', form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    flash('Ви вийшли зі свого облікового запису', 'info')
    return redirect(url_for('user_bp_in.login'))


@user_bp.route('/account')
@login_required
def account():
    return render_template('account.html')


@user_bp.route('/account/<action>')
@login_required
def account_list(action):
    place_types = db.session.query(Type). \
        filter(Type.user_id == current_user.id,
               Type.place_type == action).all()
    place_id_list = []
    for place_type in place_types:
        place_id_list.append(place_type.place_id)
    favourite_places = db.session.query(Place)\
        .filter(Place.id.in_(place_id_list)).all()
    return render_template('account_list.html', places=favourite_places)