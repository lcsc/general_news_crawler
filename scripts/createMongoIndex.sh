#!/bin/bash

CCAA="aragon cantabria catalunya galicia navarra rioja asturias baleares castillaleon ceutamelilla madrid valencia andalucia canarias castillamancha extremadura murcia pvasco"

TAG=$1

MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
MONGO_HOST=dana-monzondb:32717
#MONGO_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'):32717

MSH="mongosh"
MSH_CON="mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}/general_news --authenticationDatabase=admin"

#echo "MDB_CON: $MDB_CON"


$MSH $MSH_CON -eval "db.bCubeCategory.createIndex({'ccaa':1,'short_name':1})"

$MSH $MSH_CON -eval "db.NewsArticles.createIndex({'np_ccaa':1,'np_name':1})"
$MSH $MSH_CON -eval "db.NewsArticles.createIndex({'np_ccaa':1,'np_name':1,'article_id':1})"
$MSH $MSH_CON -eval "db.NewsArticles.createIndex({'date':1})"

$MSH $MSH_CON -eval "db.NewsPapers.createIndex({'ccaa':1})"
$MSH $MSH_CON -eval "db.NewsPapers.createIndex({'ccaa':1,'provincia':1})"

for ca in $CCAA;
do
    echo "creating index for $ca "
    
    q="{\"ccaa\":\"$ca\"}"
    q_np="{\"np_ccaa\":\"$ca\"}"
    #set -x
    $MSH $MSH_CON -eval "db.data_${ca}.createIndex({'path':1,'group':1})" 
    #set +x

done
