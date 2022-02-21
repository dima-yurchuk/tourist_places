from app import db
# from app.user.models import User
from datetime import datetime
# from flask_sqlalchemy import hybrid_property
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import select, func, and_


class Category(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    name = db.Column(db.String(25), unique=True, nullable=False)

    category = db.relationship('Place', backref='category_br', lazy=True)

    def __repr__(self):
        return f"Category('{self.name}'')"

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    region = db.relationship('Place', backref='place_br', lazy=True)

    def __repr__(self):
        return f"Region('{self.name}'')"


class Place(db.Model):  # type: ignore

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'),
                          nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text)
    coordinates = db.Column(db.String(25), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)

    comments = db.relationship('Comment', backref='post_br', lazy=True)
    ratings = db.relationship('Rating', backref='post_br', lazy=True)
    types = db.relationship('Type', backref='post_br', lazy=True)

    def __repr__(self):
        return f'<Place {self.id} {self.title} >'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Comment {self.id} {self.user_id} {self.post_id} ' \
               f'{self.text} >'


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    mark = db.Column(db.Float)

    def __repr__(self):
        return f'<Rating {self.id} {self.user_id} {self.place_id} ' \
               f'{self.mark} >'


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    type = db.Column(db.Integer)

    def __repr__(self):
        return f'<Type {self.id} {self.user_id} {self.place_id} ' \
               f'{self.type} >'
