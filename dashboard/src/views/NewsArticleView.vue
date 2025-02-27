<template>
    <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
      <div v-if="np">
      Mostrando Articulos de {{ np.name }} {{ router.params.ccaa }} - {{ router.params.short_name }}
      </div>
      <EasyDataTable :headers="headers" :items="data" alternating>
        <template #item-real_url="item">
          <a :href="item.real_url" target="_blank">{{ item.real_url }}</a>
        </template>
      </EasyDataTable>
    </div>
  </template>
  
  <style></style>

<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import type { Header } from "vue3-easy-data-table";

import {type NewsPaper, type NewsArticle} from "../newsclient/hey";
import { useRoute } from "vue-router";
import { NewsClient } from "@/newsclient/newsclient";
const mainSize = inject("mainSize");

const data = ref<NewsArticle[]>([]);

const headers: Header[] = [
  { text: "Url", value: "url", sortable: true },
  ]

const router = useRoute()

const np  = ref<NewsPaper|undefined>()


onMounted(async()=>{
  np.value = await  NewsClient.instance.getNewsPaper(router.params.ccaa, router.params.short_name)
});

</script>