from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jump_smash'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///draft.db'

# initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

from app import routes, models

# create db tables
with app.app_context():
    db.create_all()