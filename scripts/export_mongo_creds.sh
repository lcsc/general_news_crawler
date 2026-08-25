MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
MONGO_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
MONGO_PORT=32717
#MONGO_HOST=dana-monzondb:32717

h=$(hostname -f)

if [ "$h" != "$MONGO_HOST" ]; then
    export MONGO_HOST=dana-$MONGO_HOST

fi


export MONGODB_PASSWORD=$MONGO_PASS
export MONGODB_USERNAME=$MONGO_USER
export MONGO_HOST=$MONGO_HOST
export MONGO_PORT=$MONGO_PORT
export MONGODB_URL=mongodb://$MONGODB_USERNAME:$MONGODB_PASSWORD@$MONGO_HOST:$MONGO_PORT/general_news?authSource=admin
