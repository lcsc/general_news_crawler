#!/bin/sh

docker compose stop news_api news_dashboard
docker compose rm news_api news_dashboard

docker rmi general_news_crawler_api general_news_crawler_dashboard
docker compose build
docker compose create news_api news_dashboard
docker compose start news_api news_dashboard

