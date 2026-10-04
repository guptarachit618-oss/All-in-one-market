from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
import os
app.config['SECRET_KEY'] = os.environ.get('4b3464b1c50bd426899572c9ada6af8f84feeb4bb858277e', 'dev-only-key')
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view ='login_page'
login_manager.login_message_category='info'
from market.models import Item
from market import routes

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Item': Item}