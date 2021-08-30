#!/usr/bin/env bash
cd "$PWD/redis-setup" || exit

gcloud init

gcloud container clusters create k8s-lab1 --disk-size 10 --zone asia-east1-a --machine-type n1-standard-2 --num-nodes 3 --scopes compute-rw

kubectl config get-contexts

kubectl apply -f redis-statefulset.yaml

kubectl apply -f redis-svc.yaml

kubectl get pvc

kubectl describe pods redis-cluster-0

kubectl apply -f redis-svc.yaml

IP_ADDRS=$(kubectl get pods -l app=redis-cluster -o jsonpath='{range.items[*]}{.status.podIP}:6379')

# Get hostnames/ip as IP_1, ..IP_5 from above output

kubectl exec -it redis-cluster-0 -- redis-cli --cluster create "${IP_ADDRS}" --cluster-replicas 1

kubectl exec -it redis-cluster-0 -- redis-cli cluster info

kubectl apply -f app.yaml