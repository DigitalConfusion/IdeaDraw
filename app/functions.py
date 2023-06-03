# Import required libaries.
from flask import session
from app.db import get_db


# Get the current drawing stage of the lobby
def get_drawing_stage():
    # Create a DB connection
    db = get_db()

    drawing_stage = db.execute(
        "SELECT drawing_stage FROM lobbies WHERE lobby_code == ?",
        (session["lobby_code"],),
    ).fetchone()["drawing_stage"]

    return drawing_stage

