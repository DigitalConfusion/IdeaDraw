# Import required libaries.
from flask_socketio import join_room
from flask import Blueprint, render_template, url_for, session

# Import required functions from modules.
from app.db import get_db
from app.functions import get_drawing_stage

# Import the SocketIO connection from app.
from app import socketio

# Create the blueprint
bp = Blueprint("vote", __name__, url_prefix="/")


# This function renders the "voting.html" template for the "/voting" route.
@bp.route("/vote", methods=["GET", "POST"])
def vote():
    return render_template("game/voting.html")


# Connect the player to SocketIO room to be able to send messages to the entire lobby.
# Sends a callback to the client of the current drawing stage (1, 2, 3)
# to be able to differentiate between different voting stages.
@socketio.on("join_voting_room")
def connect_to_lobby():
    join_room(session["lobby_code"])
    return get_drawing_stage()


# This function retrieves all drawings for a certain round from a database, excluding the drawing of
# the user requesting the drawings, and returns them as a dictionary of image IDs and base64-encoded image data.
@socketio.on("get_drawings_for_voting")
def get_drawings_for_voting(player_id):
    # Dictonary to store the image data
    images = {}

    # Create a DB connection.
    db = get_db()

    # Get all certain round drawings from database with the player not included
    drawings = db.execute(
        "SELECT drawing_id, drawing_base64 FROM drawings WHERE lobby_code == ? AND player_id != ? AND drawing_stage = ?",
        (
            session["lobby_code"],
            player_id,
            get_drawing_stage(),
        ),
    ).fetchall()

    # Add each drawing to the dictonary with the drawing id as the key and the base64
    # data as the value
    for drawing in drawings:
        images[drawing["drawing_id"]] = drawing["drawing_base64"]

    # Return the images
    return images


# When player has voted on a certain sketch, record this event to DB
@socketio.on("submit_vote")
def submit_vote(drawing_id, vote):
    # Create a DB connection.
    db = get_db()

    # Get current drawing vote data from the DB
    current_voting_data = db.execute(
        "SELECT vote_total, voters FROM drawings WHERE drawing_id == ?", (drawing_id,)
    ).fetchone()

    # Add player's vote to drawings total vote sum in the DB
    db.execute(
        "UPDATE drawings SET vote_total = ? WHERE drawing_id = ?",
        ((current_voting_data["vote_total"] + vote), drawing_id),
    )

    # Increment the voter count by 1 in the DB
    db.execute(
        "UPDATE drawings SET voters = ? WHERE drawing_id = ?",
        (
            (current_voting_data["voters"] + 1),
            drawing_id,
        ),
    )

    # Commit the changes to the DB.
    db.commit()


# This function checks if all players in the lobby have voted in the current stage.
@socketio.on("check_if_all_players_have_voted")
def check_if_all_players_have_voted():
    # Create a DB connection.
    db = get_db()

    # Get the player count in the lobby.
    player_count = db.execute(
        "SELECT player_count FROM lobbies WHERE lobby_code == ?",
        (session["lobby_code"],),
    ).fetchone()["player_count"]

    # Get the amount of players that have voted.
    voters = db.execute(
        "SELECT voters FROM drawings WHERE lobby_code == ? AND drawing_stage == ?",
        (session["lobby_code"], get_drawing_stage()),
    ).fetchone()["voters"]

    if voters == player_count - 1:
        return True
    return False


# This function updates the database with the average vote for each drawing, selects the winning
# drawing for the current drawing stage, updates the lobby with the winning drawing ID and the next
# drawing stage, and emits a redirect event to the appropriate page for the next drawing stage.
@socketio.on("redirect_to_next_round")
def redirect_to_next_round():
    # Create a DB connection.
    db = get_db()

    # Get the current drawing stage
    drawing_stage = get_drawing_stage()

    # Get info about all drawings that were made in the current round
    drawing_data = db.execute(
        "SELECT vote_total, voters, drawing_id FROM drawings WHERE lobby_code == ? AND drawing_stage == ?",
        (session["lobby_code"], drawing_stage),
    ).fetchall()

    # Calculate and set each drawing's average vote value
    for row in drawing_data:
        avg_vote = round(row["vote_total"] / row["voters"], 4)
        db.execute(
            "UPDATE drawings SET average_vote = ? WHERE drawing_id == ?",
            (avg_vote, row["drawing_id"]),
        )

    # This code retrieves the id of the drawing with the highest average
    # vote for the current lobby and drawing stage
    drawing_win_id = db.execute(
        "SELECT drawing_id FROM drawings WHERE lobby_code == ? AND drawing_stage == ? ORDER BY average_vote DESC",
        (session["lobby_code"], drawing_stage),
    ).fetchone()["drawing_id"]

    # Update the "lobbies" table in the database with the ID of the winning drawing
    # depending on the current game stage
    if drawing_stage == 1:
        db.execute(
            "UPDATE lobbies SET first_drawing_win_id = ? WHERE lobby_code == ?",
            (drawing_win_id, session["lobby_code"]),
        )
    elif drawing_stage == 2:
        db.execute(
            "UPDATE lobbies SET second_drawing_win_id = ? WHERE lobby_code == ?",
            (drawing_win_id, session["lobby_code"]),
        )
    elif drawing_stage == 3:
        db.execute(
            "UPDATE lobbies SET third_drawing_win_id = ? WHERE lobby_code == ?",
            (drawing_win_id, session["lobby_code"]),
        )

    # If the drawing stage hasn't reached the final stage,
    # increment the drawing stage to show that next stage has begun
    if drawing_stage != 3:
        db.execute(
            "UPDATE lobbies SET drawing_stage = ? WHERE lobby_code == ?",
            (drawing_stage + 1, session["lobby_code"]),
        )

    # Commit the changes to the DB.
    db.commit()

    # Emit a SocketIO event to redirect the players in the current lobby to the
    # appropriate page for the next drawing stage based on the current drawing stage
    if drawing_stage == 1:
        socketio.emit("redirect", url_for("draw.draw"), to=session["lobby_code"])
    elif drawing_stage == 2:
        socketio.emit("redirect", url_for("draw.paint"), to=session["lobby_code"])
    else:
        socketio.emit("redirect", url_for("results.results"), to=session["lobby_code"])
