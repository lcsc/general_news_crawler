#!/bin/bash

MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
MONGODB_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')

docker build -t general_news_crawler_api:dev .
docker run --rm -p5000:5000 \
  -e MONGODB_USERNAME=$MONGO_USER \
  -e MONGODB_PASSWORD=$MONGO_PASS \
  -e MONGODB_URL=mongodb://$MONGODB_HOST:32717 \
  --add-host $MONGODB_HOST:host-gateway \
  general_news_crawler_api:dev 
