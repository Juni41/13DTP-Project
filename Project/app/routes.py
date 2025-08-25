from app import app, db
from flask import render_template, abort, request, redirect, url_for
from app.models import Player, Match, Court, CourtPlayer
from app.forms import PlayerForm, MatchForm
from sqlalchemy import case
import random 

@app.route('/')
def layout():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/draft', methods=['GET', 'POST'])
def draft():
    form = PlayerForm()  
    # Get the sorting parameter from url/request
    sort_by = request.args.get('sort_by', 'id') 

    if sort_by == 'gender':
        players_query = Player.query.order_by(Player.gender) # Order players by the gender
    elif sort_by == 'skill':
        skill_order = case( # Sort order for skill levels
            (Player.skill == 'Beginner', 1),
            (Player.skill == 'Intermediate', 2),
            (Player.skill == 'Advanced', 3),
        )
        players_query = Player.query.order_by(skill_order)
    else:
        # Default sort by id
        players_query = Player.query.order_by(Player.id)
    players = players_query.all()
    
    if form.validate_on_submit():
        db.session.add(Player(
            name=form.name.data,
            skill=form.skill.data,
            gender=form.gender.data
        ))
        db.session.commit()
        return redirect(url_for('draft', sort_by=sort_by))

    return render_template('draft.html', players=players, form=form, current_sort=sort_by)

@app.route('/generate_matches', methods=['POST'])
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

@app.route('/set_winner/<int:court_id>/<int:team_number>', methods=['POST'])
def set_winner(court_id, team_number):
    court = Court.query.get_or_404(court_id) # Find the court in the database or return a 404 error if not found.

    if court.winning_team is not None: # Check if a winner has already been set to prevent changes.
        return redirect(url_for('view_matches'))

    court.winning_team = team_number # Update the winning_team column with the provided team number (1 or 2).
    db.session.commit()
    return redirect(url_for('view_matches'))

@app.route('/matches', methods=['GET'])
def view_matches():
    matches = Match.query.all()
    assigned_player_ids = db.session.query(CourtPlayer.player_id).subquery()
    resting_players = Player.query.filter(Player.id.not_in(assigned_player_ids)).all()
    return render_template('generated_match.html', matches=matches, resting_players=resting_players)

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('draft'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")
