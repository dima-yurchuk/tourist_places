from app import db
from datetime import datetime
# from flask_sqlalchemy import hybrid_property
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import select, func, and_, case
import itertools


class Category(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    name = db.Column(db.String(25), unique=True, nullable=False)

    category = db.relationship('Place', backref='category_br', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}'')"


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    region = db.relationship('Place', backref='region_br', lazy=True)

    def __repr__(self):
        return f"Region('{self.name}'')"


class Place(db.Model):  # type: ignore
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id',
                                                    ondelete='RESTRICT'),
                          nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',
                                                    ondelete='RESTRICT'))
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text)
    location = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id',
                                                      ondelete='RESTRICT'),
                            nullable=False)

    comments = db.relationship('Comment', backref='place_br', lazy=True)
    ratings = db.relationship('Rating', backref='place_br', lazy=True)
    types = db.relationship('Type', backref='place_br', lazy=True)

    def total_comments(self):
        return Comment.query.filter(Comment.place_id == self.id).count()


    @hybrid_property
    def average_rating(self):
        ratings = db.session.query(Rating.mark).filter(
            Rating.place_id == self.id).all()
        ratings_list = list(itertools.chain(*ratings))
        if len(ratings_list) > 0:
            return round(sum(ratings_list)/len(ratings_list), 1)
        return 0

    @average_rating.expression
    def average_rating(cls):
        ratings = db.session.query(Rating.mark).filter(
            Rating.place_id == cls.id).all()
        ratings_list = list(itertools.chain(*ratings))
        if len(ratings_list) > 0:
            return select([func.sum(Rating.mark)/func.count(Rating.mark)]).where(
                and_(Rating.place_id == cls.id)).label(
                'average_rating')
        else:
            return select(
                [func(func.sum(Rating.mark))]).where(
                and_(Rating.place_id == cls.id)).label(
                'average_rating')

    def __repr__(self):
        return f'<Place {self.id} {self.title} >'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',
                                                  ondelete='RESTRICT'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id',
                                                   ondelete='RESTRICT'))
    text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Comment {self.id} {self.user_id} {self.place_id} ' \
               f'{self.text} >'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',
                                                  ondelete='RESTRICT'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id',
                                                   ondelete='RESTRICT'))
    mark = db.Column(db.Integer)

    def __repr__(self):
        return f'<Rating {self.id} {self.user_id} {self.place_id} ' \
               f'{self.mark} >'


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',
                                                  ondelete='RESTRICT'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id',
                                                   ondelete='RESTRICT'))
    place_type = db.Column(db.String(25), nullable=False)
    places = db.relationship('Place', backref='type_br', lazy=True)

    def __repr__(self):
        return f'<Type {self.id} {self.user_id} {self.place_id} ' \
               f'{self.place_type} >'
