# Import the required libaries.
from flask import Blueprint, render_template, url_for, session
from flask_socketio import join_room

# Import required functions from modules
from app.db import get_db

# Import the SocketIO connection from app.
from app import socketio

# Create the blueprint
bp = Blueprint("lobby", __name__, url_prefix="/")


# This function renders the "lobby.html" template for the "/lobby" route.
@bp.route("/lobby", methods=["GET", "POST"])
def lobby():
    return render_template("home/lobby.html")


# Connect the player to SocketIO room to be able to send messages to the entire lobby.
# Sends a callback to the client with data containing list of players, lobby code and the player's id
@socketio.on("connect_to_lobby")
def connect_to_lobby():
    # Dictonary to store the gathered data
    session_data = {}

    # Send a message to the rest of the players in the lobby, that a new player has joined
    socketio.emit("player_joined", get_players(), to=session["lobby_code"])

    # Join the SocketIO room
    join_room(session["lobby_code"])

    # Get the data and store it in the session data dictonary
    lobby_data = get_lobby_data()
    session_data["players"] = lobby_data["players"]
    session_data["lobby_code"] = session["lobby_code"]
    session_data["player_id"] = session["player_id"]

    # Return the gathered data
    return session_data


# Returns data about the lobby
# Currently only returns the player list
@socketio.on("get_lobby_data")
def get_lobby_data():
    # Create a DB connection
    db = get_db()

    lobby_data = db.execute(
        "SELECT players FROM lobbies WHERE lobby_code == ?", (session["lobby_code"],)
    ).fetchone()

    return lobby_data


# Return just the player list in the lobby
@socketio.on("get_players")
def get_players():
    # Create a DB connection
    db = get_db()

    players = db.execute(
        "SELECT players FROM lobbies WHERE lobby_code == ?", (session["lobby_code"],)
    ).fetchone()["players"]

    return players


# Returns the username of the player with the given id
@socketio.on("get_username")
def get_username(player_id):
    # Create a DB connection
    db = get_db()

    username = db.execute(
        "SELECT username FROM players WHERE player_id == ?", (player_id,)
    ).fetchone()["username"]

    return username


# Return the amount of players in the current lobby
@socketio.on("get_player_count")
def get_player_count():
    # Create a DB connection
    db = get_db()

    player_count = db.execute(
        "SELECT player_count FROM lobbies WHERE lobby_code == ?",
        (session["lobby_code"],),
    ).fetchone()["player_count"]

    return player_count


# This function emits a socket event to all players in the lobby
# to redirect all the users to the first round of the game.
@socketio.on("begin_first_round")
def redirect_to_first_round():
    socketio.emit(
        "redirect_to_first_round", url_for("draw.draw"), to=session["lobby_code"]
    )


# This function emits a socket event to all players in the lobby
# to warn that a player is ready to begin the game.
@socketio.on("player_is_ready")
def player_is_ready(player_id):
    socketio.emit("ready_player_id", get_username(player_id), to=session["lobby_code"])


# This function emits a socket event to all players in the lobby
# to warn that a player is not ready anymore to begin the game.
@socketio.on("player_not_ready")
def player_not_ready(player_id):
    socketio.emit(
        "not_ready_player_id", get_username(player_id), to=session["lobby_code"]
    )
