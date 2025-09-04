from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length

class PlayerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=30)])
    skill = SelectField('Skill Level', choices=[
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ], validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Add Player')

class MatchForm(FlaskForm):
    num_courts = SelectField('Number of Courts', coerce=int, validators=[DataRequired()])
    
    match_type = RadioField(
        'Matchmaking Type', 
        choices=[
            ('skill', 'Balanced by Skill (Top players on same court)'),
            ('mixed', 'Balanced by Skill & Gender (Prioritizes Mixed Teams)'),
            ('random', 'Purely Random')
        ],
        default='skill', # Set a sensible default
        validators=[DataRequired()]
    )
    submit = SubmitField('Generate Matches')
