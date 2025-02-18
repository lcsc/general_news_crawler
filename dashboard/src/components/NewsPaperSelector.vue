<script setup lang="ts">
import {
  MDBDropdown,
  MDBDropdownToggle,
  MDBDropdownMenu,
  MDBDropdownItem,
} from "mdb-vue-ui-kit";
import { ref, onMounted } from "vue";
import axios from "axios";
import { default as DropDown } from "./DropDown.vue";
import type { NewsPaperSelectorModel } from "@/model/selectors";

const ccaa = ref([]);
const ca = ref<string | null>("");
const provincias = ref([]);
const engines = ref([]);
const sub_engines = ref([]);
const state = ref<NewsPaperSelectorModel>({
  ca: null,
  provincia: null,
  engine: "bCube",
  sub_engine: null,
});

onMounted(async () => {
  let response = await axios.get("/news/api/options");
  console.log(response.data);
  ccaa.value = response.data.ccaas;
  engines.value = response.data.engines;
  sub_engines.value = response.data.sub_engines;
});

const emit = defineEmits<{
  stateChannged: [state: NewsPaperSelectorModel];
}>();

function onCcaaChanged(data: string | null) {
  state.value.ca = data;
  ca.value = data;
  emit("stateChannged", state.value);
}

function onProvinciaChanged(data: string | null) {
  state.value.provincia = data;
  emit("stateChannged", state.value);
}

function onEngineChanged(data: string | null) {
  state.value.engine = data;
  emit("stateChannged", state.value);
}

function onSubEngineChanged(data: string | null) {
  state.value.sub_engine = data;
  emit("stateChannged", state.value);
}
</script>
<template>
  <div style="display: inline-flex">
    <DropDown
      caption="CCAA"
      :data="ccaa"
      :selected="state.ca"
      @onSelect="(data) => onCcaaChanged(data)"
    ></DropDown>
    <DropDown
      caption="Provincias"
      :data="provincias"
      :selected="state.provincia"
      @onSelect="(data) => onProvinciaChanged(data)"
    ></DropDown>
    <DropDown
      caption="Motores"
      :data="engines"
      :selected="state.engine"
      @onSelect="(data) => onEngineChanged(data)"
    ></DropDown>
    <DropDown
      caption="Sub_Motores"
      :data="sub_engines"
      :selected="state.sub_engine"
      @onSelect="(data) => onSubEngineChanged(data)"
    ></DropDown>
  </div>
</template>
