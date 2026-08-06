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