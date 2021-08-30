import logging
import os
import traceback

from flask import Flask, request, jsonify

from nlp_sentiment_classifier import *

app = Flask(__name__)


@app.route('/nlp/')
def hello_world():
    return 'Hello from NLP Service.'


@app.route('/nlp/classify-sentiment-absa', methods=['POST'])
def classify_sentiment_absa():
    try:
        if request.method == 'POST':
            absa = SentimentClassifier()
            content = request.json
            logging.info(content)
            res = absa.getABSA(content['text_content']
                         , content['anchor_entity']
                         , content['text_id']
                         , content['text_type']
                         , content['entity_similarity_threshold']
                         , content['salience_threshold'])

            return jsonify(res)
    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({'status': 'failed'})
        # return jsonify(isError= False, message= "Success", statusCode= 200, data= data), 200

@app.route('/nlp/classify-sentiment', methods=['POST'])
def classify_sentiment():
    try:
        if request.method == 'POST':
            content = request.json
            logging.info(content)
            absa = SentimentClassifier()
            return jsonify(absa.getSATransformers(content['text_content'], content['text_id']))


    except Exception as e:
        logging.error(traceback.format_exc())
        return jsonify({'status': 'failed'})


if __name__ == '__main__':
    from waitress import serve

    serve(app, host=os.environ["SERVER_HOSTNAME"]
          , port=int(os.environ["SERVER_PORT"]))
