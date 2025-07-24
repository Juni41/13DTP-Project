from app import app, db
from flask import render_template, abort, request, redirect, url_for
from app.models import Player, Match, Court, CourtPlayer
from app.forms import PlayerForm, MatchForm
import random 

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
        db.session.add(Player(
            name=form.name.data,
            skill=form.skill.data,
            gender=form.gender.data
        ))
        db.session.commit()
        return redirect(url_for('draft'))

    return render_template('draft.html', players=players, form=form)

@app.route('/generate_matches', methods=['GET', 'POST'])
def generate_matches():


def create_matches(players, num_courts):
    available = list(players)
    matches = []

    for court_num in range(1, num_courts + 1):
        if len(available) < 4:
            break

        selected = random.sample(available, 4)
        for p in selected:
            available.remove(p)

        matches.append({
            'court': court_num,
            'team1': selected[:2],
            'team2': selected[2:]
        })

    return matches

@app.route('/matches')
def view_matches():
    matches = Match.query.all()
    return render_template('generated_match.html', matches=matches)

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('draft'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")
