import os

from flask import Flask


def prepare_upload_folder(folder):
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass


app = Flask(__name__)
app.config.from_object('config')


prepare_upload_folder(app.config['UPLOAD_FOLDER'])

import polyglot_api.index
