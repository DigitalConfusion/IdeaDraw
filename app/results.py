# Import required libaries.
from flask import Blueprint, render_template, session
from flask_socketio import join_room

# Import required functions from modules.
from app.db import get_db

# Import the SocketIO connection from app.
from app import socketio


# Create the blueprint
bp = Blueprint("results", __name__, url_prefix="/")


# This function renders the "results.html" template for the "/results" route.
@bp.route("/results", methods=["GET", "POST"])
def results():
    return render_template("game/results.html")


# Connect the player to SocketIO room to be able to send messages to the entire lobby.
@socketio.on("join_results_room")
def join_results_room():
    join_room(session["lobby_code"])


# This function retrieves the final winning drawings and info about them
# from the DB and returns them as a dictionary.
@socketio.on("get_final_results")
def get_final_results():
    # Create a DB connection.
    db = get_db()

    # Dictonary to store the gathered data.
    results = {}
    
    # Get the drawing ids that won each drawing round from the DB.
    winning_ids = db.execute(
        "SELECT first_drawing_win_id, second_drawing_win_id, third_drawing_win_id FROM lobbies WHERE lobby_code == ?",
        (session["lobby_code"],),
    ).fetchone()

    # Get the winning drawings and their info from the DB
    drawings = db.execute(
        "SELECT drawing_stage, player_id, average_vote, drawing_base64 FROM drawings WHERE lobby_code == ? AND drawing_id == ? OR drawing_id == ? OR drawing_id == ?",
        (
            session["lobby_code"],
            winning_ids["first_drawing_win_id"],
            winning_ids["second_drawing_win_id"],
            winning_ids["third_drawing_win_id"],
        ),
    ).fetchall()

    # For each drawing, find the username of the player of the winning drawings
    for drawing in drawings:
        # Get the author's username
        author = db.execute(
            "SELECT username FROM players WHERE player_id == ?", (drawing["player_id"],)
        ).fetchone()["username"]

        # Add the info about the drawing to the dictonary
        if drawing["drawing_stage"] == 1:
            results["first_drawing_image"] = drawing["drawing_base64"]
            results["first_drawing_average_vote"] = drawing["average_vote"]
            results["first_drawing_author"] = author
        elif drawing["drawing_stage"] == 2:
            results["second_drawing_image"] = drawing["drawing_base64"]
            results["second_drawing_average_vote"] = drawing["average_vote"]
            results["second_drawing_author"] = author
        elif drawing["drawing_stage"] == 3:
            results["third_drawing_image"] = drawing["drawing_base64"]
            results["third_drawing_average_vote"] = drawing["average_vote"]
            results["third_drawing_author"] = author

    # Return the dictonary with the gathered data
    return results
