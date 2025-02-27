<template>
  <header ref="refHeader"><ViewerHeader></ViewerHeader></header>
  <main ref="refMain" :style="{ height: mainSize + 'px' }">
    <RouterView />
  </main>
  <footer ref="refFoot">Texto footer</footer>
</template>

<script setup lang="ts">
import { inject, onBeforeUnmount, onMounted, ref, type Ref } from "vue";

import ViewerHeader from "./components/ViewerHeader.vue";

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
