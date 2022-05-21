from flask import render_template, request, current_app as app, current_app
from .tourist_places.models import Place, Category
from .utils import handle_post_view
from app.tourist_places.models import Category
from app import db

@app.context_processor
def inject_category():
    return dict(categories=Category.query.all())

@app.route('/')
def home():
    places = handle_post_view(Place.query, request.args)
    db.session.commit()
    return render_template('home.html', title='RestInUA', places=places)

@app.route('/contacts')
def contacts():
    category = Category(name='test')
    db.session.add(category)
    return render_template('contacts.html', title='Контакти')
