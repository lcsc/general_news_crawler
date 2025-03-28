<script setup lang="ts">
import { Feature, type Map as OlMap, type MapBrowserEvent } from "ol";
import { fromLonLat } from "ol/proj";
import { inject, onMounted, provide, ref, type Ref } from "vue";
import {
  Map,
  Layers,
  Sources,
  Styles,
  type Vue3OpenlayersGlobalOptions,
  Interactions,
  MapControls,
} from "vue3-openlayers";

import type { SelectEvent } from "ol/interaction/Select";
import type { Coordinate } from "ol/coordinate";
import { useRouter } from "vue-router";

import ccaaUrl from "../assets/communities.geojson?url";
import provsUrl from "../assets/provinces.geojson?url";
import { ccaa_codes } from "../model/gejson_codes";
import {
  type MapConfigOptions,
  type NewsPaperSelectorModel,
} from "@/model/selectors";
import MapConfigDialog from "@/components/dialogs/MapConfigDialog.vue";

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
const mapCenter = ref(fromLonLat([-3.7038, 40.4168], "EPSG:4326"));
const mapZoom = ref(6);
const router = useRouter();
const npState = inject<Ref<NewsPaperSelectorModel>>("npSelectorState");

type mcdType = InstanceType<typeof MapConfigDialog>;
const configDialog = ref<mcdType | null>(null);
const config: Ref<MapConfigOptions> | undefined = ref<MapConfigOptions>({
  layer: "Comunidades",
});
provide("MapConfig", config);

const featureSelected = (event: SelectEvent) => {
  let selectedArray = event.selected;
  if (selectedArray.length == 0) {
    selectedFeature.value = null;
  } else {
    selectedFeature.value = selectedArray[0];
  }
  //event.
  //console.log(event);
};

const selectInteactionFilter = (feature: Feature) => {
  //console.log(feature);
  return feature.get("name") != undefined;
};

function onMapClick(evt: MapBrowserEvent<UIEvent>) {
  if (npState == undefined) return;

  if (selectedFeature.value != null) {
    const cod_ccaa = selectedFeature.value.get("cod_ccaa");
    if (ccaa_codes[cod_ccaa] != undefined) {
      npState.value.ca = ccaa_codes[cod_ccaa].id;
      router.push({ name: "newspapers" });
    } else {
      alert("Click on " + selectedFeature.value.get("cod_ccaa"));
    }
  }
}

function handleClick(event: PointerEvent) {
  if (configDialog.value) configDialog.value.visible = true;
}

const getCoord = (event: MapBrowserEvent<UIEvent>) => {
  if (event.dragging) {
    return;
  }
  tooltipCoord.value = event.coordinate;
};

provide("ol-options", options);

onMounted(() => {
  map.value?.map.on("pointermove", getCoord);
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
      @click="onMapClick"
      :controls="[]"
    >
      <Map.OlView :center="mapCenter" :zoom="mapZoom" projection="EPSG:4326" />
      <Layers.OlTileLayer>
        <Sources.OlSourceOsm />
      </Layers.OlTileLayer>

      <Map.OlOverlay
        v-if="tooltipCoord && selectedFeature"
        :position="tooltipCoord"
        :offset="[0, -5]"
        positioning="bottom-center"
        :stopEvent="false"
        :insertFirst="false"
      >
        <div class="tooltip">{{ selectedFeature.get("name") }}</div>
      </Map.OlOverlay>

      <!-- <Interactions.OlInteractionPointer @move="getCoord($event)"> 
      </Interactions.OlInteractionPointer>-->

      <Layers.OlVectorLayer :visible="config.layer == 'Comunidades'">
        <Sources.OlSourceVector :url="ccaaUrl" :format="geoJson">
          <Styles.OlStyle>
            <Styles.OlStyleStroke color="gray" :width="2"></Styles.OlStyleStroke>
            <Styles.OlStyleFill color="rgba(255,255,255,0.1)"></Styles.OlStyleFill>
          </Styles.OlStyle>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

      <Layers.OlVectorLayer :visible="config.layer == 'Provincias'">
        <Sources.OlSourceVector :url="provsUrl" :format="geoJson">
          <Styles.OlStyle>
            <Styles.OlStyleStroke color="gray" :width="2"></Styles.OlStyleStroke>
            <Styles.OlStyleFill color="rgba(255,255,255,0.1)"></Styles.OlStyleFill>
          </Styles.OlStyle>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>

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
      <MapControls.OlZoomControl />
      <MapControls.OlAttributionControl />
      <MapControls.OlButtonControl
        html="<span class='pi pi-wrench' />"
        className="config-btn"
        :handleClick="handleClick"
      />
    </Map.OlMap>
  </div>
  <MapConfigDialog ref="configDialog" />
</template>

<style>
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

.config-btn {
  top: 65px;
  left: 0.5em;
}
.ol-touch .config-btn {
  top: 80px;
}
</style>
