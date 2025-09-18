from app import db
from datetime import datetime

match_roster = db.Table('match_roster',
    db.Column('match_id', db.Integer, db.ForeignKey('match.id', ondelete="CASCADE"), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id', ondelete="CASCADE"), primary_key=True)
)

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    court_players = db.relationship('CourtPlayer', back_populates='player')

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    num_courts = db.Column(db.Integer, nullable=False)
    match_type = db.Column(db.String(20), nullable=False, default='random')
    player_ids_snapshot = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    resting_players_snapshot = db.Column(db.Text, nullable=True)
    # The relationship to Player for the historical roster snapshot.
    roster = db.relationship('Player', secondary=match_roster, lazy='subquery',
                             backref=db.backref('matches', lazy=True))
    courts = db.relationship('Court', back_populates='match', cascade='all, delete-orphan')

class Court(db.Model):
    """Represents a single court within a specific match."""
    __tablename__ = 'court'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    court_number = db.Column(db.Integer, nullable=False) 
    winning_team = db.Column(db.Integer, nullable=True)
    
    match = db.relationship('Match', back_populates='courts')
    
    # The cascade here IS correct: if a Court is deleted, all its player links should go too.
    court_players = db.relationship('CourtPlayer', back_populates='court', cascade='all, delete-orphan')

class CourtPlayer(db.Model):
    __tablename__ = 'court_player'
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('court.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id', ondelete="SET NULL"), nullable=True)
    
    # This is the snapshot of the player's name, which is now the source of truth for history.
    player_name = db.Column(db.String(100), nullable=False)
    
    court = db.relationship('Court', back_populates='court_players')
    # The relationship to Player. This will be 'None' if the player has been deleted.
    player = db.relationship('Player', back_populates='court_players')
    