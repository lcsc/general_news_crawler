# Kubernetes General News Crawler

Partimos de que ya tenemos un Cluster Kubernetes mono-nodo (Minikube o similar).

## Despliegue en K8s

### MongoDB

Para instalar MongoDB ejecutar los siguientes pasos:
```bash
password=$(tr -dc 'A-Za-z0-9=-' < /dev/urandom | head -c 10)
# echo $password
kubectl create ns news-crawler
kubectl -n news-crawler create secret generic mongodb-creds \
  --from-literal=username="admin" \
  --from-literal=password="$password" 

#kube_pass=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
#echo $kube_pass

kubectl -n news-crawler apply -f 00_mongo_db.yaml
```

Ahora probamos si podemos conectarnos a MongoDB:
```bash
mongo_pass=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.password}' | base64 -d)
mongo_user=$(kubectl -n news-crawler get secret mongodb-creds -o jsonpath='{.data.username}' | base64 -d)
mongosh "mongodb://${mongo_user}:${mongo_pass}@dana-monzondb:32717/" --authenticationDatabase=admin --eval "show dbs"
```

El ultimo componente es el mongo-express:
```bash
kubectl -n news-crawler apply -f 01_mongo_express.yaml
```

Cuando este desplegado podremos usarlo en la url "http://dana-monzondb:30080/news/mongo"

> *IMPORTANTE: "dana-monzondb" Al no usar el operador cualquier cambio (request, imagen, etc).
se debe primero "escalar a 0" y luego aplicar el yaml.
Se deja un `redeploy.sh` para facilitar el cambio.

```bash
kubectl -n news-crawler scale deploy mongodb --replicas=0
kubectl -n news-crawler apply -f 00_mongo_db.yaml
kubectl -n news-crawler scale deploy mongodb --replicas=1
```


## API
El api se despliega aplicando el siguiente archivo:
```bash
kubectl -n news-crawler apply -f 02_api.yaml
```
Lo podemos probar con "http://dana-monzondb:30080/news/api/docs"

## Dashboard
El dashboard se desplica aplcando su archivo
```bash
kubectl -n news-crawler apply -f 03_dashboard.yaml
```
Lo podemos probar con "http://dana-monzondb:30080/news/dashboard"



