<template>
    <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
      <div v-if="np">
      Mostrando Articulos de {{ np.name }} {{ router.params.ccaa }} - {{ router.params.short_name }}
      </div>
      <EasyDataTable 
      :headers="headers" 
      :items="data"   
      v-model:server-options="serverOptions"
      :server-items-length="serverItemsLength"
      :loading="loading"
       alternating
       :rowsPerPage="15" :rowsItems="[5,10,15,20,25]">
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
const mainSize = inject("mainSize");

const data = ref<NewsArticle[]>([]);

const headers: Header[] = [
  { text: "Articulo", value: "headline" },
  { text: "fecha", value: "date", sortable: true },
  { text: "Categorias", value: "categories", sortable: true },
  ]

const router = useRoute()

const np  = ref<NewsPaper|undefined>()

const ccaa:string = router.params.ccaa
const short_name:string= router.params.short_name
const client = NewsClient.instance;

onMounted(async()=>{

  np.value = await  client.getNewsPaper(ccaa, short_name);
  loadFromServer();

});

const loading = ref(false);
const serverItemsLength = ref(0);
const serverOptions = ref<ServerOptions>({
  page: 1,
  rowsPerPage: 15,
  sortBy: undefined,
  sortType: undefined,
});

const loadFromServer = async () => {
  loading.value = true;
  /*
  const {
    serverCurrentPageItems,
    serverTotalItemsLength,
  } = await mockServerItems(serverOptions.value);
  items.value = serverCurrentPageItems;*/

  console.log(serverOptions.value)
  let res = await client.listArticles(ccaa,short_name, serverOptions.value)
  console.log(res)
  if(res.results){
    serverItemsLength.value =res.results;
    data.value=res.items?res.items:[]
  }

  loading.value = false;
};

// initial load


watch(serverOptions, (value) => { loadFromServer(); }, { deep: true });

</script>