# Import required libaries.
from flask import current_app, g
import sqlite3
import click


# This function returns a connection to a SQLite3 database stored in the Flask application context.
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


# This function initializes the database by executing the SQL schema script.
def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


# This function creates a command to create a database and output a message confirming its creation,
# by typing "flask init-db" into the terminal
@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database created!")


# This function associates the close_db and init_db function with their relative tasks.
def init_app(app):
    app.cli.add_command(init_db_command)
