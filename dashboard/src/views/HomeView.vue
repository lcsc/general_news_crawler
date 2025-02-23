<script setup lang="ts">
import { Feature, type Map as OlMap, type MapBrowserEvent } from "ol";
import { fromLonLat } from "ol/proj";
import { inject, onMounted, provide, ref } from "vue";
import {
  Map,
  Layers,
  Sources,
  Styles,
  type Vue3OpenlayersGlobalOptions,
  Interactions,
} from "vue3-openlayers";

import type { SelectEvent } from "ol/interaction/Select";
import type { Coordinate } from "ol/coordinate";

const selectConditions = inject("ol-selectconditions");
const format = inject("ol-format");
const mainSize = inject("mainSize");

const selectCondition = selectConditions.pointerMove;
const selectedFeature = ref<Feature | null>(null);
const geoJson = new format.GeoJSON();
const options: Vue3OpenlayersGlobalOptions = {
  debug: false,
};

const tooltipCoord = ref<Coordinate | null>(null);
const map = ref<{ map: OlMap } | null>(null);

const featureSelected = (event: SelectEvent) => {
  let selectedArray = event.selected;
  if (selectedArray.length == 0) {
    setTimeout(() => {
      selectedFeature.value = null;
    });
  } else {
    setTimeout(() => {
      selectedFeature.value = selectedArray[0];
    });
  }
  //event.
  //console.log(event);
};

const selectInteactionFilter = (feature: Feature) => {
  //console.log(feature);
  return feature.get("name") != undefined;
};

function getMouseCoords(evt: MapBrowserEvent<PointerEvent>) {
  if (evt.dragging) {
    return;
  }

  tooltipCoord.value = evt.coordinate;
}

function onMapClick() {
  if (selectedFeature.value != null) {
    alert("Click on " + selectedFeature.value.get("name"));
  }
}

const log = (type: string, event: MapBrowserEvent<UIEvent>) => {
  setTimeout(() => {
    tooltipCoord.value = event.coordinate;
  });
};

provide("ol-options", options);

onMounted(() => {
  //map.value?.map.on("pointermove", getMouseCoords);
  //map.value?.map.on("click", onMapClick);
});
</script>

<template>
  <div>
    <Map.OlMap
      ref="map"
      class="mapa"
      :style="{ height: mainSize + 'px' }"
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

      <Map.OlOverlay
        v-if="tooltipCoord"
        :position="tooltipCoord"
        :offset="[0, -5]"
        positioning="bottom-center"
        :stopEvent="true"
        :insertFirst="true"
      >
        <div class="tooltip">selectedFeature.get("name")</div>
      </Map.OlOverlay>

      <Interactions.OlInteractionPointer @move="log('⬆️ up', $event)">
      </Interactions.OlInteractionPointer>

      <Interactions.OlInteractionSelect
        @select="featureSelected"
        :condition="selectCondition"
        :filter="selectInteactionFilter"
      >
        <Styles.OlStyle>
          <Styles.OlStyleStroke color="white" :width="4"></Styles.OlStyleStroke>
          <Styles.OlStyleFill color="rgba(255,255,64,0.5)"></Styles.OlStyleFill>
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
  /* height: 600px; */
  min-width: 400px;
  min-height: 400px;
}
.tooltip {
  position: relative;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  opacity: 0.7;
  white-space: nowrap;
  font-size: 12px;
  cursor: default;
  user-select: none;
}
</style>
