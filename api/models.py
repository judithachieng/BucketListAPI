from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from api import app
from datetime import datetime
from flask import g

db = SQLAlchemy(app)


class User(db.Model):
    _tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    bucketlists = db.relationship('Bucketlist', backref='user',
                                  lazy='dynamic', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expiration=6000):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token, expiration=6000):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False
        user_id = data['id']
        #g.user = db.session.query(User).filter_by(id=user_id).first()
        return user_id

    def __repr__(self):
        return '<User %r>' % self.username


class Bucketlist(db.Model):
    __tablename__ = 'bucketlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    description = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('Item', backref='bucketlist', lazy='dynamic')

    def print_data(self):
        items=Item.query.filter_by(bucketlist_id=self.id).all()
        return {
        "id": self.id,
        "name" : self.name,
        "description" : self.description,
        "date_created" : self.date_created,
        "date_modified" : self.date_modified,
        "created_by" : self.created_by,
        "items" : [item.print_data() for item in items]
        }


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, onupdate=datetime.now)
    done = db.Column(db.Boolean, default=False)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey('bucketlist.id'))

    def print_data(self):
        return {
        "id": self.id,
        "name" : self.name,
        "date_created" : self.date_created,
        "date_modified" : self.date_modified,
        "done" : self.done
        }
