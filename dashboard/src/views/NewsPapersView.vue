<script setup lang="ts">
import { inject, onMounted, ref, watch, type Ref } from "vue";

import { default as NewsPaperSelector } from "../components/NewsPaperSelector.vue";
import { default as YearTimeLine } from "@/components/icons/YearTimeLine.vue";

import type { Header, Item, ServerOptions } from "vue3-easy-data-table";
import type { NewsPaperSelectorModel } from "@/model/selectors";

import { NewsClient } from "../newsclient/newsclient";
import type { NewsPaper } from "@/newsclient/hey";

const data = ref<NewsPaper[]>([]);
const loading = ref(false);
const serverItemsLength = ref(0);
const serverOptions = ref<ServerOptions>({
  page: 1,
  rowsPerPage: 15,
  sortBy: undefined,
  sortType: undefined,
});

let state: NewsPaperSelectorModel = {
  ca: undefined,
  provincia: undefined,
  engine: undefined,
  sub_engine: undefined,
};

const headers: Header[] = [
  { text: "CCAA", value: "ccaa", sortable: true },
  { text: "Provincia", value: "provincia", sortable: true },
  { text: "Short_Name", value: "short_name" },
  { text: "Nombre", value: "name" },
  { text: "Acciones", value: "actions" },
  { text: "Url", value: "real_url" },
  { text: "Motor", value: "engine.engine", sortable: true },
  { text: "Version", value: "engine.sub_engine", sortable: true },
  { text: "Nº Articulos", value: "n_articulos", sortable: true },
  { text: "Primer Mes", value: "first_month", sortable: true },
  { text: "Primer Articulo", value: "first_article", sortable: true },
  { text: "Ultima Comprobacion", value: "last_check", sortable: true },
  { text: "2024", value: "backfill", width: 150 },
];

const mainSize = inject("mainSize");
const npState = inject<Ref<NewsPaperSelectorModel>>("npSelectorState");

async function update(state: NewsPaperSelectorModel, reset: boolean) {
  if (loading.value) return;
  if (reset) {
    serverOptions.value.page = 1;
  }
  loading.value = true;
  let client = NewsClient.instance;
  try {
    let res = await client.listNewsPapers(state, serverOptions.value);
    if (res.results) {
      serverItemsLength.value = res.results;
      data.value = res.items ? res.items : [];
    } else {
      serverItemsLength.value = 0;
      data.value = [];
    }
  } catch (e) {
    console.error(e);
    serverItemsLength.value = 0;
    data.value = [];
    serverOptions.value.page = 1;
  }
  loading.value = false;
}

async function onStateChanged(_state: NewsPaperSelectorModel) {
  state = _state;
  await update(state, true);
}

onMounted(async () => {
  if (npState) state = npState.value;
  update(state, true);
});

watch(
  serverOptions,
  (value) => {
    update(state, false);
  },
  { deep: true }
);
</script>

<script lang="ts"></script>
<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <NewsPaperSelector
      @stateChannged="(state:NewsPaperSelectorModel)=> onStateChanged(state)"
    />

    <EasyDataTable
      :headers="headers"
      :items="data"
      alternating
      v-model:server-options="serverOptions"
      :server-items-length="serverItemsLength"
      :loading="loading"
      :rowsPerPage="15"
      :rowsItems="[5, 10, 15, 20, 25]"
      buttons-pagination
    >
      <template #item-real_url="item">
        <a :href="item.real_url" target="_blank">{{ item.real_url }}</a>
      </template>
      <template #item-n_articulos="item">
        <RouterLink
          :to="{
            name: 'news',
            params: { ccaa: item.ccaa, short_name: item.short_name },
          }"
          >{{ item.n_articulos }}</RouterLink
        >
      </template>
      <template #item-actions="item">
        <RouterLink
          :to="{
            name: 'news',
            params: { ccaa: item.ccaa, short_name: item.short_name },
          }"
          ><i class="pi pi-file" title="Abrir listado de Articulos"></i
        ></RouterLink>
        <RouterLink
          :to="{
            name: 'categories',
            params: { ccaa: item.ccaa, short_name: item.short_name },
          }"
          ><i class="pi pi-tag" title="Abrir listado de Categorias"></i
        ></RouterLink>
      </template>
      <template #item-backfill="item">
        <YearTimeLine v-if="item.backfill" :data="item.backfill" year="2024" short />
      </template>
    </EasyDataTable>
  </div>
</template>

<style></style>
