FROM mirror.lcsc.csic.es/lcsc/python-base:3.12.3 

WORKDIR /app
COPY general_news_crawler /app

RUN ls -la
RUN poetry install 
RUN pip install -e /app

CMD ["uvicorn","--host","0.0.0.0","--port", "5000","--forwarded-allow-ips","*", "news_api.main:app"]


