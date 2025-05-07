from app import db

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num_courts = db.Column(db.Integer, nullable=False)
    
class Court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)

class CourtPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('court.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
