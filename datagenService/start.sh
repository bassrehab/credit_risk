#!/bin/sh
echo "The current working directory: $PWD"
export CURRENT_WORKING_DIR=$PWD
export GOOGLE_APPLICATION_CREDENTIALS=$CURRENT_WORKING_DIR/gcp-key.json
echo "Fetched GCP credentials from: $GOOGLE_APPLICATION_CREDENTIALS"

# clean up
rm data/*


export FLASK_APP='datagen-service'
export FLASK_ENV='production'
export SERVER_HOSTNAME='0.0.0.0'
export SERVER_PORT=7070


chmod a+x app.py
python app.py