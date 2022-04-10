from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, \
    ValidationError
from flask_wtf.file import FileField, FileAllowed

from app.user.models import User


def check_letters(form, string):
    if not any(x.islower() for x in string.data) or \
            not any(x.isupper() for x in string.data):
        raise ValidationError('Пароль повинен містити великі та малі літери')


def check_digits(form, string):
    if not any(x.isdigit() for x in string.data):
        raise ValidationError('Пароль повинен містити цифру')


def check_symbols(form, string):
    if string.data.strip().isalnum():
        raise ValidationError('Пароль повинен містити символ(не літеру і не '
                              'цифру)')


def check_file_size(form, field):
    if field.data:
        if len(field.data.read()) > 3000000:
            raise ValidationError('Ромір файлу не повинен перевищувати 3 MB')


def check_spaces(form, string):
    if ' ' in string.data:
        raise ValidationError('Пароль не повинен містити пробіли')


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(message='Заповніть це поле!'),
                    Email(message='Некоректна email адреса!')]
    )
    password = PasswordField(
        'Пароль',
        validators=[DataRequired(message='Заповніть це поле!')]
    )
    remember = BooleanField("Запам'ятати мене")
    submit = SubmitField('Увійти')


class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім'я користувача",
        validators=[Length(min=3, max=30,
                           message='Поле повинно бути довжиною '
                                   'від 3 до 30 симолів!'),
                    DataRequired(message='Заповніть це поле!'),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                           "Ім'я повинно містити тільки англійські літери, "
                           "цифри, крапку або нижнє підкреслення!")
                    ]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(message='Заповніть це поле!'),
                    Email(message='Некоректна email адреса!')]
    )
    password = PasswordField(
        'Пароль',
        validators=[Length(min=8, max=30,
                           message='Пароль повинен бути довжиною від 8 до 30 '
                                   'симолів!'),
                    DataRequired(message='Заповніть це поле!'),
                    check_letters, check_digits,
                    check_symbols, check_spaces],
        render_kw={"placeholder": "повинен включати велику та малу літери,"
                                  " цифру та спецсимвол"}
    )
    confirm_password = PasswordField(
        'Підтвердження паролю',
        validators=[DataRequired(message='Заповніть це поле!'),
                    EqualTo('password', message='Паролі не збігаються!')]
    )
    submit = SubmitField('Зареєструватись')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(
                'Користувач з таким email уже зареєстрований!')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(
                "Користувач з таким іменем уже зареєстрований!")


class AccountUpdateForm(FlaskForm):
    username = StringField(
        "Ім'я користувача",
        validators=[Length(min=3, max=30,
                           message='Поле повинно бути довжиною '
                                   'від 3 до 30 симолів!'),
                    DataRequired(message='Заповніть це поле!'),
                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                           "Ім'я повинно містити тільки англійські літери, "
                           "цифри, крапку або нижнє підкреслення!")
                    ]
    )
    picture = FileField('Фото профілю',
                        validators=[
                            FileAllowed(['jpg', 'png', 'jpeg'],
                                        message='Файл повинен мати одне з '
                                                'наступних розширень: '
                                                '.jpg, .png, .jpeg'),
                            check_file_size])
    submit = SubmitField('Оновити')


class PasswordUpdateForm(FlaskForm):
    old_password = PasswordField(
        'Старий пароль',
        validators=[
            DataRequired(message='Заповніть це поле!'),
        ]
    )
    password = PasswordField(
        'Пароль',
        validators=[Length(min=8, max=30,
                           message='Пароль повинен бути довжиною від 8 до 30 '
                                   'симолів!'),
                    DataRequired(message='Заповніть це поле!'),
                    check_letters, check_digits,
                    check_symbols, check_spaces],
        render_kw={"placeholder": "повинен включати велику та малу літери,"
                                  " цифру та спецсимвол"}
    )
    confirm_password = PasswordField(
        'Підтвердження паролю',
        validators=[DataRequired(message='Заповніть це поле!'),
                    EqualTo('password', message='Паролі не збігаються!')]
    )
    submit = SubmitField('Змінити')


class RequestResetPasswordForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(message='Заповніть це поле!'),
                                    Email(message='Некоректна email адреса!')]
                        )
    submit = SubmitField('Надіслати')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError(
                'Користувача з таким email не знайдено.')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        'Пароль',
        validators=[Length(min=8, max=30,
                           message='Пароль повинен бути довжиною від 8 до 30 '
                                   'симолів!'),
                    DataRequired(message='Заповніть це поле!'),
                    check_letters, check_digits,
                    check_symbols, check_spaces],
        render_kw={"placeholder": "повинен включати велику та малу літери,"
                                  " цифру та спецсимвол"}
    )
    confirm_new_password = PasswordField(
        'Підтвердження паролю',
        validators=[DataRequired(message='Заповніть це поле!'),
                    EqualTo('new_password', message='Паролі не збігаються!')]
    )
    submit = SubmitField('Змінити')
