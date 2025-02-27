<template>
    <div :style="{ height: mainSize + 'px' }" class="overflow-auto">
  
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

import {NewsArticle} from "../newsclient/hey";
const mainSize = inject("mainSize");

const data = ref<NewsPaperArticle[]>([]);

const headers: Header[] = [
  { text: "CCAA", value: "ccaa", sortable: true },
  ]

</script>