from app import app, db  
from flask import render_template, abort, request, redirect, url_for
from app.models import Player, Match, Court, CourtPlayer
from app.forms import PlayerForm, MatchForm



@app.route('/')
def layout():
    return render_template("layout.html")

@app.route('/home')
def homepage():
    return render_template("home.html")

@app.route('/draft', methods=['GET', 'POST'])
def draft():
    form = PlayerForm()
    players = Player.query.all()
    
    if form.validate_on_submit():
        new_player = Player(
            name=form.name.data,
            skill=form.skill.data,
            gender=form.gender.data
        )
        db.session.add(new_player)
        db.session.commit()
        return redirect(url_for('draft'))
    
    return render_template('draft.html', players=players, form=form)

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    player_name = player.name
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('draft'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
