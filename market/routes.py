from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
import random
import time

last_tick = time.time()


def fluctuate_prices():
    """Har 10 second (testing) / 5 minute mein sab items ka price thoda upar-neeche."""
    global last_tick
    ticks = int((time.time() - last_tick) // 7)   # testing ke liye 10; final mein 300 (5 min)
    if ticks < 1:
        return
    last_tick = time.time()
    for item in Item.query.all():
        for _ in range(min(ticks, 12)):
            item.price = max(50, round(item.price * (1 + random.uniform(-0.05, 0.06))))
    db.session.commit()


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    if request.method == 'POST':
        # Purchase item logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                price_paid = p_item_object.price
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {price_paid}$. Your new budget: {current_user.prettier_budget}. New market price: {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately You dont have enough money to purchase {p_item_object.name}", category='danger')

        # Sell item logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                payout = s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} for {payout}$ back to market. Your new budget: {current_user.prettier_budget}. New market price: {s_item_object.price}$", category='success')
            else:
                flash("Something went wrong", category='danger')

        return redirect(url_for('market_page'))

    # GET request
    fluctuate_prices()
    items = Item.query.filter_by(owner=None)
    owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('market.html', items=items, purchase_form=purchase_form,
                           owned_items=owned_items, selling_form=selling_form)


@app.route('/api/prices')
@login_required
def api_prices():
    fluctuate_prices()
    return {str(i.id): {'price': i.price, 'sell_price': i.sell_price} for i in Item.query.all()}


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account Created Successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user : {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as :{attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and Password does not match! Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))