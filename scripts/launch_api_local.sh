#!/bin/bash

MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
MONGODB_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'):32717

MONGODB_PASSWORD=$MONGO_PASS
MONGODB_USERNAME=$MONGO_USER
MONGODB_URL=mongodb://$MONGODB_HOST

uvicorn --host 0.0.0.0 --port 5000 --forwarded-allow-ips "*" news_api.main:app