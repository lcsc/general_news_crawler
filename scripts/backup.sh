#!/bin/bash
CCAA="aragon cantabria catalunya galicia navarra rioja asturias baleares castillaleon ceutamelilla madrid valencia andalucia canarias castillamancha extremadura murcia pvasco"

TAG=$(date +'%Y%m%d')

MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
MONGO_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
MONGO_PORT=32717
h=$(hostname -f)
if [ "$h" != "$MONGO_HOST" ]; then
    MONGO_HOST=dana-$MONGO_HOST
fi

MDB="mongoexport"
MDB_CON="--uri=mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}:${MONGO_PORT}/general_news --authenticationDatabase=admin"


if [ $# -gt 0 ]; then
    CCAA="$@"
fi


for ca in $CCAA;
do
    echo "backup $ca"
    
    mkdir -p backup/$TAG
    mkdir -p data/$ca
    q="{\"ccaa\":\"$ca\"}"
    q_np="{\"np_ccaa\":\"$ca\"}"
    #set -x
    $MDB  $MDB_CON -cNewsPapers -q $q > data/$ca/NewsPapers.json
    $MDB  $MDB_CON -cbCubeCategory -q $q > data/$ca/bCubeCategory.json
    $MDB  $MDB_CON -cbCubePIMetaData -q $q > data/$ca/bCubePIMetaData.json
    $MDB  $MDB_CON -cNewsArticles -q $q_np > data/$ca/NewsArticles.json
    $MDB  $MDB_CON -cdata_${ca} > data/$ca/data_${ca}.json
    #set +x
    tar -cvzf backup/$TAG/data_${ca}_${TAG}.tar.gz data/$ca
    rm -r data/$ca
done

exit 1 