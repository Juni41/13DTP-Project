from flask import render_template, flash, request, redirect, url_for
from app import app, db
from app.models import Player, Match, Court, CourtPlayer
from app.forms import PlayerForm, MatchForm
from sqlalchemy import case
from app.matchmaking import create_skill_based_matches, create_random_matches, create_mixed_gender_matches

@app.route('/')
def layout():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/draft', methods=['GET', 'POST'])
def draft():
    player_form = PlayerForm()
    match_form = MatchForm()
    MAX_PLAYERS = 12
    current_player_count = Player.query.count()

    if player_form.validate_on_submit(): # Backend enforcement of player limit even if frontend is bypassed.
        if current_player_count >= MAX_PLAYERS:
            flash(f"The maximum number of players ({MAX_PLAYERS}) has been reached.", "error")
            return redirect(url_for('draft'))

        sort_by = request.form.get('sort_by', 'id')
        clean_name = ' '.join(player_form.name.data.split()) # Remove beginning, trailing and in between whitespace.
        new_player = Player(
            name=clean_name,
            skill=player_form.skill.data,
            gender=player_form.gender.data
        )
        db.session.add(new_player)
        db.session.commit()
        flash(f'Player "{clean_name}" was added successfully!', 'success')
        return redirect(url_for('draft', sort_by=sort_by))
    
    sort_by = request.args.get('sort_by', 'id') # Get current sort order form url query string.

    players_query = Player.query
    if sort_by == 'gender':
        players_query = players_query.order_by(Player.gender.asc(), Player.name.asc())
        
    elif sort_by == 'skill': # Create virtual column to sort by.
        skill_order = case(
            (Player.skill == 'Beginner', 1),
            (Player.skill == 'Intermediate', 2),
            (Player.skill == 'Advanced', 3),
            else_=0 # Assign to unexpected values.
        )
        players_query = players_query.order_by(skill_order.desc(), Player.name.asc())
    else:
        players_query = players_query.order_by(Player.name.asc())
    players = players_query.all()

    max_courts = len(players) // 4
    if max_courts > 0:
        match_form.num_courts.choices = [
            (i, f"{i} court{'s' if i > 1 else ''} ({i*4} players)")
            for i in range(1, max_courts + 1)
        ]
        match_form.num_courts.data = max_courts
    else:
        match_form.num_courts.choices = []

    return render_template(
        'draft.html',
        players=players,
        form=player_form,
        match_form=match_form,
        current_sort=sort_by,
        player_count=current_player_count,
        max_players_limit=MAX_PLAYERS
    )

@app.route('/generate_matches', methods=['POST'])
def generate_matches():
    form = MatchForm()
    players = Player.query.all()
    max_courts = len(players) // 4
    form.num_courts.choices = [(i, str(i)) for i in range(1, max_courts + 1)]

    if form.validate_on_submit():
        num_courts = form.num_courts.data
        match_type = form.match_type.data

        if match_type == 'skill':
            match_data = create_skill_based_matches(players, num_courts)
        elif match_type == 'mixed':
            match_data = create_mixed_gender_matches(players, num_courts)
        else: # 'random'
            match_data = create_random_matches(players, num_courts)

        if not match_data:
            flash("Not enough players to generate any courts.", "warning")
            return redirect(url_for('draft'))
        
        new_match = Match(num_courts=len(match_data)) # Create the parent Match object.
        db.session.add(new_match)
        db.session.flush() # Flush to get the ID for the new_match

        for data in match_data: # Loop through the court data and create Court and CourtPlayer records.
            court = Court(court_number=data['court'], match_id=new_match.id)
            db.session.add(court)
            db.session.flush() # Flush to get the ID for the new court

            for player in data['team1'] + data['team2']:
                db.session.add(CourtPlayer(court_id=court.id, player_id=player.id))
        db.session.commit()
        
        flash("New match generated successfully!", "success") 
        return redirect(url_for('view_match_details', match_id=new_match.id))
    
    flash("There was an error with your match request. Please try again.", "error") # Runs if form validation fails.
    return redirect(url_for('draft'))

@app.route('/history')
def match_history():
    all_matches = Match.query.order_by(Match.created_at.desc()).all()
    return render_template('match_history.html', matches=all_matches)

@app.route('/match/<int:match_id>')
def view_match_details(match_id):
    match = Match.query.get_or_404(match_id)
    player_ids_in_match = {cp.player_id for court in match.courts for cp in court.court_players}
    resting_players = [p for p in Player.query.all() if p.id not in player_ids_in_match]
    return render_template('generated_match.html', match=match, resting_players=resting_players)

@app.route('/set_winner/<int:court_id>/<int:team_number>', methods=['POST'])
def set_winner(court_id, team_number):
    court = Court.query.get_or_404(court_id)
    if court.winning_team is None:
        court.winning_team = team_number
        db.session.commit()
        flash(f'Team {team_number} declared winner for Court {court.court_number}!', 'success')
    else:
        flash('A winner has already been declared for this court.', 'warning')
    return redirect(url_for('view_match_details', match_id=court.match_id))

@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    flash(f'Player "{player.name}" has been deleted.', 'info')
    return redirect(url_for('draft'))

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template("/error-templates/500.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("/error-templates/404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("/error-templates/405.html")
