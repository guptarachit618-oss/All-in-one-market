from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
import random


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=2000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f'{self.budget}$'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    image_file = db.Column(db.String(length=60), nullable=False, unique=True, default='default_item.png')

    def __repr__(self):
        return f'Item{self.name}'

    @property
    def sell_price(self):
        return round(self.price * 0.90)   # 90% milega   # user ko market price ka 90% milta hai

    def buy(self, current_user):
        self.owner = current_user.id
        current_user.budget -= self.price

        # Price fluctuation
        increase_percent = random.uniform(0.03, 0.08)
        self.price = round(self.price * (1 + increase_percent))

        db.session.commit()

    def sell(self, current_user):
        payout = self.sell_price      # price badalne se PEHLE nikalo
        self.owner = None
        current_user.budget += payout

        # Price fluctuation
        decrease_percent = random.uniform(0.05, 0.15)
        self.price = round(self.price * (1 - decrease_percent))

        db.session.commit()
        return payout