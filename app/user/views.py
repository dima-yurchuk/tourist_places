from flask import render_template, redirect, url_for, flash, request, \
    current_app, session, jsonify, abort
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
from itsdangerous import URLSafeTimedSerializer

from ..utils import handle_post_view
import cloudinary.uploader
from io import BytesIO




def save_picture(form_picture):
    output_size = (800, 800)
    im = Image.open(form_picture)
    im.thumbnail(output_size)
    buf = BytesIO()
    # зберігаємо об'єкт Image в об'єкт BytesIO
    im.save(buf, 'png')
    buf.seek(0)
    image_bytes = buf.read()
    buf.close()
    upload_result = cloudinary.uploader.upload(
        image_bytes, folder=current_app.config['IMG_STORAGE_FOLDER_DEV'])
    return upload_result.get("url").split(
        current_app.config['IMG_STORAGE_FOLDER_DEV'] + '/')[1]


def activate_account(email):
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(email, salt='email-confirm')
    msg = Message('Активувати акаунт',
                  recipients=[email],
                  sender='noreply@demo.com')
    msg.body = f'''
    Для активації акаунту перейдіть за посиланням:
    {url_for('user_bp_in.confirm_email', token=token, _external=True)}
    '''
    mail.send(msg)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_in_db = User.query.filter_by(email=form.email.data).first()
        if user_in_db:
            if not user_in_db.activated:
                activate_account(user_in_db.email)
                flash('Ваш акаунт не активовано! На ваш email надіслано лист '
                      'для активації акаунту!', 'success')
                return redirect(url_for('user_bp_in.login'))
            if user_in_db.verify_password(form.password.data):
                login_user(user_in_db, remember=form.remember.data)
                flash('Користувач успішно увійшов у свій аккаунт!', 'success')
                return redirect(url_for('user_bp_in.account'))
            else:
                flash('Введено невірний пароль.', 'danger')
                return redirect(url_for('user_bp_in.login'))
        else:
            flash('Користувач із вказаним емейлом не зареєстрований на сайті.',
                  'danger')

    return render_template('login.html', form=form, title='Вхід')


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
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.picture = picture_file
        try:
            db.session.add(user)
            db.session.commit()
            activate_account(user.email)
            flash(f'На ваш email надіслано лист для активації акаунту!',
                  'success')
        except:
            db.session.rollback()
            flash('Помилка при реєстрації! Перевірти чи правильно введена '
                  'email адреса!', 'danger')
        return redirect(url_for('user_bp_in.login'))
    return render_template('register.html', title='Реєстрація', form=form)


@user_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt='email-confirm', max_age=3600)
        user_in_db = User.query.filter_by(email=email).first()
        if user_in_db:
            user_in_db.activated = True
            # print(user_in_db.activated)
            try:
                db.session.commit()
                flash('Акаунт успішно активовано!', 'info')
                return redirect(url_for('user_bp_in.login'))
            except:
                db.session.rollback()
                flash('Помилка при активації акаунту!', 'danger')
                return redirect(
                    url_for('user_bp_in.login'))
        else:
            flash('Користувач із вказаним емейлом не зареєстрований на сайті.',
                  'danger')
            return redirect(
                url_for('user_bp_in.login'))
    except:
        flash('Час дії токену закінчився!', 'danger')
        return redirect(
            url_for('user_bp_in.login'))


@user_bp.route('/logout')
def logout():
    logout_user()
    flash('Ви вийшли зі свого облікового запису', 'info')
    return redirect(url_for('user_bp_in.login'))


@user_bp.route('/account')
@login_required
def account():
    return render_template('account.html', title='Профіль')

@user_bp.route('/<int:user_id>/delete')
@login_required
def account_delete(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id != user_id:
        abort(403, description="Ви не маєте доступу до цієї сторінки")
    users = User.query.filter_by(role_id=1).all()
    if user.role_id == 1 and len(users) == 1:
        flash('Не можливо видалити останнього адміністратора сайту!',
              'danger')
        return redirect(url_for('home'))
    try:
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash('Акаунт успішно видалено!', 'success')
    except:
        flash('Помилка при видаленні акаунту', 'danger')
    return redirect(url_for('home'))


@user_bp.route('/account/<action>')
@login_required
def account_list(action):
    place_types = db.session.query(Type). \
        filter(Type.user_id == current_user.id,
               Type.place_type == action).all()
    place_id_list = []
    for place_type in place_types:
        place_id_list.append(place_type.place_id)
    places = handle_post_view(db.session.query(Place).
                              filter(Place.id.in_(place_id_list)),
                              request.args)
    # print(request.path.split('/')[-1])
    return render_template('account_list.html', places=places, action=action,
                           title='Профіль')


@user_bp.route('/account/my_added_places')
@login_required
def account_my_added_places():
    page = request.args.get('page', 1, type=int)
    places = Place.query.filter_by(user_id=current_user.id). \
        paginate(page=page, per_page=current_app.config['PLACE_IN_PAGE'])
    # maybe need to change passing change
    return render_template('account_list.html', places=places,
                           action=request.path.split('/')[-1],
                           title='Мої додані місця')


@user_bp.route("/account/update/<action>", methods=['GET', 'POST'])
@login_required
def account_update(action):
    form_account = AccountUpdateForm()
    form_password = PasswordUpdateForm()
    if request.method == 'GET':
        form_account.username.data = current_user.username
    if action == 'main':  # якщо ми змінюємо тільки основні дані
        if form_account.validate_on_submit():
            if form_account.picture.data:
                picture_file = save_picture(form_account.picture.data)
                current_user.picture = picture_file
            if current_user.username == form_account.username.data:
                pass
            elif User.query.filter_by(
                    username=form_account.username.data).first():
                flash('Користувач з таким іменем вже існує', 'danger')
                return redirect(
                    url_for('user_bp_in.account_update', action='main'))
            current_user.username = form_account.username.data
            try:
                db.session.commit()
                flash('Дані успішно оновлено', 'info')
                return redirect(url_for('user_bp_in.account'))
            except:
                db.session.rollback()
                flash('Помилка при оновленні даних', 'danger')
                return redirect(
                    url_for('user_bp_in.account_update', action='main'))
    if action == 'password':  # якщо ми змінюємо пароль
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
                           form_password=form_password,
                           title='Редагування профіль')


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
                           form=form_request_reset_password,
                           title='Скидання паролю')


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
    return render_template('change_password.html', form=form_reset_password,
                           title='Зміна паролю')
