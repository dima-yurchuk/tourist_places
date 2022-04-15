from flask import current_app as app, render_template, flash, redirect, \
    url_for, abort, request, current_app
from .models import Region, Place, Category, Type, Comment, Rating
from . import place_bp
from .form import FormPlaceCreate, FormPlaceUpdate, FormComment
from app import db
from flask_login import current_user, login_required
from app.utils import handle_post_view


@app.context_processor
def get_regions_list():
    return dict(regions=Region.query.all())


@place_bp.route('/create', methods=['GET', 'POST'])
@login_required
def place_create():
    if current_user.role_id != 2:
        abort(403, description="Ви не маєте доступу до цієї сторінки")
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
    form_comment = FormComment()
    place = Place.query.get_or_404(place_id)
    comments = Comment.query.filter_by(place_id=place_id).all()
    if form_comment.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(user_id=current_user.id, place_id=place_id,
                          text=form_comment.comment.data)
        print(comment)
        print('dfsd')
        try:
            db.session.add(comment)
            db.session.commit()
            return redirect(
                url_for('place_bp_in.place_view', place_id=place.id))
        except:
            db.session.rollback()
            flash('Помилка додавання коменнтаря', 'danger')
    return render_template('place_view.html', form=form_comment, place=place,
                           comments=comments)


@place_bp.route('/<int:place_id>/update', methods=["GET", "POST"])
@login_required
def place_update(place_id):
    form = FormPlaceUpdate.new()
    place = Place.query.get_or_404(place_id)
    if current_user.role_id != 2 and place.user_id != current_user.id:
        abort(403, description="Ви не маєте доступу до цієї сторінки")

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
        form.region.data = place.region_br.id
        form.title.data = place.title
        form.content.data = place.content
        form.coordinates.data = place.coordinates
    return render_template('place_update.html',
                           title='Оновити публікацію', form=form)


@place_bp.route('/<int:place_id>/delete', methods=["GET", "POST"])
def place_delete(place_id):
    place = Place.query.get_or_404(place_id)
    if current_user.role_id != 2 and place.user_id != current_user.id:
        abort(403, description="Ви не маєте доступу до цієї сторінки")
    try:
        db.session.delete(place)
        db.session.commit()
        flash('Публікацію успішно видалено!', 'success')
    except:
        flash('Помилка при видаленні публікації', 'danger')
    return redirect(url_for('home'))


@place_bp.route('/comment/<int:comment_id>/delete')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    place_id = comment.place_id
    if current_user.id != comment.user_id:
        abort(403, description="Ви не маєте доступу до цієї сторінки")
    try:
        db.session.delete(comment)
        db.session.commit()
        # flash('Публікацію успішно видалено!', 'success')
    except:
        flash('Помилка при видаленні коментаря', 'danger')
    return redirect(url_for('place_bp_in.place_view', place_id=place_id))


@place_bp.route('/region_places/<int:region_id>/', methods=["GET", "POST"])
def region_places(region_id):
    places = handle_post_view(Place.query.filter_by(region_id=region_id),
                              request.args)
    region = Region.query.get_or_404(region_id)
    return render_template('region_places.html',
                           title=region.name, places=places)


@place_bp.route('/category_places/<int:category_id>/', methods=["GET", "POST"])
def category_places(category_id):
    places = handle_post_view(Place.query.filter_by(category_id=category_id),
                              request.args)
    category = Category.query.get_or_404(category_id)
    return render_template('category_places.html',
                           title=category.name, places=places)


@place_bp.route('/<int:place_id>/favourite_handle', methods=["GET", "POST"])
@login_required
def favourite_list_handle(place_id):
    type_place = Type.query.filter_by(place_id=place_id,
                                      user_id=current_user.id,
                                      place_type='favourite').first()
    # якщо місце не додано у список улюблених, то додаємо
    if type_place is None:
        type_place = Type(user_id=current_user.id, place_id=place_id,
                          place_type='favourite')
        try:
            db.session.add(type_place)
            db.session.commit()
            flash('Місце додано до списку "Улюблені"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при додаванні місця до списку "Улюблені"', 'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
    else:  # інакше видаляємо зі списку улюблених
        place = Place.query.get_or_404(place_id)
        try:
            db.session.delete(type_place)
            db.session.commit()
            flash('Місце видалено зі списку "Улюблені"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place.id))
        except:
            db.session.rollback()
            flash('Помилка при видаленні місця зі списку "Улюблені"', 'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place.id))


@place_bp.route('/<int:place_id>/visited_handle', methods=["GET", "POST"])
@login_required
def visited_list_handle(place_id):
    type_place = Type.query.filter_by(place_id=place_id,
                                      user_id=current_user.id,
                                      place_type='visited').first()
    # якщо місце не додано у список відвіданих, то додаємо
    if type_place is None:
        type_place = Type(user_id=current_user.id, place_id=place_id,
                          place_type='visited')
        try:
            db.session.add(type_place)
            db.session.commit()
            flash('Місце додано до списку "Відвідані"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при додаванні місця до списку "Відвідані"',
                  'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
    else:  # інакше видаляємо зі списку відвіданих
        place = Place.query.get_or_404(place_id)
        try:
            db.session.delete(type_place)
            db.session.commit()
            flash('Місце видалено зі списку "Відвідані"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place.id))
        except:
            db.session.rollback()
            flash('Помилка при видаленні місця зі списку "Відвідані"',
                  'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place.id))


@place_bp.route('/<int:place_id>/want_to_visit_handle',
                methods=["GET", "POST"])
@login_required
def want_to_visit_list_handle(place_id):
    type_place = Type.query.filter_by(place_id=place_id,
                                      user_id=current_user.id,
                                      place_type='want to visit').first()
    # якщо місце не додано у список 'Хочу відвідати', то додаємо
    if type_place is None:
        type_place = Type(user_id=current_user.id, place_id=place_id,
                          place_type='want to visit')
        try:
            db.session.add(type_place)
            db.session.commit()
            flash('Місце додано до списку "Хочу відвідати"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при додаванні місця до списку "Хочу відвідати"',
                  'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
    else:  # інакше видаляємо зі списку 'хочу відвідати'
        try:
            db.session.delete(type_place)
            db.session.commit()
            flash('Місце видалено зі списку "Хочу відвідати"', 'success')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при видаленні місця зі списку "Хочу відвідати"',
                  'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))


@place_bp.route('/rate/<int:mark>/<int:place_id>', methods=["GET", "POST"])
@login_required
def rate_place(place_id, mark):
    rating = Rating.query.filter_by(place_id=place_id,
                                    user_id=current_user.id).first()
    if rating is None:
        rating = Rating(user_id=current_user.id, place_id=place_id, mark=mark)
        try:
            db.session.add(rating)
            db.session.commit()
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка оцінки місця',
                  'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
    else:
        try:
            db.session.delete(rating)
            db.session.commit()
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))
        except:
            db.session.rollback()
            flash('Помилка при видаленні оцінки', 'danger')
            return redirect(url_for('place_bp_in.place_view',
                                    place_id=place_id))


@place_bp.route('/search', methods=["GET"])
def search():
    query = request.args.get('query')
    result_by_keywords = Place.query.msearch(query)
    result_by_substring = Place.query.filter(Place.title.contains(f'%{query}%'))
    places = result_by_keywords.union(result_by_substring)
    places = handle_post_view(places,
                              request.args)
    return render_template('home.html', title='RestInUA', places=places)
