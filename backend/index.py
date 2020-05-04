import os
import logging

from flask import Flask

if os.environ.get("ENV") == "dev":
  from flask_cors import CORS
else:
  CORS = None

from flask_cors import CORS
from .connect4.game import Connect4
from .blueprint_constructor import new_blueprint

app = Flask(__name__)
connect4_app = new_blueprint("connect4", Connect4)
app.register_blueprint(connect4_app, url_prefix="/connect4")

if CORS:
  CORS(app)

@app.before_first_request
def setup_logging():
    """Sets up the system for appropriate logging."""
    if not app.debug:
        app.logger.setLevel(logging.INFO)