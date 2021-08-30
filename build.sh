#!/usr/bin/env bash

_cwd=$PWD
# shellcheck disable=SC2155
export _GCP_PROJECT_ID="$(gcloud config get-value project -q)"
export _GCP_COMPUTE_ZONE=us-west1-a
export _GCP_COMPUTE_REGION=us-west1
export _GCP_GKE_CLUSTER_NAME=credit-risk-cluster

export _LISTENING_PORT_DATAGEN_SVC=7070
export _LISTENING_PORT_NEWS_CRAWLER_SVC=9090
export _LISTENING_PORT_NLP_SVC=8080

if [ "$1" -eq 0 ]
  then
    _RELEASE_TAG='latest'
  else
    _RELEASE_TAG=$1
fi

if [ "$2" -eq 0 ]
  then
    gcloud config set compute/zone ${_GCP_COMPUTE_ZONE}
    gcloud config set compute/region ${_GCP_COMPUTE_REGION}

    #Autopilot
    gcloud container clusters create-auto ${_GCP_GKE_CLUSTER_NAME}

    echo "Waiting for cluster to complete provisioning (4 mins).."
    sleep 3m 30s
    gcloud compute instances list
    gcloud container clusters get-credentials ${_GCP_GKE_CLUSTER_NAME} --zone ${_GCP_COMPUTE_ZONE}
fi


# Deploy Redis Cluster on GKE
if [ "$2" -eq 0 ]
  then
    chmod a+x deploy-redis.sh
    ./deploy-redis.sh
    cd "$_cwd" || exit
  else
    brew services stop redis
    redis-server /usr/local/etc/redis.conf
fi




# Build Docker Image
cd ./datagenService || exit
if [ "$2" -eq 0 ]
  then
    docker build -t gcr.io/"${_GCP_PROJECT_ID}"/svc-datagen:"$_RELEASE_TAG" .
  else
    docker build -t svc-datagen:"$_RELEASE_TAG" .
    docker run -dp ${_LISTENING_PORT_DATAGEN_SVC}:${_LISTENING_PORT_DATAGEN_SVC} svc-datagen

fi

docker images

cd "$_cwd" || exit

# Build Docker Image
cd ./newsCrawlerService || exit
if [ "$2" -eq 0 ]
  then
    docker build -t gcr.io/"${_GCP_PROJECT_ID}"/svc-news-crawler:"$_RELEASE_TAG" .
  else
    docker build -t svc-news-crawler:"$_RELEASE_TAG" .
    docker run -dp ${_LISTENING_PORT_NEWS_CRAWLER_SVC}:${_LISTENING_PORT_NEWS_CRAWLER_SVC} svc-news-crawler
fi

docker images

cd "$_cwd" || exit

# Build Docker Image
cd ./nlpService || exit
if [ "$2" -eq 0 ]
  then
    docker build -t gcr.io/"${_GCP_PROJECT_ID}"/svc-nlp:"$_RELEASE_TAG" .
  else
    docker build -t svc-nlp:"$_RELEASE_TAG" .
    docker run -dp ${_LISTENING_PORT_NLP_SVC}:${_LISTENING_PORT_NLP_SVC} svc-nlp

fi

docker images

if [ "$2" -eq 0 ]
  then
    gcloud auth configure-docker
    docker push gcr.io/"${_GCP_PROJECT_ID}"/svc-da_RELEASE_TAGen:"$_RELEASE_TAG"
    docker push gcr.io/"${_GCP_PROJECT_ID}"/svc-news-crawler:"$_RELEASE_TAG"
    docker push gcr.io/"${_GCP_PROJECT_ID}"/svc-nlp:"$_RELEASE_TAG"

#    kubectl run datagenservice --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-datagen:"$_RELEASE_TAG" --port 80
#    kubectl run newscrawlerservice --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-news-crawler:"$_RELEASE_TAG" --port 80
#    kubectl run nlpservice --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-nlp:"$_RELEASE_TAG" --port 80


    kubectl create deployment svc-datagen --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-da_RELEASE_TAGen:"$_RELEASE_TAG"
    kubectl create deployment svc-news-crawler --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-news-crawler:"$_RELEASE_TAG"
    kubectl create deployment svc-nlp --image=gcr.io/"${_GCP_PROJECT_ID}"/svc-nlp:"$_RELEASE_TAG"

    kubectl scale deployment svc-datagen --replicas=1 datagenservice
    kubectl scale deployment svc-news-crawler --replicas=2 newscrawlerservice
    kubectl scale deployment svc-nlp --replicas=2 nlpservice

    kubectl autoscale deployment svc-datagen --cpu-percent=80 --min=1 --max=2
    kubectl autoscale deployment svc-news-crawler --cpu-percent=80 --min=1 --max=5
    kubectl autoscale deployment svc-nlp --cpu-percent=80 --min=1 --max=7

    kubectl get pods

    # ClusterIP, NodePort, LoadBalancer, ExternalName, Headless

    kubectl expose deployment svc-datagen --name=datagen-service --type=ClusterIP --port 80 --target-port ${_LISTENING_PORT_DATAGEN_SVC}
    kubectl expose deployment svc-news-crawler --name=news-crawler-service --type=ClusterIP --port 80 --target-port ${_LISTENING_PORT_NEWS_CRAWLER_SVC}
    kubectl expose deployment svc-nlp --name=nlp-service --type=ClusterIP --port 80 --target-port ${_LISTENING_PORT_NLP_SVC}

    kubectl get service

fi

