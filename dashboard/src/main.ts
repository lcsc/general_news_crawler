import "mdb-vue-ui-kit/css/mdb.min.css";
import "./assets/main.css";
import "vue3-easy-data-table/dist/style.css";
import "vue3-openlayers/styles.css";

import Vue3EasyDataTable from "vue3-easy-data-table";

import { createApp, ref } from "vue";
import App from "./App.vue";
import router from "./router";
import OpenLayersMap from "vue3-openlayers";

import { NewsClient } from "./newsclient/newsclient";

NewsClient.instance.getOptions();
const mainSize = ref<number>(400);

const app = createApp(App);
app.component("EasyDataTable", Vue3EasyDataTable);
app.use(router);
app.use(OpenLayersMap);
app.provide("mainSize", mainSize);

app.mount("#app");
