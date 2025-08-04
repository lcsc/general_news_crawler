<template>
  <Dialog v-model:visible="visible" modal header="Articulo" :style="{ width: '75%' }">
    <div class="flex flex-col items-left gap-4 mb-4" v-if="article">
      <h1>{{ article.article_headline }}</h1>
      <div>
        <h2>Fecha</h2>
        <span class="text-sm text-gray-500">{{ article.date }}</span>
      </div>
      <div v-if="is_ld_json">
        <h2>Fuente</h2>
        <Select
          v-model="typeSelected"
          :options="typesOptions"
          showClear
          placeholder="Schema Type"
          class="w-full md:w-56"
          @update:modelValue="onTypeChanged"
        />
      </div>
      <div>
        <h2>Texto Obtenido</h2>
        <span
          class="text-sm text-gray-500"
          :style="{ maxHeight: '200px', display: 'block', overflowY: 'scroll' }"
          >{{ file_txt }}</span
        >
      </div>
    </div>
  </Dialog>
</template>

<script lang="ts" setup>
import { default as Dialog } from "primevue/dialog";
import { inject, ref, type Ref } from "vue";
import type { NewsArticle } from "@/newsclient/hey";
import { NewsClient } from "@/newsclient/newsclient";
import { default as Select } from "primevue/select";

const visible = ref(false);
const article = ref<NewsArticle | null>(null);
const file_txt = ref<string>("Loading...");
const is_ld_json = ref<boolean>(false);
const typesOptions = ref<string[]>([]);
const typeSelected = ref<string | null>(null);

const client = NewsClient.instance;

function openListData(articleData: NewsArticle) {
  article.value = articleData;
  visible.value = true;
  is_ld_json.value = false;
  file_txt.value = "Cargando datos...";

  if (articleData.raw_data) {
    client
      .getFile("list", articleData.raw_data)
      .then((data) => {
        file_txt.value = data;
      })
      .catch((error) => {
        console.error("Error loading file:", error);
        file_txt.value = "Error loading data";
      });
  }
}

function openLdJsonData(articleData: NewsArticle) {
  article.value = articleData;
  visible.value = true;
  is_ld_json.value = true;
  file_txt.value = "Cargando datos...";

  if (articleData.article_data) {
    client
      .getFile("article", articleData.article_data)
      .then((data) => {
        let data_json = JSON.parse(data); // Validate JSON format

        let keys = Object.keys(data_json);
        if (keys.length === 0) {
          file_txt.value = "No data available";
          return;
        }
        typesOptions.value = Object.keys(data_json);
        typeSelected.value = typesOptions.value[0];
        file_txt.value = JSON.stringify(
          data_json[typesOptions.value[0]],
          null,
          2
        );
      })
      .catch((error) => {
        console.error("Error loading file:", error);
        file_txt.value = "Error loading data";
      });
  }
}

function onTypeChanged(type: string) {}

defineExpose({ openListData, openLdJsonData });
</script>
