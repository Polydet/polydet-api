from flask import jsonify
from werkzeug.exceptions import NotFound

from polyglot_api import app


@app.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify(error='Not found'), error.code
