<template>
  <header>
    <div>Aqui iran imagenes</div>
    <MDBNavbar expand="lg" light bg="white" container>
      <MDBNavbarBrand href="/">News Crawler</MDBNavbarBrand>
      <MDBNavbarToggler
        target="#navbarExample01"
        @click="collapse1 = !collapse1"
      ></MDBNavbarToggler>
      <MDBCollapse id="#navbarExample01" v-model="collapse1">
        <MDBNavbarNav class="mb-2 mb-lg-0">
          <MDBNavbarItem to="/newspapers"> NewsPapers </MDBNavbarItem>
          <MDBNavbarItem to="#"> News </MDBNavbarItem>
          <MDBNavbarItem to="#"> Servicios </MDBNavbarItem>
          <MDBNavbarItem to="/about"> About </MDBNavbarItem>
        </MDBNavbarNav>
      </MDBCollapse>
    </MDBNavbar>
  </header>
  <main>
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import {
  MDBNavbar,
  MDBNavbarBrand,
  MDBNavbarToggler,
  MDBCollapse,
  MDBNavbarItem,
  MDBNavbarNav,
} from "mdb-vue-ui-kit";
import { ref } from "vue";

const collapse1 = ref(false);
const dropdown1 = ref(false);
</script>

<script lang="ts">
export default {
  name: "App",
  components: {},
};
</script>

<style>
#app {
  font-family: Roboto, Helvetica, Arial, sans-serif;
}
</style>
