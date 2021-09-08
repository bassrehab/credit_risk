# Created by Subhadip Mitra <dev@subhadipmitra.com>
import logging
import os
import traceback
import sys

from flask import Flask

from src.build_dataset import BuildDataset

app = Flask(__name__)

@app.route('/datagen/')
def hello_world():
    return 'Hello World from DataGen Service'

@app.route('/datagen/build-dataset')
def build_dataset():
    print("GCP_key" + os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    try:
        bd = BuildDataset()
        bd.process()
        return 'Processing Succeeded!'
    except Exception as e:
        logging.error(traceback.format_exc())
        return 'Processing Failed'


if __name__ == '__main__':
    from waitress import serve

    serve(app, host=os.environ["SERVER_HOSTNAME"]
          , port=int(os.environ["SERVER_PORT"]))