MONGO_PASS=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
MONGO_USER=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
#MONGO_HOST=dana-monzondb:32717
MONGODB_HOST=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}'):32717


export MONGODB_PASSWORD=$MONGO_PASS
export MONGODB_USERNAME=$MONGO_USER
export MONGODB_URL=mongodb://$MONGODB_HOST
