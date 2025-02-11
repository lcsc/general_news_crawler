import "mdb-vue-ui-kit/css/mdb.min.css";
import "./assets/main.css";
import "vue3-easy-data-table/dist/style.css";

import Vue3EasyDataTable from "vue3-easy-data-table";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.component("EasyDataTable", Vue3EasyDataTable);
app.use(router);

app.mount("#app");
