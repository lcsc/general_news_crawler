import "./assets/main.css";
import "vue3-easy-data-table/dist/style.css";
import "vue3-openlayers/styles.css";
import "primeicons/primeicons.css";

// eslint-ts-ignore @typescript-eslint/no-default-export
// @ts-expect-error
import Vue3EasyDataTable from "vue3-easy-data-table";

import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";

import { createApp, ref } from "vue";
import App from "./App.vue";
import router from "./router";
import OpenLayersMap from "vue3-openlayers";

import { NewsClient } from "./newsclient/newsclient";
import Ripple from "primevue/ripple";

NewsClient.instance.getOptions();
const mainSize = ref<number>(400);

const app = createApp(App);
app.component("EasyDataTable", Vue3EasyDataTable);
app.use(router);
app.use(OpenLayersMap);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});
app.directive("ripple", Ripple);

app.provide("mainSize", mainSize);

app.mount("#app");
