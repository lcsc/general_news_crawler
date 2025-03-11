<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Seleccionar Periodico"
    :style="{ width: '25rem' }"
  >
    <div class="flex items-center gap-4 mb-4">
      <label for="state.ca" class="font-semibold w-24">CCAA</label>
      <Select
        v-model="state.ca"
        :options="ccaa"
        showClear
        placeholder="CCAA"
        class="w-full md:w-56"
        @update:modelValue="onCcaaChanged"
      />
    </div>
    <div class="flex items-center gap-4 mb-8">
      <label for="state.provincia" class="font-semibold w-24">Provincia</label>
      <Select
        v-model="state.provincia"
        :options="provincias"
        showClear
        placeholder="Provincias"
        class="w-full md:w-56"
        @update:modelValue="onProvinciaChanged"
        :disabled="state.ca == undefined"
      />
    </div>
    <div class="flex items-center gap-4 mb-8">
      <label for="newspapers" class="font-semibold w-24">Periodico</label>
      <Select
        v-model="newspaper"
        :options="newspapers"
        showClear
        placeholder="Periodico"
        class="w-full md:w-56"
        @update:modelValue="onNewspaperChanged"
        option-label="name"
        :disabled="newspapers == undefined || newspapers.length == 0"
      />
    </div>
    <div class="flex justify-end gap-2">
      <Button
        type="button"
        label="Cancel"
        severity="secondary"
        @click="visible = false"
      ></Button>
      <Button
        type="button"
        label="Ver"
        @click="goToNews"
        :disabled="newspaper == undefined"
      ></Button>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { default as Dialog } from "primevue/dialog";
import { defineExpose, onMounted } from "vue";
import { default as Select } from "primevue/select";
import { default as InputText } from "primevue/inputtext";
import { default as Button } from "primevue/button";
import { ref } from "vue";
import { NewsClient } from "@/newsclient/newsclient";
import type { NewsPaperSelectorModel } from "@/model/selectors";
import { type NewsPaper } from "@/newsclient/hey";
import { useRouter } from "vue-router";

const visible = ref(false);
const target = ref<string>("news");

defineExpose({ visible, target });

const state = ref<NewsPaperSelectorModel>({
  ca: undefined,
  provincia: undefined,
  engine: undefined,
  sub_engine: undefined,
});

const ccaa = ref<string[] | undefined>([]);
const provincias = ref<string[] | undefined>([]);
const engines = ref<string[] | undefined>([]);
const sub_engines = ref<string[] | undefined>([]);
const newspaper = ref<NewsPaper | undefined>(undefined);
const newspapers = ref<NewsPaper[] | undefined>([]);
const router = useRouter();

let data_provincias: { [key: string]: Array<string> } | undefined;

onMounted(async () => {
  let srv_options = NewsClient.instance.serverOptions;
  if (srv_options == undefined) {
    srv_options = await NewsClient.instance.getOptions();
  }

  //console.log(srv_options);
  if (srv_options != undefined) {
    ccaa.value = srv_options.ccaas;
    engines.value = srv_options.engines;
    sub_engines.value = srv_options.sub_engines;
    data_provincias = srv_options.provincias;
  } else {
    alert("No hay opciones");
  }
});

async function updateNewspapers() {
  if (state.value.ca && state.value.provincia) {
    const res = await NewsClient.instance.listNewsPapers(state.value, {
      page: -1,
      rowsPerPage: -1,
    });
    newspapers.value = res.items;
    newspaper.value = undefined;
  } else {
    newspapers.value = [];
    newspaper.value = undefined;
  }
}

function onCcaaChanged(data?: string) {
  state.value.ca = data;
  state.value.provincia = undefined;
  if (data && data_provincias) {
    provincias.value = data_provincias[data];
  } else {
    provincias.value = undefined;
  }
  updateNewspapers();
}

function onProvinciaChanged(data?: string) {
  state.value.provincia = data;
  updateNewspapers();
}

function onNewspaperChanged(data?: NewsPaper) {
  newspaper.value = data;
}

function onEngineChanged(data?: string) {
  state.value.engine = data;
}

function onSubEngineChanged(data?: string) {
  state.value.sub_engine = data;
}

function goToNews() {
  if (newspaper.value) {
    visible.value = false;
    router.push({
      name: target.value,
      params: {
        ccaa: newspaper.value.ccaa,
        short_name: newspaper.value.short_name,
      },
    });
  }
}
</script>
