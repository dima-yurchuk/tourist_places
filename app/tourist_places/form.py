from .models import Category, Place, Region
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField, TextAreaField,
                     ValidationError)
from wtforms.validators import DataRequired, Length, Regexp
import re


def check_text_length(form, field):
    clean_text = re.sub(re.compile('<.*?>'), '', field.data)
    length = len(clean_text)
    if length < 15:
        raise ValidationError('Текст повинен бути довжиною від 15 символів ('
                              'ви ввели - {})'.format(length))


class FormPlaceCreate(FlaskForm):
    category = SelectField(
        'Категорія',
        coerce=int
    )
    region = SelectField(
        'Область',
        coerce=int
    )
    title = StringField(
        "Заголовок",
        validators=[Length(min=5, max=120,
                           message='Заголовок повинен бути довжиною '
                                   'від 5 до 120 симолів!'),
                    DataRequired(message='Публікація повинна мати заголовок')]
    )
    content = TextAreaField(
        'Вміст',
        validators=[check_text_length],
        # render_kw={'cols':35, 'rows': 5}
    )
    location = StringField(
        "Місце розташування(посилання на гугл карти)",
        validators=[DataRequired(message='Місце повинно мати розташування'),
                    Regexp('^https://www.google.com/maps/place.*$', 0,
                           "Повинно міститися посилання на google maps"
                           "(https://www.google.com/maps/place/...)")
                    ]
    )
    submit = SubmitField('Створити')

    def validate_title(self, field):
        if Place.query.filter_by(title=field.data).first():
            raise ValidationError(
                'Ви вже створювали публікацію з такою самою назвою!')

    def validate_category(self, field):
        if field.data == 0:
            raise ValidationError('Ви не обрали категорію!')

    @classmethod
    def new(cls):
        # Instantiate the form
        form = cls()
        # Update the choices for the agency field
        choices_list_category = [(elem.id, elem.name) for elem in
                                 Category.query.all()]
        choices_list_category.insert(0, (0, 'Оберіть категорію'))
        form.category.choices = choices_list_category
        choices_list_region = [(elem.id, elem.name) for elem in
                               Region.query.all()]
        choices_list_region.insert(0, (0, 'Оберіть область'))
        form.region.choices = choices_list_region
        return form


class FormPlaceUpdate(FlaskForm):
    category = SelectField(
        'Категорія',
        coerce=int
    )
    region = SelectField(
        'Область',
        coerce=int
    )
    title = StringField(
        "Заголовок",
        validators=[Length(min=5, max=120,
                           message='Заголовок повинен бути довжиною '
                                   'від 5 до 120 симолів!'),
                    DataRequired(message='Публікація повинна мати заголовок')]
    )
    content = TextAreaField(
        'Вміст',
        validators=[check_text_length],
        # render_kw={'cols':35, 'rows': 5}
    )
    location = StringField(
        "Місце розташування(посилання на гугл карти)",
        validators=[DataRequired(message='Місце повинно мати розташування'),
                    Regexp('^https://www.google.com/maps/place.*$', 0,
                           "Повинно міститися посилання на google maps"
                           "(https://www.google.com/maps/place/...)")
                    ]
    )
    submit = SubmitField('Оновити')



    @classmethod
    def new(cls):
        # Instantiate the form
        form = cls()
        # Update the choices for the agency field
        form.category.choices = [(elem.id, elem.name) for elem in
                                 Category.query.all()]
        form.region.choices = [(elem.id, elem.name) for elem in
                               Region.query.all()]
        return form


class FormComment(FlaskForm):
    comment = TextAreaField(
        'Коментар',
        render_kw={'cols': 40, 'rows': 3},
        validators=[Length(
            min=3, max=500,
            message='Коментар має бути довжиню від 3 до 500 символів'),
            DataRequired('Коментар не може бути пустим')
        ]
    )
    submit = SubmitField('Опублікувати')
