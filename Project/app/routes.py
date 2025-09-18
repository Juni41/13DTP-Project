from flask import render_template, flash, request, redirect, url_for
from app import app, db
from app.models import Player, Match, Court, CourtPlayer
from app.forms import PlayerForm, MatchForm
from sqlalchemy import case
from app.matchmaking import create_skill_based_matches, create_random_matches, create_mixed_gender_matches

@app.route('/')
def layout():
    return render_template("home.html")

@app.route('/draft', methods=['GET', 'POST'])
def draft():
    player_form = PlayerForm()
    match_form = MatchForm()
    MAX_PLAYERS = app.config['MAX_PLAYERS']
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
    players_in_draft = Player.query.all()
    max_courts = len(players_in_draft) // 4
    form.num_courts.choices = [(i, str(i)) for i in range(1, max_courts + 1)]

    if form.validate_on_submit():
        num_courts = form.num_courts.data
        match_type = form.match_type.data

        if match_type == 'mixed':
            # Check the roster for the minimum number of players of each gender.
            males_count = Player.query.filter_by(gender='male').count()
            females_count = Player.query.filter_by(gender='female').count()
            
            # Need at least 2 of each to form one court of mixed teams.
            if males_count < 2 or females_count < 2:
                flash("Cannot generate mixed match. You need at least 2 male and 2 female players.", "error")
                return redirect(url_for('draft'))
            
        if match_type == 'skill':
            match_data = create_skill_based_matches(players_in_draft, num_courts)
        elif match_type == 'mixed':
            match_data = create_mixed_gender_matches(players_in_draft, num_courts)
        else: # 'random'
            match_data = create_random_matches(players_in_draft, num_courts)

        if not match_data:
            flash("Not enough players to generate any courts.", "warning")
            return redirect(url_for('draft'))


        player_ids_in_match = {p_obj.id for d in match_data for p_obj in d['team1']+d['team2']}
        
        # Find the Player objects for those who are on rest.
        resting_players_objects = [p for p in players_in_draft if p.id not in player_ids_in_match]

        # Get their names.
        resting_players_names = [p.name for p in resting_players_objects]
        
        # Join the names into a single string to be saved in the database.
        resting_players_str = ",".join(resting_players_names)
        
        player_ids_str = ",".join([str(p.id) for p in players_in_draft])
        new_match = Match(
            num_courts=len(match_data),
            match_type=match_type,
            player_ids_snapshot=player_ids_str,
            resting_players_snapshot=resting_players_str
        )
        new_match.roster = players_in_draft
        db.session.add(new_match)
        db.session.flush()

        for data in match_data:
            court = Court(court_number=data['court'], match_id=new_match.id)
            db.session.add(court)
            db.session.flush()

            for player_object in data['team1'] + data['team2']:
                court_player_link = CourtPlayer(
                    court_id=court.id,
                    player_id=player_object.id,
                    player_name=player_object.name
                )
                db.session.add(court_player_link)
        db.session.commit()
        
        flash("New match generated successfully!", "success")
        try:
            history_limit = app.config['MAX_MATCHES']
            all_matches = Match.query.order_by(Match.created_at.asc()).all()

            if len(all_matches) > history_limit:
                matches_to_delete_count = len(all_matches) - history_limit
                
                # Get the specific match objects to be deleted from the start of the list.
                matches_to_delete = all_matches[:matches_to_delete_count]
                print(f"INFO: Match history limit ({history_limit}) exceeded. Deleting {len(matches_to_delete)} oldest match(es).")
                
                for old_match in matches_to_delete:
                    db.session.delete(old_match)
                    
                db.session.commit()
                flash(f"{len(matches_to_delete)} oldest match(es) pruned from history.", "info")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Could not prune match history. Error: {e}")
            flash("Could not prune old match history.", "error")
        return redirect(url_for('view_match_details', match_id=new_match.id))

    flash("There was an error with your match request.", "error")
    return redirect(url_for('draft'))

@app.route('/regenerate_match/<int:previous_match_id>', methods=['POST'])
def regenerate_match(previous_match_id):
    previous_match = Match.query.get_or_404(previous_match_id)
    players_for_rematch = previous_match.roster
    
    # Get the other settings from the old match.
    num_courts = previous_match.num_courts
    match_type = previous_match.match_type

    # Check if there are still enough players to create the match.
    if len(players_for_rematch) < num_courts * 4:
        flash("Cannot regenerate: not enough of the original players still exist.", "warning")
        return redirect(url_for('view_match_details', match_id=previous_match_id))
    
    if match_type == 'skill':
        match_data = create_skill_based_matches(players_for_rematch, num_courts)
    elif match_type == 'mixed':
        match_data = create_mixed_gender_matches(players_for_rematch, num_courts)
    else: # 'random'
        match_data = create_random_matches(players_for_rematch, num_courts)

    if not match_data:
        flash("Could not regenerate pairings with the original settings.", "warning")
        return redirect(url_for('view_match_details', match_id=previous_match_id))

    # Create and save the new match with the new results and snapshots.
    player_ids_in_match = {p_obj.id for d in match_data for p_obj in d['team1']+d['team2']}
    resting_players = [p.name for p in players_for_rematch if p.id not in player_ids_in_match]

    new_match = Match(
        num_courts=len(match_data),
        match_type=match_type,
        player_ids_snapshot=",".join([str(p.id) for p in players_for_rematch]),
        resting_players_snapshot=",".join(resting_players)
    )
    new_match.roster = players_for_rematch # Save the same historical roster for the new match.
    db.session.add(new_match)
    db.session.flush()

    # Loop through and save the new court and player link data.
    for data in match_data:
        court = Court(court_number=data['court'], match_id=new_match.id)
        db.session.add(court)
        db.session.flush()
        for player_object in data['team1'] + data['team2']:
            court_player_link = CourtPlayer(
                court_id=court.id,
                player_id=player_object.id,
                player_name=player_object.name
            )
            db.session.add(court_player_link)

    db.session.commit()

    flash("Match was regenerated with a full reshuffle!", "success")
    return redirect(url_for('view_match_details', match_id=new_match.id))

@app.route('/history')
def match_history():
    all_matches = Match.query.order_by(Match.created_at.desc()).all()
    return render_template('match_history.html', matches=all_matches)

@app.route('/match/<int:match_id>')
def view_match_details(match_id):
    match = Match.query.get_or_404(match_id)
    resting_players_names = []
    if match.resting_players_snapshot:
        resting_players_names = match.resting_players_snapshot.split(',')
    return render_template('generated_match.html', match=match, resting_players=resting_players_names)

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
