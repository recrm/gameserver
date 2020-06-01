import os
import logging
from flask import Flask

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

from .connection import managers
from .blueprint_constructor import new_blueprint

app = Flask(__name__)

# Connection games
for manager in managers:
    new_app = new_blueprint(manager.__name__, manager)
    app.register_blueprint(new_app, url_prefix="/" + manager.__name__)

if CORS:
    CORS(app)

@app.before_first_request
def setup_logging():
    """Sets up the system for appropriate logging."""
    if not app.debug:
        app.logger.setLevel(logging.INFO)