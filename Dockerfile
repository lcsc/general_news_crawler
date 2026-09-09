FROM mirror.lcsc.csic.es/lcsc/python-base:3.12.3 

WORKDIR /app
COPY poetry.lock /app/
COPY pyproject.toml /app/

RUN poetry install 
COPY news_crawler /app/news_crawler
COPY news_api /app/news_api
RUN pip install -e /app

CMD ["uvicorn","--host","0.0.0.0","--port", "5000","--forwarded-allow-ips","*", "news_api.main:app"]


