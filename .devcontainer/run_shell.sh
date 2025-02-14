#!/bin/sh

docker run -it --rm \
    -v $(pwd):/work \
    -w /work \
    --network=general_news_crawler_default \
    --add-host=host.docker.internal:host-gateway \
    -p 5001:5000 \
    mcr.microsoft.com/devcontainers/python:3.12 \
    zsh