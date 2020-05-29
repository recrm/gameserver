import os
import logging

from flask import Flask

print(os.environ.get("REACT_APP_ENV"))

if os.environ.get("REACT_APP_ENV") == "prod":
    CORS = None
else:
    print("activating cors")
    from flask_cors import CORS

from .connect4.game import Connect4_4x4, Connect4_5x4, Connect4_5x5
from .blueprint_constructor import new_blueprint

app = Flask(__name__)

connect4_4x4_app = new_blueprint("connect4_4x4", Connect4_4x4)
app.register_blueprint(connect4_4x4_app, url_prefix="/connect4_4x4")

connect4_5x4_app = new_blueprint("connect4_5x4", Connect4_5x4)
app.register_blueprint(connect4_5x4_app, url_prefix="/connect4_5x4")

connect4_5x5_app = new_blueprint("connect4_5x5", Connect4_5x5)
app.register_blueprint(connect4_5x5_app, url_prefix="/connect4_5x5")

if CORS:
    CORS(app)

@app.before_first_request
def setup_logging():
    """Sets up the system for appropriate logging."""
    if not app.debug:
        app.logger.setLevel(logging.INFO)