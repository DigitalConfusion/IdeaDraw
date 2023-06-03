# Import required libaries.
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Length, DataRequired


# Create a definition for a JoinForm used for submiting data when joining a lobby
# This form contains the username, the lobby code to join, and the submit button
class JoinForm(FlaskForm):
    username = StringField(
        label="Username", validators=[Length(min=3, max=12), DataRequired()]
    )
    lobby = StringField(
        label="Lobby code", validators=[Length(min=6, max=6), DataRequired()]
    )
    submit = SubmitField(label="Play")


# Create a definition for a PlayForm used for submiting data when creating a lobby
# Contains the username, round length selector and the submit button
class PlayForm(FlaskForm):
    username = StringField(
        label="Username", validators=[Length(min=3, max=12), DataRequired()]
    )
    round_length = SelectField(
        label="Round length",
        choices=["1 minute", "2 minutes", "3 minutes"],
        default="2 minutes",
    )
    submit = SubmitField(label="Play")
