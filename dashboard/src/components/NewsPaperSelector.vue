<script setup lang="ts">
import { ref, onMounted } from "vue";

import { Select } from "primevue";

import type { NewsPaperSelectorModel } from "@/model/selectors";
import { NewsClient } from "../newsclient/newsclient";

const ccaa = ref<string[] | undefined>([]);
const provincias = ref<string[] | undefined>([]);
const engines = ref<string[] | undefined>([]);
const sub_engines = ref<string[] | undefined>([]);
const state = ref<NewsPaperSelectorModel>({
  ca: undefined,
  provincia: undefined,
  engine: "bCube",
  sub_engine: undefined,
});

let provs_data: { [ca: string]: string[] };
let all_provs: string[] = [];

function update_provs() {
  if (state.value.ca == null) {
    provincias.value = all_provs;
  } else {
    provincias.value = provs_data[state.value.ca];
  }
}

onMounted(async () => {
  let srv_options = NewsClient.instance.serverOptions;
  if (srv_options == undefined) {
    srv_options == (await NewsClient.instance.getOptions());
  }

  if (srv_options != undefined) {
    ccaa.value = srv_options.ccaas;
    engines.value = srv_options.engines;
    sub_engines.value = srv_options.sub_engines;
    if (srv_options.provincias) {
      provs_data = srv_options.provincias;
      all_provs = [];
      Object.keys(provs_data).forEach((ca) => {
        let tmp = provs_data[ca];
        all_provs = all_provs.concat(tmp);
      });
      update_provs();
    }
  }
});

const emit = defineEmits<{
  stateChannged: [state: NewsPaperSelectorModel];
}>();

function onCcaaChanged(data?: string) {
  state.value.ca = data;
  state.value.provincia = undefined;
  update_provs();
  emit("stateChannged", state.value);
}

function onProvinciaChanged(data?: string) {
  state.value.provincia = data;
  emit("stateChannged", state.value);
}

function onEngineChanged(data?: string) {
  state.value.engine = data;
  emit("stateChannged", state.value);
}

function onSubEngineChanged(data?: string) {
  state.value.sub_engine = data;
  emit("stateChannged", state.value);
}
</script>
<template>
  <div style="display: inline-flex">
    <Select
      v-model="state.ca"
      :options="ccaa"
      showClear
      placeholder="CCAA"
      class="w-full md:w-56"
      @update:modelValue="onCcaaChanged"
    />

    <Select
      v-model="state.provincia"
      :options="provincias"
      showClear
      placeholder="Provincias"
      class="w-full md:w-56"
      @update:modelValue="onProvinciaChanged"
    />
    <Select
      v-model="state.engine"
      :options="engines"
      showClear
      placeholder="Motores"
      class="w-full md:w-56"
      @update:modelValue="onEngineChanged"
    />

    <Select
      v-model="state.sub_engine"
      :options="sub_engines"
      showClear
      placeholder="Sub_Motores"
      class="w-full md:w-56"
      @update:modelValue="onSubEngineChanged"
    />
  </div>
</template>
