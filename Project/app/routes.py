from app import app, db  
from flask import render_template, abort, request, redirect, url_for
from app.models import Player, Match, Court, CourtPlayer

@app.route('/')
def layout():
    return render_template("layout.html")

@app.route('/home')
def homepage():
    return render_template("home.html")

@app.route('/draft')
def draft():
    players = Player.query.all()
    return render_template('draft.html', players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form['name']
    skill = request.form['skill']
    gender = request.form['gender']
    
    new_player = Player(name=name, skill=skill, gender=gender)
    db.session.add(new_player)
    db.session.commit()
    return redirect(url_for('draft'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
