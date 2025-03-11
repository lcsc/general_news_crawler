docker compose exec mongodb mongoexport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cNewsPapers > data/NewsPapers.json
docker compose exec mongodb mongoexport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cbCubeCategory > data/bCubeCategory.json
docker compose exec mongodb mongoexport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cbCubePIMetaData > data/bCubePIMetaData.json
docker compose exec mongodb mongoexport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cpiStats > data/piStats.json
docker compose exec mongodb mongoexport --uri="mongodb://root:example@localhost/" --authenticationDatabase=admin -dgeneral_news -cNewsArticles > data/NewsArticles.json
