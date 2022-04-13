from flask import render_template, request, current_app as app, current_app
from .tourist_places.models import Place, Category
from .utils import handle_post_view

@app.context_processor
def inject_category():
    return dict(categories=Category.query.all())

@app.route('/')
def home():
    # page = request.args.get('page', 1, type=int)
    places = handle_post_view(Place.query, request.args)
    # places = Place.query.paginate(page=page,
    #                               per_page=current_app.config['PLACE_IN_PAGE'])
    return render_template('home.html', title='RestInUA', places=places)
