from flask import current_app as app, render_template, flash, redirect, \
    url_for, abort, request
from .models import Region, Place, Category
from . import place_bp
from .form import FormPlaceCreate, FormPlaceUpdate
from app import db
from flask_login import current_user, login_required


@app.context_processor
def get_regions_list():
    return dict(regions=Region.query.all())


@place_bp.route('/create', methods=['GET', 'POST'])
@login_required
def place_create():
    form = FormPlaceCreate.new()
    if form.validate_on_submit():
        category = db.session.query(Category.id).filter(
            Category.id == form.category.data)
        region = db.session.query(Region.id).filter(
            Region.id == form.region.data)
        place = Place(category_id=category,
                      user_id=current_user.id,
                      region_id=region,
                      title=form.title.data,
                      content=form.content.data,
                      coordinates=form.coordinates.data)
        try:
            db.session.add(place)
            db.session.commit()
            flash('Публікація успішно створена', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place.id))
        except:
            db.session.rollback()
            flash('Помилка при додаванні публікації', 'danger')
            return redirect(url_for('place_bp_in.place_create'))

    return render_template('place_create.html', form=form,
                           title='Створити публікацію')

@place_bp.route('/<int:place_id>', methods=["GET", "POST"])
def place_view(place_id):
    place = Place.query.get_or_404(place_id)
    return render_template('place_view.html', place=place)

@place_bp.route('/<int:place_id>/update', methods=["GET", "POST"])
def place_update(place_id):
    form = FormPlaceUpdate.new()
    place = Place.query.get_or_404(place_id)
    if not current_user.is_authenticated or current_user.id != place.user_id:
        abort(403, description="Ви не маєте прав на редагування даної "
                               "публікації")

    if form.validate_on_submit():
        place.category_id = db.session.query(Category.id).filter(
            Category.id == form.category.data)
        place.region_id = db.session.query(Region.id).filter(
            Region.id == form.region.data)
        place.title = form.title.data
        place.content = form.content.data
        place.coordinates = form.coordinates.data
        try:
            db.session.commit()
            flash('Публікація успішно оновлена', 'info')
            return redirect(
                url_for('place_bp_in.place_view', place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при оновленні публікації', 'danger')
    elif request.method == 'GET':  # якщо ми відкрили сторнку
        # для редагування, записуємо у поля форми значення з БД
        form.category.data = place.category_br.id
        form.region.data = place.place_br.id
        form.title.data = place.title
        form.content.data = place.content
        form.coordinates.data = place.coordinates
    return render_template('place_update.html',
                           title='Оновити публікацію', form=form)

@place_bp.route('/<int:place_id>/delete', methods=["GET", "POST"])
def place_delete(place_id):
    place = Place.query.get_or_404(place_id)
    if not current_user.is_authenticated or current_user.id != place.user_id:
        abort(403, description="Ви не маєте прав на видалення даної "
                               "публікації")
    try:
        db.session.delete(place)
        db.session.commit()
        flash('Публікацію успішно видалено!', 'success')
    except:
        flash('Помилка при видаленні публікації', 'danger')
    return redirect(url_for('home'))

@place_bp.route('/region_places/<int:region_id>/', methods=["GET", "POST"])
def region_places(region_id):
    places = Place.query.filter_by(region_id=region_id)
    region = Region.query.get_or_404(region_id)
    return render_template('region_places.html',
                           title=region.name, places=places)

@place_bp.route('/category_places/<int:category_id>/', methods=["GET", "POST"])
def category_places(category_id):
    places = Place.query.filter_by(category_id=category_id)
    category = Category.query.get_or_404(category_id)
    return render_template('category_places.html',
                           title=category.name, places=places)

