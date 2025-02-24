<template>
  <header ref="refHeader">
    <div>Aqui iran imagenes</div>
    <!--<MDBNavbar expand="lg" light bg="white" container>
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
    </MDBNavbar>-->
    <div class="card">
      <Menubar :model="items">
            <template #item="{ item, props, hasSubmenu }">
                <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
                    <a v-ripple :href="href" v-bind="props.action" @click="navigate">
                        <span :class="item.icon" />
                        <span>{{ item.label }}</span>
                    </a>
                </router-link>
                <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
                    <span :class="item.icon" />
                    <span>{{ item.label }}</span>
                    <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
                </a>
            </template>
        </Menubar>

        </div>
  </header>
  <main ref="refMain" :style="{ height: mainSize + 'px' }">
    <RouterView />
  </main>
  <footer ref="refFoot">Texto footer</footer>
</template>

<script setup lang="ts">

import { inject, onBeforeUnmount, onMounted, ref } from "vue";

const collapse1 = ref(false);
const dropdown1 = ref(false);

import { useRouter, useRoute } from "vue-router";
import {default as Menubar} from "primevue/menubar"

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


const items = ref([{
        label: 'Router',
        icon: 'pi pi-palette',
        items: [
            {
                label: 'Styled',
                route: '/theming/styled'
            },
            {
                label: 'Unstyled',
                route: '/theming/unstyled'
            }
        ]
    },
    {
        label: 'Programmatic',
        icon: 'pi pi-link',
        command: () => {
            router.push('/introduction');
        }
    },
    {
        label: 'External',
        icon: 'pi pi-home',
        items: [
            {
                label: 'Vue.js',
                url: 'https://vuejs.org/'
            },
            {
                label: 'Vite.js',
                url: 'https://vitejs.dev/'
            }
        ]
    }
]);

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
