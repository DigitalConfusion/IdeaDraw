# Import required libaries.
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
import json
import random
import string

# Import required functions from modules
from app.db import get_db
from app.forms import JoinForm, PlayForm
from app.prompts import get_prompt


# Create the blueprint
bp = Blueprint("home", __name__, url_prefix="/")


# This function handles the creation of a new game lobby and player in the database,
# and redirects the user to the lobby page.
@bp.route("/", methods=["GET", "POST"])
@bp.route("/play", methods=["GET", "POST"])
def play():
    # Create the form
    play_form = PlayForm(request.form)

    # Create a DB connection
    db = get_db()

    # Checks if the request method is POST and if the form data submitted by
    # the user passes all the validation checks defined in the `PlayForm` class.
    if request.method == "POST" and play_form.validate_on_submit():
        # Clear any session data from the previous games
        session.clear()
        
        # Get data from the submitted form
        username = play_form.username.data
        round_length_seconds = play_form.round_length.data[0] * 60
        
        # Get a random prompt to assign this lobby
        prompt = get_prompt()

        # Generate a random lobby code
        lobby_code = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        # If this lobby code already exists, generate a new code until a free one is found
        while (
            db.execute(
                "SELECT * FROM lobbies WHERE lobby_code == ?", (lobby_code,)
            ).fetchone()
            is not None
        ):
            lobby_code = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=6)
            )

        # Add the player to DB and get the player id
        db.execute("INSERT INTO players (username) VALUES (?)", (username,))
        player_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Add lobby code and player id to the personal session data for later use
        session["lobby_code"] = lobby_code
        session["player_id"] = player_id

        # Create a players list to save in the DB
        players = {
            "player_1_id": player_id,
            "player_2_id": None,
            "player_3_id": None,
            "player_4_id": None,
            "player_5_id": None,
            "player_6_id": None,
            "player_7_id": None,
            "player_8_id": None,
        }
        
        # Convert the dictonary to JSON format
        players = json.dumps(players)
        
        # Add a new lobby to the DB
        db.execute(
            "INSERT INTO lobbies (lobby_code, round_length_seconds, prompt, players) VALUES (?, ?, ?, ?)",
            (lobby_code, round_length_seconds, prompt, players),
        )
        
        # Commit the changes to the DB
        db.commit()

        # Redirect the user to the lobby screen
        return redirect(url_for("lobby.lobby"))

    # Render the home screen, where the user can create a new lobby
    return render_template("home/play.html", play_form=play_form)


# This function handles the joining of an existing game lobby,
# and redirects the user to the lobby page after a succesful join.
@bp.route("/join", methods=["GET", "POST"])
def join():
    # Create the form
    join_form = JoinForm(request.form)

    # Create a DB connection
    db = get_db()

    # Checks if the request method is POST and if the form data submitted by
    # the user passes all the validation checks defined in the `JoinForm` class.
    if request.method == "POST" and join_form.validate_on_submit():
        # Clear any session data from the previous games
        session.clear()
        
        # Get data from the submitted form
        username = join_form.username.data
        lobby_code = join_form.lobby.data

        # Check if entered lobby code exists
        if (
            db.execute(
                "SELECT * FROM lobbies WHERE lobby_code == ?", (lobby_code,)
            ).fetchone()
            is not None
        ):
            # Check if there is a free spot in the lobby
            if (
                db.execute(
                    "SELECT player_count FROM lobbies WHERE lobby_code == ?",
                    (lobby_code,),
                ).fetchone()["player_count"]
                <= 7
            ):
                # Lobby exists and there is a free spot, so add player to database to get player id
                db.execute("INSERT INTO players (username) VALUES (?)", (username,))
                player_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

                # Add player to lobby players
                # Get the players in the lobby from the DB
                players = db.execute(
                    "SELECT players FROM lobbies WHERE lobby_code == ?", (lobby_code,)
                ).fetchone()["players"]
                
                # Convert it to JSON format
                players = json.loads(players)
                
                # Add player to the free spot in the lobby
                for player, id in players.items():
                    if id == None:
                        players[player] = player_id
                        break
                    
                # Add lobby code and player id to the personal session data for later use
                session["lobby_code"] = lobby_code
                session["player_id"] = player_id

                # Update the players in lobby
                db.execute(
                    "UPDATE lobbies SET players = ? WHERE lobby_code == ?",
                    (
                        json.dumps(players),
                        lobby_code,
                    ),
                )
                # Update the player count in the lobby, in the DB
                db.execute(
                    "UPDATE lobbies SET player_count = ? WHERE lobby_code == ?",
                    (
                        db.execute(
                            "SELECT player_count FROM lobbies WHERE lobby_code = ?",
                            (lobby_code,),
                        ).fetchone()["player_count"]
                        + 1,
                        lobby_code,
                    ),
                )
                
                # Commit the changes to the DB
                db.commit()
                
            # If there is no free spot in the lobby, show warning
            else:
                flash(
                    "Lobby is full! Please try to join another lobby!",
                    category="danger",
                )
                # Rerender the page, to clear the entered data
                return render_template("home/join.html", join_form=join_form)
            
            # If player joined succesfully, redirect the user to the lobby
            return redirect(url_for("lobby.lobby"))
        # If the entered lobby code is invalid, show a warning
        else:
            flash(
                "Lobby code is not valid! Try to join again or create your own lobby!",
                category="danger",
            )
    # Render the home screen, where the user can join a lobby
    return render_template("home/join.html", join_form=join_form)
