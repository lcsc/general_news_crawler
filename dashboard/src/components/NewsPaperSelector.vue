<script setup lang="ts">
import {
  MDBDropdown,
  MDBDropdownToggle,
  MDBDropdownMenu,
  MDBDropdownItem,
} from "mdb-vue-ui-kit";
import { ref, onMounted } from "vue";
import axios from "axios";

const dropdown1 = ref(false);
const drop_prov = ref(false);
const drop_engines = ref(false);
const drop_sub_engines = ref(false);
const ccaa = ref([]);
const engines = ref([]);
const sub_engines = ref([]);

onMounted(async () => {
  let response = await axios.get("/news/api/options");
  console.log(response.data);
  ccaa.value = response.data.ccaas;
  engines.value = response.data.engines;
  sub_engines.value = response.data.sub_engines;
});

const emit = defineEmits<{
  setCcaa: [ca: string];
  setProvincia: [provincia: string];
  setEngine: [value: string];
  setSubEngine: [value: string];
}>();
</script>
<template>
  <div style="display: inline-flex">
    <MDBDropdown v-model="dropdown1">
      <MDBDropdownToggle @click="dropdown1 = !dropdown1">
        CCAA
      </MDBDropdownToggle>
      <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
        <MDBDropdownItem @click="$emit('setCcaa', null)" href="#"
          >Todas</MDBDropdownItem
        >
        <MDBDropdownItem
          v-for="ca in ccaa"
          @click="$emit('setCcaa', ca)"
          href="#"
          >{{ ca }}</MDBDropdownItem
        >
      </MDBDropdownMenu>
    </MDBDropdown>
    <MDBDropdown v-model="drop_prov">
      <MDBDropdownToggle @click="drop_prov = !drop_prov">
        Provincias
      </MDBDropdownToggle>
      <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
        <MDBDropdownItem @click="$emit('setProvincia', null)" href="#"
          >Todas</MDBDropdownItem
        >
      </MDBDropdownMenu>
    </MDBDropdown>
    <MDBDropdown v-model="drop_engines">
      <MDBDropdownToggle @click="drop_engines = !drop_engines">
        Engines
      </MDBDropdownToggle>
      <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
        <MDBDropdownItem @click="$emit('setEngine', null)" href="#"
          >Todos</MDBDropdownItem
        >
        <MDBDropdownItem
          v-for="engine in engines"
          @click="$emit('setEngine', engine)"
          href="#"
          >{{ engine }}</MDBDropdownItem
        >
      </MDBDropdownMenu>
    </MDBDropdown>
    <MDBDropdown v-model="drop_sub_engines">
      <MDBDropdownToggle @click="drop_sub_engines = !drop_sub_engines">
        Engines
      </MDBDropdownToggle>
      <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
        <MDBDropdownItem @click="$emit('setSubEngine', null)" href="#"
          >Todos</MDBDropdownItem
        >
        <MDBDropdownItem
          v-for="engine in sub_engines"
          @click="$emit('setSubEngine', engine)"
          href="#"
          >{{ engine }}</MDBDropdownItem
        >
      </MDBDropdownMenu>
    </MDBDropdown>
  </div>
</template>
