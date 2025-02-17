<script setup lang="ts">
import { onMounted, ref } from "vue";

import { default as NewsPaperSelector } from "../components/NewsPaperSelector.vue";
import { MDBContainer } from "mdb-vue-ui-kit";
import axios from "axios";
import type { Header, Item } from "vue3-easy-data-table";
import type { NewsPaperSelectorModel } from "@/model/selectors";

const data = ref([]);

let state: NewsPaperSelectorModel = {
  ca: null,
  provincia: null,
  engine: "bCube",
  sub_engine: null,
};

const headers: Header[] = [
  { text: "CCAA", value: "ccaa", sortable: true },
  { text: "Short_name", value: "short_name" },
  { text: "Provincia", value: "provincia", sortable: true },
  { text: "Nombre", value: "name" },
  { text: "Url", value: "real_url" },
  { text: "Motor", value: "engine.engine", sortable: true },
  { text: "Version", value: "engine.sub_engine", sortable: true },
  { text: "Nº Articulos", value: "n_articulos", sortable: true },
  { text: "Primer Mes", value: "first_month", sortable: true },
  { text: "Primer Articulo", value: "first_article", sortable: true },
  { text: "Ultima Comprobacion", value: "last_check", sortable: true },
];

async function onStateChanged(_state: NewsPaperSelectorModel) {
  state = _state;
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
}

async function onCcaaChanged(ca: string) {
  state.ca = ca;
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
}

async function onProvinciaChanged(prov: string) {
  state.provincia = prov;
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
}
async function onEngineChanged(engine: string) {
  state.engine = engine;
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
}
async function onSubEngineChanged(sub_engine: string) {
  state.sub_engine = sub_engine;
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
}

onMounted(async () => {
  let response = await axios.get(buildUrl(state));
  data.value = response.data;
});
</script>

<script lang="ts">
function buildUrl(state: any) {
  function add_param(url: string, param: string, value: string) {
    if (value != null) {
      if (url.indexOf("?") == -1) {
        url += "?";
      } else {
        url += "&";
      }
      url += param + "=" + value;
    }
    return url;
  }

  let url = "/news/api/np/";
  if (state.ca != null) {
    url += state.ca + "/";
  }
  url = add_param(url, "engine", state.engine);
  url = add_param(url, "sub_engine", state.sub_engine);

  return url;
}
</script>
<template>
  <MDBContainer fluid>
    <NewsPaperSelector
      @setCcaa="(ca:string) => onCcaaChanged(ca)"
      @setProvincia="(engine:string) => onProvinciaChanged(engine)"
      @setEngine="(engine:string) => onEngineChanged(engine)"
      @setSubEngine="(engine:string) => onSubEngineChanged(engine)"
      @stateChannged="(state:NewsPaperSelectorModel)=> onStateChanged(state)"
    />
  </MDBContainer>
  <MDBContainer fluid>
    <EasyDataTable :headers="headers" :items="data" alternating>
      <template #item-real_url="item">
        <a :href="item.real_url" target="_blank">{{ item.real_url }}</a>
      </template>
    </EasyDataTable>
  </MDBContainer>
</template>
