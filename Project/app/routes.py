from app import app
from flask import render_template, abort
from flask_sqlalchemy import SQLALCHEMY
import os

if __name__ == "__main__":
    app.run(debug=True)