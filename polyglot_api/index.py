import os

from flask import render_template, request
from polyglot_detector import PolyglotLevel
from werkzeug.utils import secure_filename

from polyglot_api import app
from polyglot_api.analysis import Analysis


@app.template_filter('polyglot_level')
def display_polyglot_level(level: PolyglotLevel):
    res = []
    if level & PolyglotLevel.INVALID:
        res.append('invalid')
    if level & PolyglotLevel.GARBAGE_AT_BEGINNING:
        res.append('suspicious data at the beginning')
    if level & PolyglotLevel.GARBAGE_IN_MIDDLE:
        res.append('suspicious data at the middle')
    if level & PolyglotLevel.GARBAGE_AT_END:
        res.append('suspicious data at the end')
    return ', '.join(res) if res else 'is valid'


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
    results = Analysis(file.filename, path)
    os.remove(path)
    return render_template('index.html', results=results)
