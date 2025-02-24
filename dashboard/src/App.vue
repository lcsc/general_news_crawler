<template>
  <header ref="refHeader">
    <div>Aqui iran imagenes</div>
    <MDBNavbar expand="lg" light bg="white" container>
      <MDBNavbarBrand>
        <router-link class="navbar-brand" to="/"
          >News Crawler</router-link
        ></MDBNavbarBrand
      >
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
  <main ref="refMain" :style="{ height: mainSize + 'px' }">
    <RouterView />
  </main>
  <footer ref="refFoot">Texto footer</footer>
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
import { inject, onBeforeUnmount, onMounted, ref } from "vue";

const collapse1 = ref(false);
const dropdown1 = ref(false);

import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const refHeader = ref<HTMLElement | null>(null);
const refMain = ref<HTMLElement | null>(null);
const refFoot = ref<HTMLElement | null>(null);
const mainSize = inject("mainSize");

function handleWindowSizeChange() {
  console.log("on resize");
  const headerSize = refHeader.value?.clientHeight;
  const footSize = refFoot.value?.clientHeight;
  const windowSize = refHeader.value?.parentElement?.clientHeight;
  mainSize.value = windowSize - headerSize - footSize;
  console.log(mainSize);
}

onMounted(() => {
  window.addEventListener("resize", handleWindowSizeChange);
  handleWindowSizeChange();
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", handleWindowSizeChange);
});
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
  height: 100vh;
}
main {
  overflow: hidden;
}
</style>
