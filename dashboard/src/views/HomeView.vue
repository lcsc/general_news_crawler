<script setup lang="ts">
import { provide } from "vue";
import {
  Map,
  Layers,
  Sources,
  type Vue3OpenlayersGlobalOptions,
} from "vue3-openlayers";

const options: Vue3OpenlayersGlobalOptions = {
  debug: true,
};

provide("ol-options", options);
</script>

<template>
  <div>
    <Map.OlMap ref="map" class="mapa" style="min-width: 400px; min-height: 400px">
      <Map.OlView :center="[-4, 40]" :zoom="6" projection="EPSG:4326" />
      <Layers.OlTileLayer>
        <Sources.OlSourceOsm />
      </Layers.OlTileLayer>
    </Map.OlMap>
  </div>
</template>

<style scoped>
.mapa {
  height: 600px;
}
</style>
