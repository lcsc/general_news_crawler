#!/bin/bash
CCAA="andalucia aragon"

TAG=$(date +'%Y%m%d')

MDB="compose exec mongodb mongoexport"
MDB_CON="--uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news"

for ca in $CCAA;
do
    echo "backup $ca"
    
    mkdir -p backup/$TAG
    q="{\"ccaa\":\"$ca\"}"
    q_np="{\"np_ccaa\":\"$ca\"}"
    #set -x
    docker $MDB  $MDB_CON -cNewsPapers -q $q > data/$ca/NewsPapers.json
    docker $MDB  $MDB_CON -cbCubeCategory -q $q > data/$ca/bCubeCategory.json
    docker $MDB  $MDB_CON -cbCubePIMetaData -q $q > data/$ca/bCubePIMetaData.json
    docker $MDB  $MDB_CON -cNewsArticles -q $q_np > data/$ca/NewsArticles.json
    #set +x
    tar -cvzf backup/$TAG/data_$ca_$TAG.tar.gz data/$ca

done

exit 1 