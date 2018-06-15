import logging
import os

from flask import Flask

formatter = logging.Formatter('%(name)-12s %(levelname)-8s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def prepare_upload_folder(folder):
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass


app = Flask(__name__)
app.config.from_object('config')


prepare_upload_folder(app.config['UPLOAD_FOLDER'])

import polyglot_api.index
