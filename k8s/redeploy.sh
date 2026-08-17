#!/bin/bash

# Permite re-desplegar los servicios en caso de cambios en los yaml.
# Si se cambia la imagen de mongodb, hay que escalar a 0 primero y luego escalar a 1
# Este script tiene como parametros que componentes ha redesplegar

COMPONENTS="mongodb mongo-express api dashboard cronjob"
if [ $# -gt 0 ]; then
    COMPONENTS="$@"
fi


for comp in $COMPONENTS;
do
    
case $comp in
    mongodb)
        echo "mongodb"
         kubectl -n news-crawler scale deploy mongodb --replicas=0
         kubectl -n news-crawler apply -f 00_mongo_db.yaml
         ;;    
    mongo-express)
        echo "mongo-express"
        kubectl -n news-crawler apply -f 01_mongo_express.yaml
        ;;
    api)
        echo "api"
        kubectl -n news-crawler apply -f 02_api.yaml
        ;;
    dashboard)
        echo "dashboard"
        kubectl -n news-crawler apply -f 03_dashboard.yaml
        ;;
    cronjob)
        echo "cronjob"
        kubectl -n news-crawler apply -f 04_cronjob.yaml
        ;;
    *)
        echo "Usage: $0 [mongodb|mongo-express|api|dashboard|cronjob]"
        exit 1
        ;;
esac 
done
