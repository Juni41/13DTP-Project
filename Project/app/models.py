from app import db

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    court_players = db.relationship('CourtPlayer', back_populates='player')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_courts = db.Column(db.Integer, nullable=False)

    # Each match has many courts
    courts = db.relationship('Court', back_populates='match', cascade='all, delete-orphan')

class Court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    court_number = db.Column(db.Integer, nullable=False) 
    # Link to Match
    match = db.relationship('Match', back_populates='courts')
    # Each court has many players
    court_players = db.relationship('CourtPlayer', back_populates='court', cascade='all, delete-orphan')

class CourtPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('court.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

    # Link to Court
    court = db.relationship('Court', back_populates='court_players')
    # Link to Player
    player = db.relationship('Player', back_populates='court_players')
