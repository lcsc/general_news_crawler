<template>
  <div class="ht-theme-main-dark-auto">
    <hot-table
      ref="hotTableComponent"
      :data="data"
      :rowHeaders="true"
      :colHeaders="true"
      :settings="hotSettings"
    >
      <hot-column title="CCAA" data="ccaa"></hot-column>
      <hot-column title="Short_name" data="short_name"></hot-column>
      <hot-column title="Provincia" data="ccaa"></hot-column>
      <hot-column title="Nombre" data="name"></hot-column>
      <hot-column title="Nombre" data="real_url"></hot-column>
      <hot-column title="Motor" data="engine.engine"></hot-column>
      <hot-column title="Version" data="engine.sub_engine"></hot-column>
      <hot-column title="Nº Articulos" data="n_articulos"></hot-column>
      <hot-column title="Primer Mes" data="first_month"></hot-column>
      <hot-column title="Primer Articulo" data="first_article"></hot-column>
      <hot-column title="Ultima Comprobacion" data="last_check"></hot-column>
      <!--
      "id":"679c810af7dc50b65c6ce62e",
      "name":"El Correo de Andalucía",*
      "ccaa":"andalucia",*
      "provincia":"Sevilla",*
      "city":"Sevilla",
      "type":"Periódicos diarios de Andalucía",
      "short_name":"elcorreoweb",*
      "real_url":"https://www.elcorreoweb.es/",*
      "alt_urls":["https://elcorreoweb.es/","https://www.elcorreoweb.es/"],
      "lister_info":[{"name":"El Correo de Andalucía","ccaa":"andalucia","provincia":"","city":null,"type":"Periódicos diarios de Andalucía","url":"https://elcorreoweb.es/","src":"https://www.prensadigital.com/"},{"name":"EL CORREO DE ANDALUCÍA","ccaa":"andalucia","provincia":"Sevilla","city":"Sevilla","type":null,"url":"https://www.elcorreoweb.es/","src":"https://www.prensaescrita.com/"}],
      "engine":{"engine":"bCube","sub_engine":"PrensaIberica","evidence":{"type":"html head meta","name":"generator","content":"BBT bCube NX"}},
      "url_fails":null,
      "first_article":"2004-08-28T02:00:00",*
      "first_month":"2009-09",*
      "n_articulos":295779,*
      "last_check":"2025-02-07T08:46:46.825000"* -->
    </hot-table>
  </div>
</template>

<script lang="js">
import { ref, defineComponent, onMounted } from "vue";
import { HotTable,HotColumn } from "@handsontable/vue3";
import { registerAllModules } from "handsontable/registry";
import "handsontable/styles/handsontable.min.css";
import "handsontable/styles/ht-theme-main.min.css";
import axios from "axios";

// register Handsontable's modules
registerAllModules();

export default defineComponent({
  data() {
    return {
      data:null,
      hotSettings: {
        licenseKey: "non-commercial-and-evaluation",
        rowHeaders: true,
        manualRowMove: true,
        contextMenu: true,
      },

    };
  },
  components: {
    HotTable, HotColumn
  },
  mounted() {
    axios.get("/api/np?engine=bCube").then(response=>{
      //hotTableComponent.update_data(response.data)
      this.$refs.hotTableComponent.hotInstance.loadData(response.data)
    })
  },
});
</script>
