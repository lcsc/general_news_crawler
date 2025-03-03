<template>
  <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
    <Panel v-if="np" :header="np.name" toggleable>
      <p class="m-0">
        Mostrando Articulos de {{ router.params.ccaa }} - {{ router.params.short_name }}
      </p>
    </Panel>
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
          optionLabel="name"
          filter
          placeholder="Categorias"
          class="w-full md:w-80"
        />
        <Button icon="pi pi-search" severity="primary" text @click="loadFromServer"/>
      </template>
    </Toolbar>

    <EasyDataTable
      :headers="headers"
      :items="data"
      v-model:server-options="serverOptions"
      :server-items-length="serverItemsLength"
      :loading="loading"
      alternating
      :rowsPerPage="15"
      :rowsItems="[5, 10, 15, 20, 25]"
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

import {type NewsPaper, type NewsArticle} from "../newsclient/hey";
import { useRoute } from "vue-router";
import { NewsClient } from "@/newsclient/newsclient";
import { DatePicker, Panel, Toolbar, Button, FloatLabel, MultiSelect} from "primevue";
import type { NewsSearch } from "@/model/selectors";
const mainSize = inject("mainSize");

const data = ref<NewsArticle[]>([]);

const headers: Header[] = [
  { text: "Articulo", value: "headline" },
  { text: "fecha", value: "date", sortable: true },
  { text: "Categorias", value: "categories", sortable: true },
  ]

const router = useRoute()

const np  = ref<NewsPaper|undefined>()

const ccaa:string = router.params.ccaa;
const short_name:string= router.params.short_name;
const client = NewsClient.instance;

onMounted(async()=>{

  np.value = await  client.getNewsPaper(ccaa, short_name);
  loadFromServer();

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
const categories = ref();

const loadFromServer = async () => {
  loading.value = true;

  console.log(dates.value)
  if (dates.value && dates.value.length > 0) {
    serverOptions.value.notBefore = dates.value[0];
    serverOptions.value.notAfter = dates.value[1];
  }else{
    serverOptions.value.notBefore = undefined;
    serverOptions.value.notAfter = undefined;
  }
  let res = await client.listArticles(ccaa,short_name, serverOptions.value)
  console.log(res)
  if(res.results){
    serverItemsLength.value =res.results;
    data.value=res.items?res.items:[]
  }

  loading.value = false;
};


watch(serverOptions, (value) => { loadFromServer(); }, { deep: true });
</script>
