<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <Panel v-if="np" :header="np.name" toggleable>
      <p class="m-0">
        Mostrando Articulos de {{ router.params.ccaa }} -
        {{ router.params.short_name }}
      </p>
      <p class="m-0">
        <YearTimeLine v-if="np.backfill" :data="np.backfill" showLabels year="2024" /></p
    ></Panel>
    <EasyDataTable
      :headers="headers"
      :items="data"
      alternating
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
      </template>
      <template #item-backfill="item">
        <YearTimeLine v-if="item.backfill" :data="item.backfill" year="2024" short />
      </template>
    </EasyDataTable>
  </div>
</template>

<style></style>
<script setup lang="ts">
import { inject, onMounted, ref, watch } from "vue";

import { default as NewsPaperSelector } from "../components/NewsPaperSelector.vue";
import { default as YearTimeLine } from "@/components/icons/YearTimeLine.vue";

import type { Header, Item, ServerOptions } from "vue3-easy-data-table";

import { NewsClient } from "../newsclient/newsclient";
import { useRoute } from "vue-router";
import type { NewsPaper } from "@/newsclient/hey";
import { DatePicker, Panel, Toolbar, Button, FloatLabel, MultiSelect } from "primevue";

const mainSize = inject("mainSize");

const data = ref<BcubeCategory[]>([]);
/*const loading = ref(false);
const serverItemsLength = ref(0);
const serverOptions = ref<ServerOptions>({
  page: 1,
  rowsPerPage: 15,
  sortBy: undefined,
  sortType: undefined,
});*/

const np = ref<NewsPaper | undefined>();
const categories = ref<BcubeCategory[]>([]);

const router = useRoute();
let ccaa: string;
let short_name: string;
const client = NewsClient.instance;

const headers: Header[] = [
  { text: "Nombre", value: "cat_name", sortable: true },
  { text: "Acciones", value: "actions" },
  { text: "Url", value: "cat_url" },
  { text: "Nº Articulos", value: "n_articulos", sortable: true },
  { text: "Primer Mes", value: "first_month", sortable: true },
  { text: "Primer Articulo", value: "first_article", sortable: true },
  { text: "2024", value: "backfill", width: 150 },
];

onMounted(async () => {
  ccaa = router.params.ccaa;
  short_name = router.params.short_name;

  np.value = await client.getNewsPaper(ccaa, short_name);
  data.value = await client.listCategories(ccaa, short_name);
  //  loadFromServer(true);
});
watch(router, async () => {
  ccaa = router.params.ccaa;
  short_name = router.params.short_name;

  np.value = await client.getNewsPaper(ccaa, short_name);
  data.value = await client.listCategories(ccaa, short_name);
  //  loadFromServer(true);
});
</script>
