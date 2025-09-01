from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange

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
    num_courts = IntegerField('Number of Courts', validators=[
        DataRequired(), NumberRange(min=1, message="need at least 1 court")
    ])
    method = SelectField('Sorting Method', choices=[
        ('random', 'Random'),
        ('skill', 'Balance by Skill'),
        ('gender', 'Balance by Gender')
    ])
    submit = SubmitField('Generate Matches')