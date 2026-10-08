# General News Crawler

Pasos para hacer una captura :


```bash
  
  list          <- Descarga lista de periodicos
  detect        <- Detecta el Motor 
  extract       <- Extrae informacion basica (Categorias y fechas)
  backfillnews  <- Busca URLs de noticias
  downloadnews  <- Descarga las noticias

  classifyheadlines <- Procesa los titulares para saber si son Sequia o no

```

docker run -it --rm -e https_proxy=socks5h://172.17.0.1:1080 python:3.11 bash


## Inicilizacion Dev Python

```bash
python3 -m venv --upgrade-deps .venv
. .venv/bin/activate
poetry -V
```
> *CHECK POETRY VERSION*, requires 2.5.1 or newer. 

If you need to install or update poetry:

```bash
pip3 install poetry
poetry self update
deactivate
. .venv/bin/activate
poetry -V

```
When ready:

```bash 
# . .venv/bin/activate (ensure active)
poetry -C general_news_crawler install 
pip install -e general_news_crawler
```

## UBUNTU NOTE

Si poetry falla y se cuelga sin hacer nada aparente, hay que deshabilitar el keyring

export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring

## Cliente MongoDB

### Instalación
```bash
sudo apt install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.3 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.3.list
sudo apt-get update
sudo apt-get install -y mongodb-mongosh mongodb-database-tools
```

### Acceso a la base de datos

```bash
mongosh "mongodb://root:example@localhost/" --authenticationDatabase=admin --eval "show dbs"
```