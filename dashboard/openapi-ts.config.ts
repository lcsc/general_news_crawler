import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "apis/news_client.json",
  output: "src/newsclient/hey",
  plugins: ["@hey-api/client-axios"],
});
// curl http://localhost/news/api/openapi.json -o dashboard/apis/news_client.json
// npm run gen-client
