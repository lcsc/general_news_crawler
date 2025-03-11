#!/bin/bash

CCAA="aragon cantabria catalunya galicia navarra rioja asturias baleares castillaleon ceutamelilla madrid valencia andalucia canarias castillamancha extremadura murcia pvasco"

TAG=$1

MSH="compose exec mongodb mongosh"
MSH_CON="mongodb://root:example@localhost/general_news --authenticationDatabase=admin"

MDB="compose exec -T mongodb mongoimport"
MDB_CON="--uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news"

if [ $# -lt 1 ]; then
    echo "At least require the tag to load"
    echo "$0 <TAG> [CCAA] [CCAA ...]"
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
    set -x
    docker $MSH $MSH_CON -eval "db.NewsPapers.deleteMany(${q})"
    docker $MSH $MSH_CON -eval "db.bCubeCategory.deleteMany(${q})"
    docker $MSH $MSH_CON -eval "db.bCubePIMetaData.deleteMany(${q})"
    docker $MSH $MSH_CON -eval "db.NewsArticles.deleteMany(${q_np})"
    
    cat data/${ca}/NewsPapers.json | docker $MDB $MDB_CON -cNewsPapers
    cat data/${ca}/bCubeCategory.json | docker $MDB $MDB_CON -cbCubeCategory
    cat data/${ca}/bCubePIMetaData.json | docker $MDB $MDB_CON -cbCubePIMetaData
    cat data/${ca}/NewsArticles.json | docker $MDB $MDB_CON -cNewsArticles
    
    set +x
done
