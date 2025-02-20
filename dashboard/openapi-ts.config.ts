import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "apis/news_client.json",
  output: "src/newsclient/hey",
  plugins: ["@hey-api/client-axios"],
});
