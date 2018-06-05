import os

from flask import render_template, request
from polyglot_detector import PolyglotLevel, scan
from werkzeug.utils import secure_filename

from polyglot_api import app


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def post_index():
    if 'file' not in request.files:
        return 400
    file = request.files['file']
    if file.filename == '':
        return 400
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    results = scan(path, use_magic=True)
    os.remove(path)
    return render_template('index.html', results=__flat_embedded(results))


def __flat_embedded(results: {str: PolyglotLevel}):
    """Return the results with flatten embedded formats.
    For example:
    >>> results = {'zip': PolyglotLevel.VALID|PolyglotLevel.GARBAGE_AT_BEGINNING.with_embedded("jar")}
    >>> __flat_embedded(results)
    {'zip': <PolyglotLevel.VALID|GARBAGE_AT_BEGINNING: 5 []>, 'jar': <PolyglotLevel.VALID|GARBAGE_AT_BEGINNING: 5 []>}
    """
    new_result = {}
    for type, level in results.items():
        level_without_embedded = level & ~PolyglotLevel.EMBED
        new_result[type] = level_without_embedded
        for embedded in level.embedded:
            new_result[embedded] = new_result.get(embedded, PolyglotLevel(0)) | level_without_embedded  # TODO Use PolyglotLevel.None
    return new_result
