# Created by Subhadip Mitra <dev@subhadipmitra.com>
import logging
import os
import time
import traceback

from flask import Flask, request, jsonify

from newsCrawlerService.src.config.stages import Stages
from newsCrawlerService.src.utilities import utils
from newsCrawlerService.src.utilities.redis_utils import RedisUtils
from src.search_news import SearchNewsURLs

app = Flask(__name__)

# initialize Redis Connection
r = RedisUtils()


@app.route('/hello')
def index():
    return "Hello, World!"


@app.route("/crawler/job/submit", methods=['POST'])
def submit_job():
    status = {}
    _id = utils.get_uuid()  # generate an ID for this job

    try:
        if request.method == 'POST':
            content = request.json
            logging.info(content)
            symbol = content['symbol']
            after = content['after']
            before = content['before']

            # Used to determine the /current or /history
            is_current = content['current'] == 'true' or content['current'] == 'True'

            news = SearchNewsURLs(symbol, after, before, is_current)
            result = news.process()  # update stage

            conn = r.getConnection()

            stage = Stages.STAGE_1.value
            stage["stage_start_time"] = time.time()
            stage["stage_status"] = "INITIATED"

            status = {
                "job_id": _id,
                "job_status": "ACCEPTED",
                "current_stage": Stages.STAGE_1.name,
                "errors": []
            }
            conn.hset(_id, "JOB_STATUS", status)
            conn.hset(_id, "STAGE_1", stage)
            conn.close()

    except Exception as e:
        err = traceback.format_exc()
        logging.error(traceback.format_exc())
        status = {
            "job_id": "NONE",
            "job_status": "FAILED_TO_INITIATE",
            "current_stage": Stages.STAGE_0,
            "errors": [str(err)]
        }
    return jsonify(status)


@app.route("/crawler/job/status/<string:job_id>", methods=['GET'])
def get_job_status(job_id):
    conn = r.getConnection()
    status = conn.hgetall(job_id)

    return jsonify(status)


if __name__ == '__main__':
    from waitress import serve

    serve(app, host=os.environ["SERVER_HOSTNAME"]
          , port=int(os.environ["SERVER_PORT"]))

    # TODO: https://python-rq.org/
