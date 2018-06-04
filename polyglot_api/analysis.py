import os

from flask import request, jsonify
from polyglot_detector import PolyglotLevel, scan
from werkzeug.utils import secure_filename

from polyglot_api import app


@app.route('/analysis', methods=['POST'])
def post_analyse():
    if 'file' not in request.files:
        return jsonify(error='Missing file named "file"'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error='Missing filename'), 400
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    result = scan(path)
    os.remove(path)
    return jsonify(format_result(result)), 400


def format_result(result: {str: PolyglotLevel}) -> {str: {}}:
    return {key: format_polyglot_level(level) for (key, level) in result.items()}


def format_polyglot_level(level: PolyglotLevel) -> {str: {}}:
    res = {}
    if PolyglotLevel.VALID & level:
        res['valid'] = True
    if PolyglotLevel.INVALID & level:
        res['invalid'] = True
    if PolyglotLevel.GARBAGE_AT_BEGINNING & level:
        res['beginning'] = True
    if PolyglotLevel.GARBAGE_IN_MIDDLE & level:
        res['middle'] = True
    if PolyglotLevel.GARBAGE_AT_END & level:
        res['end'] = True
    if PolyglotLevel.EMBED & level:
        res['embed'] = list(level.embedded)
    return res
