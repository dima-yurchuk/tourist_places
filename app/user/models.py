from app.tourist_places.models import Comment, Place, Type, Rating, Region
from app import db, bcrypt, login_manager
from flask_login import UserMixin, current_user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):  # type: ignore

    def __init__(self, username, email, password, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    id = db.Column(db.Integer, primary_key=True)  # type: ignore
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    picture = db.Column(db.String(30), nullable=False,
                        server_default='default.jpg')  # type: ignore
    role_id = db.Column(db.Integer, db.ForeignKey('role.id',
                                                  ondelete='RESTRICT'),
                        nullable=False)

    comment = db.relationship('Comment', backref='user_br', lazy=True)
    like = db.relationship('Rating', backref='user_br', lazy=True)
    place = db.relationship('Place', backref='user_br', lazy=True)
    place_type = db.relationship('Type', backref='user_br', lazy=True)

    def is_admin(self):
        return self.admin

    def is_favourite_place(self, place):
        return not Type.query.filter_by(place_id=place.id,
                                        user_id=self.id,
                                        place_type='favourite').first() is None

    def is_visited_place(self, place):
        return not Type.query.filter_by(place_id=place.id,
                                        user_id=self.id,
                                        place_type='visited').first() is None

    def is_want_to_visit_place(self, place):
        return not Type.query.filter_by(place_id=place.id,
                                        user_id=self.id,
                                        place_type='want to visit').first() is None

    def verify_password(self, pwd):
        return bcrypt.check_password_hash(self.password, pwd)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

    user = db.relationship('User', backref='user_br', lazy=True)

    def __repr__(self):
        return f"Role('{self.name}'')"
