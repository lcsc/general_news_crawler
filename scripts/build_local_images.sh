#!/bin/sh

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
REGISTRY="mirror.lcsc.csic.es/lcsc"

docker build -t ${REGISTRY}/general_news_crawler_api:${TIMESTAMP} -t ${REGISTRY}/general_news_crawler_api:latest .
docker build -t ${REGISTRY}/general_news_crawler_dashboard:${TIMESTAMP} -t ${REGISTRY}/general_news_crawler_dashboard:latest ./dashboard

