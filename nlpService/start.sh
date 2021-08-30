echo "The current working directory: $PWD"
export CURRENT_WORKING_DIR=$PWD
export GOOGLE_APPLICATION_CREDENTIALS=$CURRENT_WORKING_DIR/gcp-key.json
echo "Fetched GCP credentials from: $GOOGLE_APPLICATION_CREDENTIALS"

export FLASK_APP='nlp-service'
export FLASK_ENV='production'
export SERVER_HOSTNAME='0.0.0.0'
export SERVER_PORT=8080

echo "Server IP: $SERVER_HOSTNAME, Server Port: $SERVER_PORT"
chmod a+x app.py
python app.py