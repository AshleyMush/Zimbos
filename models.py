from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()




class User(UserMixin, db.Model):
    """
    User model storing account credentials and profile data.

    Attributes:
        id (int): Primary key.
        email (str): Unique email address for login.
        password_hash (str): Hashed password.
        name (str): Display name of the user.
        phone (str): Contact phone number.
        is_active (bool): Whether the user has confirmed email.
        is_admin (bool): Whether the user has admin privileges.
        basket_items (list): Relationship to PurchasedItem entries.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='User')

    basket_items = db.relationship('PurchasedItem', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.id} {self.email}>"

class Group(db.Model):
    """
    Group model representing an available group for users to join.

    Attributes:
        id (int): Primary key.
        name (str): Name of the group.
        url (str): URL link for the group.
        description (str): Text description of the group.
        picture_filename (str): Filename for the group's image.
        member_count (int): Number of times the group URL has been used.
        basket_items (list): Relationship to PurchasedItem entries.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    picture_filename = db.Column(db.String(255))
    member_count = db.Column(db.Integer, default=0)
    basket_items = db.relationship('PurchasedItem', backref='group', lazy=True)

    def __repr__(self):
        return f"<Group {self.id} {self.name}>"

class PurchasedItem(db.Model):
    """
    Association model linking a User to a Group in the user's basket.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User model.
        group_id (int): Foreign key to the Group model.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PurchasedItem {self.id} User:{self.user_id} Group:{self.group_id}>"
