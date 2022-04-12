from flask import render_template, redirect, url_for, flash, request, \
    current_app, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from . import user_bp
from app import db, bcrypt, mail
from .forms import LoginForm, RegistrationForm, AccountUpdateForm, \
    PasswordUpdateForm, RequestResetPasswordForm, ResetPasswordForm
from .models import User
from ..tourist_places.models import Place, Type
from PIL import Image
import os, secrets


def save_picture(form_picture):
    rendom_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = rendom_hex + f_ext
    picture_path = os.path.join(user_bp.root_path, '../static/pictures/profile_img',
                                picture_fn)
    # form_picture.save(picture_path)
    # return  picture_fn
    output_size = (100, 100)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


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
    page = request.args.get('page', 1, type=int)
    place_types = db.session.query(Type). \
        filter(Type.user_id == current_user.id,
               Type.place_type == action).all()
    place_id_list = []
    for place_type in place_types:
        place_id_list.append(place_type.place_id)
    places = db.session.query(Place) \
        .filter(Place.id.in_(place_id_list)).\
        paginate(page=page, per_page=current_app.config['PLACE_IN_PAGE'])
    # print(request.path.split('/')[-1])
    return render_template('account_list.html', places=places, action=action)


@user_bp.route('/account/my_added_places')
@login_required
def account_my_added_places():
    page = request.args.get('page', 1, type=int)
    places = Place.query.filter_by(user_id=current_user.id).\
        paginate(page=page, per_page=current_app.config['PLACE_IN_PAGE'])
    # maybe need to change passing change
    return render_template('account_list.html', places=places,
                           action=request.path.split('/')[-1])


@user_bp.route("/account/update/<action>", methods=['GET', 'POST'])
@login_required
def account_update(action):
    form_account = AccountUpdateForm()
    form_password = PasswordUpdateForm()
    if request.method == 'GET':
        form_account.username.data = current_user.username
    if action == 'main':# якщо ми змінюємо тільки основні дані
        if form_account.validate_on_submit():
            if form_account.picture.data:
                picture_file = save_picture(form_account.picture.data)
                current_user.picture = picture_file
            if current_user.username == form_account.username.data:
                pass
            elif User.query.filter_by(username=form_account.username.data).first():
                flash('Користувач з таким іменем вже існує', 'danger')
                return redirect(url_for('user_bp_in.account_update', action='main'))
            current_user.username = form_account.username.data
            try:
                db.session.commit()
                flash('Дані успішно оновлено', 'info')
                return redirect(url_for('user_bp_in.account'))
            except:
                db.session.rollback()
                flash('Помилка при оновленні даних', 'danger')
                return redirect(url_for('user_bp_in.account_update', action='main'))
    if action == 'password': # якщо ми змінюємо пароль
        if form_password.validate_on_submit():
            print('good')
            if current_user.verify_password(form_password.old_password.data):
                current_user.password = bcrypt.generate_password_hash(
                    form_password.
                    password.data). \
                    decode('utf-8')
                try:
                    db.session.commit()
                    flash('Пароль успішно змінено', 'info')
                    return redirect(url_for('user_bp_in.account'))
                except:
                    db.session.rollback()
                    flash('Помилка при оновленні даних', 'danger')
                    return redirect(
                        url_for('user_bp_in.account_update', action='main'))
            else:
                flash('Неправильний старий пароль', 'danger')
                return redirect(url_for('user_bp_in.account_update',
                                        action='password'))
    return render_template('account_update.html', form_account=form_account,
                           form_password=form_password)


def send_mail(user):
    token = user.get_token()
    msg = Message('Запит скидання паролю',
                  recipients=[user.email],
                  sender='noreply@demo.com')
    msg.body = f'''
    Для відновлення паролю перейдіть за наступним посиланням:
    {url_for('user_bp_in.reset_password', token=token, _external=True)}
    '''
    mail.send(msg)


@user_bp.route('/reset_password', methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form_request_reset_password = RequestResetPasswordForm()
    if form_request_reset_password.validate_on_submit():
        user = User.query.filter_by(
            email=form_request_reset_password.email.data).first()
        send_mail(user)
        flash('Лист з посиланням для відновлення паролю надіслано на вашу '
              'пошту', 'success')
    return render_template('request_reset_password.html',
                    form=form_request_reset_password)


@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_token(token)
    if user is None:
        flash('Посилання для зміну паролю більше не активне', 'warning')
        return redirect(url_for('request_password_reset'))
    form_reset_password = ResetPasswordForm()
    if form_reset_password.validate_on_submit():
        user.password = bcrypt.generate_password_hash(
            form_reset_password.new_password.data).decode('utf-8')
        try:
            db.session.commit()
            flash('Ваш пароль змінено!', 'success')
        except:
            db.session.rollback()
            flash('Помилка зміни паролю', 'danger')
        return redirect(url_for('user_bp_in.login'))
    return render_template('change_password.html', form=form_reset_password)
