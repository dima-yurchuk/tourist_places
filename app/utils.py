from app.tourist_places.models import Place
from flask import current_app


def handle_post_view(places, request_args):
    page = request_args.get('page', 1, type=int)
    sort_by = request_args.get('sort_by', 'newest', type=str)
    if sort_by == 'rating':
        places = places.order_by(Place.average_rating.desc())
    elif sort_by == 'oldest':
        # print('oldest')
        places = places.order_by(Place.created_at.asc())
    else:
        # print('newest')
        places = places.order_by(Place.created_at.desc())
    return places.paginate(page=page,
                           per_page=current_app.config['PLACE_IN_PAGE'])
