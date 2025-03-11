container_id=$(docker compose run -d --rm -v $(pwd)/scripts:/app/scripts -v$(pwd)/log:/app/log news_api $@)
docker logs -f $container_id