#!/bin/bash

REGISTRY="mirror.lcsc.csic.es/lcsc"

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

docker build -t ${REGISTRY}/python-base:${TIMESTAMP} -t ${REGISTRY}/python-base:3.12.3 -f Dockerfile.base .
docker push ${REGISTRY}/python-base:${TIMESTAMP}
docker push ${REGISTRY}/python-base:3.12.3