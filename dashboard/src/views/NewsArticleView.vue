<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <Panel v-if="np" :header="np.name" toggleable>
      <p class="m-0">
        Mostrando Articulos de {{ router.params.ccaa }} -
        {{ router.params.short_name }}
      </p>
      <p class="m-0">
        <YearTimeLine :data="np.backfill" /></p
    ></Panel>

    <Toolbar>
      <template #center>
        <FloatLabel variant="on">
          <DatePicker
            v-model="dates"
            selectionMode="range"
            :manualInput="false"
            showButtonBar
            inputId="dateRange"
            show-icon
          />
          <label for="dateRange">Rango Fechas</label>
        </FloatLabel>

        <MultiSelect
          v-model="selectedCategories"
          :options="categories"
          optionLabel="cat_name"
          filter
          placeholder="Categorias"
          class="w-full md:w-80"
          :max-selected-labels="3"
        />
        <Button
          icon="pi pi-search"
          severity="primary"
          text
          @click="loadFromServer(true)"
        />
      </template>
    </Toolbar>

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
      <template #item-headline="item">
        <a :href="item.article_url" target="_blank">{{ item.article_headline }}</a>
      </template>

      <template #item-categories="item">
        <span v-if="item.categories">{{ item.categories.join(",") }}</span>
      </template>
    </EasyDataTable>
  </div>
</template>

<style></style>

<script setup lang="ts">
import { inject, onMounted, ref, watch } from "vue";
import type { Header, ServerOptions } from "vue3-easy-data-table";

import {
  type NewsPaper,
  type NewsArticle,
  type BcubeCategory,
} from "../newsclient/hey";
import { useRoute } from "vue-router";
import { NewsClient } from "@/newsclient/newsclient";
import {
  DatePicker,
  Panel,
  Toolbar,
  Button,
  FloatLabel,
  MultiSelect,
} from "primevue";
import type { NewsSearch } from "@/model/selectors";

import { default as YearTimeLine } from "@/components/icons/YearTimeLine.vue";
const mainSize = inject("mainSize");

const data = ref<NewsArticle[]>([]);

const headers: Header[] = [
  { text: "Articulo", value: "headline" },
  { text: "fecha", value: "date", sortable: true },
  { text: "Categorias", value: "categories" },
];

const router = useRoute();

const np = ref<NewsPaper | undefined>();

const ccaa: string = router.params.ccaa;
const short_name: string = router.params.short_name;
const client = NewsClient.instance;

onMounted(async () => {
  np.value = await client.getNewsPaper(ccaa, short_name);
  categories.value = await client.listCategories(ccaa, short_name);
  loadFromServer(true);
});

const loading = ref(false);
const serverItemsLength = ref(0);
const serverOptions = ref<NewsSearch>({
  page: 1,
  rowsPerPage: 15,
  sortBy: undefined,
  sortType: undefined,
});

const dates = ref();
const selectedCategories = ref();
const categories = ref<BcubeCategory[]>();

const loadFromServer = async (reset: boolean) => {
  if (loading.value) return;
  if (reset) {
    serverOptions.value.page = 1;
  }
  loading.value = true;
  const query = serverOptions.value;
  if (dates.value && dates.value.length > 0) {
    query.notBefore = dates.value[0];
    query.notAfter = dates.value[1];
  } else {
    query.notBefore = undefined;
    query.notAfter = undefined;
  }

  if (selectedCategories.value && selectedCategories.value.length > 0) {
    query.category = selectedCategories.value.map((c) => c.cat_name);
  } else {
    query.category = undefined;
  }
  try {
    let res = await client.listArticles(ccaa, short_name, query);

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
  }
  loading.value = false;
};

watch(
  serverOptions,
  (value) => {
    loadFromServer(false);
  },
  { deep: true }
);
</script>
