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

@app.route('/about')
def about():
    return render_template("about.html")

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
    form = MatchForm()

    if form.validate_on_submit():
        total_players = Player.query.count()
        required_players = form.num_courts.data * 4

        if total_players < required_players:
            return render_template('generated_match.html', form=form, matches=None)

        # Clear previous matches and players aaaaaaaaaaaaaaaaaa
        CourtPlayer.query.delete()
        Court.query.delete()
        Match.query.delete()
        db.session.commit()

        players = Player.query.all()
        match_data = create_matches(players, form.num_courts.data)

        new_match = Match(num_courts=form.num_courts.data)
        db.session.add(new_match)
        db.session.flush()

        for data in match_data:
            court = Court(court_number=data['court'], match_id=new_match.id)
            db.session.add(court)
            db.session.flush()

            for player in data['team1'] + data['team2']:
                db.session.add(CourtPlayer(court_id=court.id, player_id=player.id))

        db.session.commit()
        return redirect(url_for('view_matches'))

    return render_template('generated_match.html', form=form, matches=None)

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
