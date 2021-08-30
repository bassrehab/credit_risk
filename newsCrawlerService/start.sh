export REDIS_HOSTNAME='localhost'
export REDIS_PORT='6379'

export FLASK_APP='news-crawlerservice'
export FLASK_ENV='production'
export SERVER_HOSTNAME='0.0.0.0'
export SERVER_PORT=9090


chmod a+x app.py
python app.py