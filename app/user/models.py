from app.tourist_places.models import Comment, Place, Type, Rating, Region
from app import db, bcrypt, login_manager
from flask_login import UserMixin

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
    # type: ignore
    email = db.Column(db.String(50), unique=True, nullable=False)
    # type: ignore
    password = db.Column(db.String(70), nullable=False)
    # type: ignore
    picture = db.Column(db.String(30), nullable=False,
                        server_default='default.jpg')  # type: ignore
    admin = db.Column(db.Boolean, default=False)  # type: ignore

    comment = db.relationship('Comment', backref='user_br', lazy=True)
    # type: ignore
    like = db.relationship('Rating', backref='user_br', lazy=True)
    # type: ignore
    posts = db.relationship('Place', backref='user_br', lazy=True)
    # type: ignore
    type = db.relationship('Type', backref='user_br', lazy=True)
    # type: ignore

    def is_admin(self):
        return self.admin

    def verify_password(self, pwd):
        return bcrypt.check_password_hash(self.password, pwd)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
