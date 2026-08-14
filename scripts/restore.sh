#!/bin/bash

CCAA="aragon cantabria catalunya galicia navarra rioja asturias baleares castillaleon ceutamelilla madrid valencia andalucia canarias castillamancha extremadura murcia pvasco"

TAG=$1

MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
#MONGO_HOST=dana-monzondb:32717
MONGO_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'):32717

MSH="mongosh"
MSH_CON="mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}/general_news --authenticationDatabase=admin"

MDB="mongoimport"
MDB_CON="--uri=mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}/general_news --authenticationDatabase=admin"

#echo "MDB_CON: $MDB_CON"

if [ $# -lt 1 ]; then
    echo "At least require the tag to load"
    echo "$0 <TAG> [CCAA] [CCAA ...]":bash
    exit -1
fi

if [ $# -gt 1 ]; then
    CCAA="${@:2}"
fi

for ca in $CCAA;
do
    echo "restoring $ca from $TAG"
    if [ ! -f backup/${TAG}/data_${ca}_${TAG}.tar.gz ];
    then
        echo "  No hay ficheros de ${ca}"
        continue
    fi
    rm -r data/$ca
    tar -xvzf backup/${TAG}/data_${ca}_${TAG}.tar.gz

    q="{\"ccaa\":\"$ca\"}"
    q_np="{\"np_ccaa\":\"$ca\"}"
    #set -x
    $MSH $MSH_CON -eval "db.NewsPapers.deleteMany(${q})"
    $MSH $MSH_CON -eval "db.bCubeCategory.deleteMany(${q})"
    $MSH $MSH_CON -eval "db.bCubePIMetaData.deleteMany(${q})"
    $MSH $MSH_CON -eval "db.NewsArticles.deleteMany(${q_np})"
    
    cat data/${ca}/NewsPapers.json | $MDB $MDB_CON -cNewsPapers
    cat data/${ca}/bCubeCategory.json | $MDB $MDB_CON -cbCubeCategory
    cat data/${ca}/bCubePIMetaData.json | $MDB $MDB_CON -cbCubePIMetaData
    cat data/${ca}/NewsArticles.json | $MDB $MDB_CON -cNewsArticles
    cat data/${ca}/data_${ca}.json | $MDB $MDB_CON -cdata_${ca} --drop
    #set +x
    rm -r data/$ca
done
