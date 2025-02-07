<template>
  <div class="ht-theme-main-dark-auto">
    <hot-table
      :data="data"
      :rowHeaders="true"
      :colHeaders="true"
      :settings="hotSettings"
    ></hot-table>
  </div>
</template>

<script setup lang="js">
import { defineComponent, onMounted } from "vue";
import { HotTable } from "@handsontable/vue3";
import { registerAllModules } from "handsontable/registry";
import "handsontable/styles/handsontable.min.css";
import "handsontable/styles/ht-theme-main.min.css";
import axios from "axios";

onMounted(async () => {
  const response = await axios.get(
    "/api/np/andalucia?engine=bCube"
  );
  console.log(response.data);
});
</script>

<script lang="js">
// register Handsontable's modules
registerAllModules();

export default defineComponent({
  data() {
    return {
      data: [
        ["", "Ford", "Volvo", "Toyota", "Honda"],
        ["2016", 10, 11, 12, 13],
        ["2017", 20, 11, 14, 13],
        ["2018", 30, 15, 12, 13],
      ],
      hotSettings: {
        licenseKey: "non-commercial-and-evaluation",
      },
    };
  },
  components: {
    HotTable,
  },
});
</script>
