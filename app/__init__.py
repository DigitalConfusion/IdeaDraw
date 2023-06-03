# Import required libaries
import os

from flask import Flask, redirect, url_for
from flask_socketio import SocketIO

# from dotenv import load_dotenv
from werkzeug.debug import DebuggedApplication

# SocketIO object
socketio = SocketIO()

# Import the required modules
from . import db, home, lobby, draw, vote, results

# Get secret key from .env file
# To make sure this app works on any machine without
# any issues, we don't use .env file, but insted we hard code the secret key.
# load_dotenv()
# SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY = "jSoNxYNvHIRBsBTp7tBeTMsVd6XWIE8Y"


# This function creates and configures a Flask application with various blueprints
# used for organizing parts of the application, initializes database and socketio communication.
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Application settings
    app.static_folder = "static"
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        # SQLite3 Database settings
        DATABASE=os.path.join(app.instance_path, "ideadraw.sqlite"),
        # This settings loads any changes to HTML/CSS files
        # Use it only during development
        # TEMPLATES_AUTO_RELOAD=True,
    )

    # Enable these settings to ease development process
    # These settings automaticly reload the Flask server, when changes to code have been detected
    # app.debug = True
    # app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Configure folder structure
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the blueprints
    app.register_blueprint(home.bp)
    app.register_blueprint(lobby.bp)
    app.register_blueprint(draw.bp)
    app.register_blueprint(vote.bp)
    app.register_blueprint(results.bp)

    # Initalize the connection to the database
    db.init_app(app)

    # Initalize the connection to SocketIO
    socketio.init_app(app)

    # Set up the root URL ("/") to direct the user to the home screen
    @app.route("/")
    def index():
        return redirect(url_for("home.play"))

    # Return the configured app
    return app


# Create the Flask application
app = create_app()
