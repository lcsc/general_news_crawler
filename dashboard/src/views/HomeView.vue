<script setup lang="ts">
import type { Feature } from "ol";
import type { FeatureLike } from "ol/Feature";
import type { Geometry } from "ol/geom";
import { fromLonLat } from "ol/proj";
import { Fill, Stroke, Style } from "ol/style";
import { inject, provide } from "vue";
import {
  Map,
  Layers,
  Sources,
  Styles,
  type Vue3OpenlayersGlobalOptions,
} from "vue3-openlayers";

const options: Vue3OpenlayersGlobalOptions = {
  debug: false,
};

function styleFn(feature: FeatureLike) {
  return new Style({
    stroke: new Stroke({
      color: "black",
      width: 2,
    }),
    fill: new Fill({
      color: feature.get("COLOR_BIO") || "#eeeeee",
    }),
  });
}

const format = inject("ol-format");
const geoJson = new format.GeoJSON();

provide("ol-options", options);
</script>

<template>
  <div>
    <Map.OlMap
      ref="map"
      class="mapa"
      style="min-width: 400px; min-height: 400px"
    >
      <Map.OlView
        :center="fromLonLat([-3.7038, 40.4168], 'EPSG:4326')"
        :zoom="6"
        projection="EPSG:4326"
      />
      <Layers.OlTileLayer>
        <Sources.OlSourceOsm />
      </Layers.OlTileLayer>

      <Layers.OlVectorLayer>
        <Sources.OlSourceVector
          url="src/assets/communities.geojson"
          :format="geoJson"
        >
          <Styles.OlStyle :overrideStyleFunction="styleFn"></Styles.OlStyle>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>
    </Map.OlMap>
  </div>
</template>

<style scoped>
.mapa {
  height: 600px;
}
</style>
