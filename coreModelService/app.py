# Created by Subhadip Mitra <dev@subhadipmitra.com>
import logging
import os
import traceback
import sys

from flask import Flask

app = Flask(__name__)

@app.route('/core/')
def hello_world():
    return 'Hello World from Core Model Service'

@app.route('/core/score')
def score():
    print("GCP_key" + os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    try:
        pass
        return 'Processing Succeeded!'
    except Exception as e:
        logging.error(traceback.format_exc())
        return 'Processing Failed'

@app.route('/core/train')
def train():
    print("GCP_key" + os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    try:
        pass
        return 'Processing Succeeded!'
    except Exception as e:
        logging.error(traceback.format_exc())
        return 'Processing Failed'


if __name__ == '__main__':
    from waitress import serve

    serve(app, host=os.environ["SERVER_HOSTNAME"]
          , port=int(os.environ["SERVER_PORT"]))