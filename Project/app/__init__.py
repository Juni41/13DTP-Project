from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///draft.db'  

db = SQLAlchemy(app)


from app import routes, models

with app.app_context():
    from app import models 