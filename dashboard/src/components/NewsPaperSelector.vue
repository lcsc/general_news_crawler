<script setup lang="ts">
  import { MDBDropdown, MDBDropdownToggle, MDBDropdownMenu, MDBDropdownItem } from "mdb-vue-ui-kit";
  import { ref,onMounted } from 'vue';
  import axios from "axios";

  const dropdown1 = ref(false);
  const drop_prov = ref(false);
  const ccaa = ref([])

  onMounted(async ()=>{
        let response = await axios.get("/news/api/options")
        console.log(response.data)
        ccaa.value=response.data.ccaas
  });

  const emit = defineEmits<{
    setccaa: [ca: string]
    update: [value: string]
    }>()
</script>
<template>
    <div style="display: inline-flex;">
        <MDBDropdown v-model="dropdown1">
        <MDBDropdownToggle @click="dropdown1 = !dropdown1">
            CCCAA
        </MDBDropdownToggle>
        <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
            <MDBDropdownItem v-for="ca in ccaa" @click="$emit('setccaa',ca)" href="#" >{{ca}}</MDBDropdownItem>
        </MDBDropdownMenu>
        </MDBDropdown>
        <MDBDropdown v-model="drop_prov">
        <MDBDropdownToggle @click="drop_prov = !drop_prov">
            CCCAA
        </MDBDropdownToggle>
        <MDBDropdownMenu aria-labelledby="dropdownMenuButton">
            <MDBDropdownItem @click="$emit('setccaa','aragon')" href="#" >aragon</MDBDropdownItem>
        </MDBDropdownMenu>
        </MDBDropdown>
    </div>
</template>