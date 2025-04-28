from app import app
from flask import render_template, abort, request
from flask_sqlalchemy import SQLALCHEMY
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "draft.db")
db.init_app(app)

import app.models as models

app.route('/')
def layout():
    return render_template("layout.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
