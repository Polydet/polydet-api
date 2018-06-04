import os

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/polyglots'

def prepare_upload_folder():
    try:
        os.mkdir(UPLOAD_FOLDER)
    except FileExistsError:
        pass

prepare_upload_folder()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000  # 100Mo

@app.route('/')
def hello_world():
    return 'Hello, World!!!'

@app.route('/analysis', methods=['POST'])
def analyse():
    if 'file' not in request.files:
        return jsonify(error='Missing file named "file"'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error='Missing filename'), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify([]), 400
