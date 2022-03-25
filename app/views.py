from flask import render_template, request, current_app as app
from .tourist_places.models import Place, Category

@app.context_processor
def inject_category():
    return dict(categories=Category.query.all())

@app.route('/')
def home():
    places = Place.query.all()
    return render_template('home.html', title='TorP', places=places)
