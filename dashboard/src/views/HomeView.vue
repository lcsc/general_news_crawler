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
  Interactions,
} from "vue3-openlayers";

const options: Vue3OpenlayersGlobalOptions = {
  debug: false,
};
const selectConditions = inject("ol-selectconditions");

const selectCondition = selectConditions.pointerMove;

const featureSelected = (event: SelectEvent) => {
  //console.log(event);
};

const selectInteactionFilter = (feature: Feature) => {
  console.log(feature);
  return feature.get("name") != undefined;
};

function styleFn(feature: FeatureLike, style: Style) {
  if (style == null) {
    throw new Error("No esperado");
  }
  let text = style.getText();
  if (text == null) {
    console.error("no text");
  } else {
    text.setText(feature.get("noml_ccaa"));
  }

  return style;
}

const format = inject("ol-format");

const geoJson = new format.GeoJSON();
import markerIcon from "@/assets/marker.png";
import type { SelectEvent } from "ol/interaction/Select";

provide("ol-options", options);
</script>

<template>
  <div>
    <Map.OlMap
      ref="map"
      class="mapa"
      style="min-width: 400px; min-height: 400px"
      id="map"
    >
      <Map.OlView
        :center="fromLonLat([-3.7038, 40.4168], 'EPSG:4326')"
        :zoom="6"
        projection="EPSG:4326"
      />
      <Layers.OlTileLayer>
        <Sources.OlSourceOsm />
      </Layers.OlTileLayer>

      <Interactions.OlInteractionSelect
        @select="featureSelected"
        :condition="selectCondition"
        :filter="selectInteactionFilter"
      >
        <Styles.OlStyle :overrideStyleFunction="styleFn">
          <Styles.OlStyleStroke color="green" :width="4"></Styles.OlStyleStroke>
          <Styles.OlStyleFill color="rgba(255,0,0,0.5)"></Styles.OlStyleFill>
          <Styles.OlStyleText
            color="rgba(255,255,255,0.5)"
          ></Styles.OlStyleText>
        </Styles.OlStyle>
      </Interactions.OlInteractionSelect>
      <Layers.OlVectorLayer>
        <Sources.OlSourceVector
          url="src/assets/communities.geojson"
          :format="geoJson"
        >
          <Styles.OlStyle>
            <Styles.OlStyleStroke
              color="gray"
              :width="2"
            ></Styles.OlStyleStroke>
            <Styles.OlStyleFill
              color="rgba(255,255,255,0.1)"
            ></Styles.OlStyleFill>
          </Styles.OlStyle>
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
