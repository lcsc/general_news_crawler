<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <Panel v-if="np" :header="np.name" toggleable>
      <p class="m-0">
        Mostrando Articulos de {{ router.params.ccaa }} -
        {{ router.params.short_name }}
      </p>
      <p class="m-0">
        <YearTimeLine
          v-if="np.backfill"
          :data="np.backfill"
          showLabels
          year="2024"
          @clik-on="monthShortCut"
        /></p
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

      <template #item-data-actions="item">
        <div class="flex gap-1">
          <a v-if="item.raw_data" @click="() => openListData(item)"
            ><i class="pi pi-folder" title="Ver Listado"></i
          ></a>
          <a v-if="item.article_data" @click="() => openLdData(item)"
            ><i class="pi pi-eye" title="Abrir Ariculo"></i
          ></a>
        </div>
      </template>
    </EasyDataTable>
  </div>
  <ArticleViewDialog ref="articleViewDialog" />
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
import { StringType } from "ol/expr/expression";
import ArticleViewDialog from "@/components/dialogs/ArticleViewDialog.vue";

type avdType = InstanceType<typeof ArticleViewDialog>;
const articleViewDialog = ref<avdType | null>(null);

const mainSize = inject("mainSize");

const data = ref<NewsArticle[]>([]);

const headers: Header[] = [
  { text: "Articulo", value: "headline" },
  { text: "Acciones", value: "data-actions" },
  { text: "Fecha", value: "date", sortable: true },
  { text: "Categorias", value: "categories" },
];

const router = useRoute();

const np = ref<NewsPaper | undefined>();

let ccaa: string;
let short_name: string;
const client = NewsClient.instance;

function readRouter() {
  if (router.params.ccaa instanceof Array) {
    ccaa = router.params.ccaa[0];
  } else {
    ccaa = router.params.ccaa;
  }
  if (router.params.short_name instanceof Array) {
    short_name = router.params.short_name[0];
  } else {
    short_name = router.params.short_name;
  }
}

onMounted(async () => {
  readRouter();
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
const selectedCategories = ref<BcubeCategory[]>();
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

  readRouter();
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

function monthShortCut(month: string | undefined) {
  if (month) {
    dates.value = [
      new Date(2024, parseInt(month) - 1, 1),
      new Date(2024, parseInt(month), 0),
    ];
  } else {
    dates.value = undefined;
  }

  loadFromServer(true);
}

function openListData(item: NewsArticle) {
  if (item.raw_data && articleViewDialog.value) {
    articleViewDialog.value.openListData(item);
  } else {
    window.alert("No hay datos disponibles");
  }
}

function openLdData(item: NewsArticle) {
  if (item.article_data && articleViewDialog.value) {
    articleViewDialog.value.openLdJsonData(item);
  } else {
    window.alert("No hay datos disponibles");
  }
}

watch(
  serverOptions,
  (value) => {
    loadFromServer(false);
  },
  { deep: true }
);
watch(router, (newValue) => {
  loadFromServer(true);
});
</script>
