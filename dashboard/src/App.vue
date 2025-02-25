<template>
  <header ref="refHeader">
    <div>Aqui iran imagenes</div>
    <div class="card">
      <Menubar :model="items">
        <template #item="{ item, props, hasSubmenu }">
          <router-link
            v-if="item.route"
            v-slot="{ href, navigate }"
            :to="item.route"
            custom
          >
            <a v-ripple :href="href" v-bind="props.action" @click="navigate">
              <span :class="item.icon" />
              <span>{{ item.label }}</span>
            </a>
          </router-link>
          <a
            v-else
            v-ripple
            :href="item.url"
            :target="item.target"
            v-bind="props.action"
          >
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
import type { MenuItem } from "primevue/menuitem";
import { inject, onBeforeUnmount, onMounted, ref, type Ref } from "vue";
import { default as Menubar } from "primevue/menubar";

const refHeader = ref<HTMLElement | null>(null);
const refFoot = ref<HTMLElement | null>(null);
const mainSize: Ref<number> | undefined = inject("mainSize");

function handleWindowSizeChange() {
  //console.log("on resize");
  const headerSize = refHeader.value?.clientHeight;
  const footSize = refFoot.value?.clientHeight;
  const windowSize = refHeader.value?.parentElement?.clientHeight;
  if (mainSize && windowSize && headerSize && footSize) {
    mainSize.value = windowSize - headerSize - footSize;
  }
  //console.log(mainSize);
}

onMounted(() => {
  window.addEventListener("resize", handleWindowSizeChange);
  handleWindowSizeChange();
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", handleWindowSizeChange);
});

const items = ref<MenuItem[]>([
  {
    label: "News Crawler",
    icon: "pi pi-map",
    route: "/",
  },
  { label: "NewsPapers", icon: "pi pi-book", route: "/newspapers" },
  {
    label: "News",
    icon: "pi pi-file",
    command: () => {
      alert("Dialogo escoger Periodico");
    },
  },
  {
    label: "Services",
    icon: "pi pi-wrench",
    items: [{ label: "Estadisticas" }],
  },
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
