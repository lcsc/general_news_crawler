<template>
  <div>Aqui iran imagenes</div>
  <Menubar :model="menuItems">
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
  <NewsPaperSelectDialog ref="paperDialog" />
</template>
<script setup lang="ts">
import { default as Menubar } from "primevue/menubar";
import type { MenuItem } from "primevue/menuitem";

import { inject, onBeforeUnmount, onMounted, ref, type Ref } from "vue";
import NewsPaperSelectDialog from "./dialogs/NewsPaperSelectDialog.vue";
type npsdType = InstanceType<typeof NewsPaperSelectDialog>;
const paperDialog = ref<npsdType | null>(null);

const menuItems = ref<MenuItem[]>([
  {
    label: "News Crawler",
    icon: "pi pi-map",
    route: "/",
  },
  { label: "Periodicos", icon: "pi pi-book", route: "/newspapers" },
  {
    label: "Noticias",
    icon: "pi pi-file",
    command: () => {
      if (paperDialog.value) paperDialog.value.visible = true;
    },
  },
  {
    label: "Servicios",
    icon: "pi pi-wrench",
    items: [{ label: "Estadisticas" }],
  },
  {
    label: "About",
    icon: "pi pi-info",
    route: "/about",
  },
]);
</script>
