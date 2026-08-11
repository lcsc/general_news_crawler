#!/bin/sh

MONGO_USER=root
MONGO_PASSWORD=example

if [ -e .env ]; then
    . ./.env
fi

echo "/run/user/$(id -u)/podman/podman.sock"
if [ -e /run/user/$(id -u)/podman/podman.sock  ]; then
    echo "Podman detected"
    DOCKER_SOCK="/run/user/$(id -u)/podman/podman.sock"
else
    echo "Docker detected"
    DOCKER_SOCK="/var/run/docker.sock:"
fi

read -p "User for mongodb [$MONGO_USER]:" db_user
if [ -z $db_user ]; then
    echo "Using Previous"
else
    MONGO_USER="$db_user"
fi

read -p "Password for mongodb [*****]:" db_pass
if [ -z $db_pass ]; then
    echo "Using Previous"
else
    MONGO_PASSWORD="$db_pass"
fi

echo "DOCKER_SOCK=$DOCKER_SOCK"  >.env
echo "MONGO_USER=$MONGO_USER" >> .env
echo "MONGO_PASSWORD=$MONGO_PASSWORD" >> .env