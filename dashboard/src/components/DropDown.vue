<script setup lang="ts">
import {
  MDBDropdown,
  MDBDropdownToggle,
  MDBDropdownMenu,
  MDBDropdownItem,
} from "mdb-vue-ui-kit";
import { ref, onMounted } from "vue";

const drop = ref(false);
const props = defineProps(["caption", "data", "selected"]);
const emit = defineEmits<{
  onSelect: [option: string | null];
}>();
</script>

<template>
  <MDBDropdown v-model="drop">
    <MDBDropdownToggle @click="drop = !drop">
      {{ caption }}
    </MDBDropdownToggle>
    <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
      <MDBDropdownItem
        @click="$emit('onSelect', null)"
        href="#"
        :active="selected == null"
        >*</MDBDropdownItem
      >
      <MDBDropdownItem divider />
      <MDBDropdownItem
        v-for="option in data"
        @click="$emit('onSelect', option)"
        href="#"
        :active="selected == option"
        >{{ option }}</MDBDropdownItem
      >
    </MDBDropdownMenu>
  </MDBDropdown>
</template>
