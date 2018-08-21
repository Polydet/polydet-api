import os
import tempfile
import requests

from flask import jsonify, make_response, render_template, request
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

from polyglot_api import app
from polyglot_api.analysis import Analysis


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def post_index():
    if 'file[]' not in request.files:
        return render_template('index.html'), 400
    files = request.files.getlist('file[]')
    results = []
    for file in files:
        if file.filename == '':
            return render_template('index.html'), 400
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        results.append(Analysis(file.filename, path))
        os.remove(path)
    return render_template('index.html', results=results)


@app.route('/api/analysis', methods=['POST'])
@cross_origin()
def api_analyse():
    if 'file[]' not in request.files and 'file_url' not in request.form:
        return make_response(jsonify({'error': 'No input file'}), 400)
    files = request.files.getlist('file[]')
    results = []
    for file in files:
        if file.filename == '':
            return make_response(jsonify({'error': 'File without a name'}), 400)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        results.append(Analysis(file.filename, path))
        os.remove(path)
    urls = request.form.getlist('file_url')
    for url in urls:
        try:
            r = requests.get(url, stream=True)
        except Exception:
            return make_response(jsonify({'error': 'File download failed'}), 400)
        if r.status_code != 200:
            return make_response(jsonify({'error': 'File download failed'}), 400)
        with tempfile.NamedTemporaryFile(dir=app.config['UPLOAD_FOLDER']) as file:
            for chunk in r.iter_content(chunk_size=4096):
                file.write(chunk)
            file.flush()
            results.append(Analysis(url, file.name))
    return jsonify([{
        'filename': result.filename,
        'elapsedTime': result.elapsed_time / 1000,
        'status': 'dangerous' if result.is_dangerous else 'suspicious' if result.is_suspicious else 'normal',
        'entries': [{
            'ext': entry.ext,
            'suspiciousChunks': [{'offset': chunk[0], 'length': chunk[1]} for chunk in entry.level.suspicious_chunks],
            'libmagic': entry.ext in result.magic_scan_results,
            'trid': result.trid_scan_results.get(entry.ext, False) / 100,
        } for entry in result]
    } for result in results])


app.jinja_env.globals['repository_url'] = 'https://git.cs.kent.ac.uk/hljl2/polyglot-detector'
