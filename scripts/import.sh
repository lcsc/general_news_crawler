cat data/NewsPapers.json | docker compose exec -T mongodb mongoimport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cNewsPapers --drop
cat data/bCubeCategory.json | docker compose exec -T mongodb mongoimport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cbCubeCategory --drop
cat data/bCubePIMetaData.json | docker compose exec -T mongodb mongoimport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cbCubePIMetaData --drop
cat data/piStats.json | docker compose exec -T mongodb mongoimport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cpiStats --drop
cat data/NewsArticles.json | docker compose exec -T mongodb mongoimport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cNewsArticles --drop
