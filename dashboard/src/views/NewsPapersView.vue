<script setup lang="ts">
import { inject, onMounted, ref } from "vue";

import { default as NewsPaperSelector } from "../components/NewsPaperSelector.vue";

import type { Header, Item } from "vue3-easy-data-table";
import type { NewsPaperSelectorModel } from "@/model/selectors";

import { NewsClient } from "../newsclient/newsclient";
import type { NewsPaper } from "@/newsclient/hey";

const data = ref<NewsPaper[]>([]);

let state: NewsPaperSelectorModel = {
  ca: undefined,
  provincia: undefined,
  engine: "bCube",
  sub_engine: undefined,
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

const mainSize = inject("mainSize");

async function update(state: NewsPaperSelectorModel) {
  let client = NewsClient.instance;
  let response = await client.listNewsPapers(state);

  data.value = response;
}

async function onStateChanged(_state: NewsPaperSelectorModel) {
  state = _state;
  await update(state);
}

onMounted(async () => {
  update(state);
});
</script>

<script lang="ts"></script>
<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <NewsPaperSelector
      @stateChannged="(state:NewsPaperSelectorModel)=> onStateChanged(state)"
    />

    <EasyDataTable :headers="headers" :items="data" alternating>
      <template #item-real_url="item">
        <a :href="item.real_url" target="_blank">{{ item.real_url }}</a>
      </template>
    </EasyDataTable>
  </div>
</template>

<style></style>
