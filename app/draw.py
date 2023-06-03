# Import required libaries.
from flask import Blueprint, render_template, url_for, session
from flask_socketio import join_room

# Import required functions from modules.
from app.db import get_db
from app.functions import get_drawing_stage

# Import the SocketIO connection from app.
from app import socketio

# Create the blueprint
bp = Blueprint("draw", __name__, url_prefix="/")


# This function renders the "draw.html" template for the "/draw" route.
@bp.route("/draw", methods=["GET", "POST"])
def draw():
    return render_template("game/draw.html")

# This function renders the "paint.html" template for the "/paint" route.
@bp.route("/paint", methods=["GET", "POST"])
def paint():
    return render_template("game/paint.html")


# Connect the player to SocketIO room to be able to send messages to the entire lobby.
# Sends a callback to the client of the current drawing stage (1, 2, 3)
# to be able to differentiate between different stages of the game.
@socketio.on("join_drawing_room")
def join_drawing_room():
    join_room(session["lobby_code"])
    return get_drawing_stage()


# This function saves the submited drawing to the DB.
@socketio.on("submit_drawing")
def submit_drawing(player_id, drawing_base64):
    # Create a DB connection.
    db = get_db()

    db.execute(
        "INSERT INTO drawings (drawing_stage, lobby_code, player_id, drawing_base64) VALUES (?, ?, ?, ?)",
        (get_drawing_stage(), session["lobby_code"], player_id, drawing_base64),
    )
    # Commit the changes to the DB.
    db.commit()


# This function checks if all players in a lobby have submitted their drawings.
@socketio.on("check_submited_drawings")
def check_submited_drawings():
    # Create a DB connection.
    db = get_db()

    # Get the submitted drawing count.
    drawing_count = db.execute(
        "SELECT COUNT(*) FROM drawings WHERE lobby_code == ? AND drawing_stage == ?",
        (session["lobby_code"], get_drawing_stage()),
    ).fetchone()[0]
    
    # Get the player count in the lobby.
    player_count = db.execute(
        "SELECT player_count FROM lobbies WHERE lobby_code == ?",
        (session["lobby_code"],),
    ).fetchone()["player_count"]

    if drawing_count == player_count:
        return True
    return False


# This function redirects the user to the vote page when the request to redirect is received.
@socketio.on("redirect_to_vote")
def redirect_to_vote():
    socketio.emit("redirect", url_for("vote.vote"), to=session["lobby_code"])


# This function retrieves a drawing from the DB for the next round of the game.
@socketio.on("get_drawing_for_next_round")
def get_drawing_for_next_round():
    # Create a DB connection.
    db = get_db()

    # Get all certain round drawings from DB with the player drawing excluded.
    drawing = db.execute(
        "SELECT drawing_base64 FROM drawings WHERE lobby_code == ? AND drawing_stage == ? ORDER BY average_vote DESC",
        (session["lobby_code"], get_drawing_stage() - 1),
    ).fetchone()["drawing_base64"]
    
    return drawing


# This function retrieves the prompt from the DB, which is associated with the specific lobby code.
@socketio.on("get_prompt")
def get_prompt():
    # Create a DB connection.
    db = get_db()
    
    prompt = db.execute(
        "SELECT prompt FROM lobbies WHERE lobby_code == ?", (session["lobby_code"],)
    ).fetchone()["prompt"]
    
    return prompt
