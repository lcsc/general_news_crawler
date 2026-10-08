FROM mirror.lcsc.csic.es/lcsc/python-base:3.12.3 

WORKDIR /app
COPY general_news_crawler/poetry.lock /app/
COPY general_news_crawler/pyproject.toml /app/

RUN poetry install 
COPY general_news_crawler/general_news_crawler /app/general_news_crawler
COPY general_news_crawler/news_api /app/news_api
RUN pip install -e /app

CMD ["uvicorn","--host","0.0.0.0","--port", "5000","--forwarded-allow-ips","*", "news_api.main:app"]


