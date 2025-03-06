<template>
  <svg viewBox="0 0 3760 100">
    <title>Timeline 2022</title>
    <g class="bars">
      <rect fill="#0066FF" x="0" width="310" height="25"></rect>
      <rect fill="#3366AA" x="320" width="280" height="25"></rect>
      <rect fill="#99AA33" x="610" width="310" height="25"></rect>
      <rect fill="#99EE33" x="930" width="300" height="25"></rect>
      <rect fill="green" x="1240" width="310" height="25"></rect>
      <rect fill="yellow" x="1560" width="300" height="25"></rect>
      <rect fill="gold" x="1870" width="310" height="25"></rect>
      <rect fill="cyan" x="2190" width="310" height="25"></rect>
      <rect fill="orange" x="2510" width="300" height="25"></rect>
      <rect fill="red" x="2820" width="310" height="25"></rect>
      <rect fill="brown" x="3140" width="300" height="25"></rect>
      <rect fill="white" x="3450" width="310" height="25"></rect>
    </g>
    <g
      class="labels"
      style="font-size: 50px"
      text-anchor="middle"
      v-if="year != null && showLabels"
    >
      <text fill="#747474" x="0" y="80" text-anchor="start">Enero</text>
      <text fill="#747474" x="320" y="80" text-anchor="start">Febrero</text>
      <text fill="#747474" x="610" y="80" text-anchor="start">Marzo</text>
      <text fill="#747474" x="930" y="80" text-anchor="start">Abril</text>
      <text fill="#747474" x="1240" y="80" text-anchor="start">Mayo</text>
      <text fill="#747474" x="1560" y="80" text-anchor="start">Junio</text>
      <text fill="#747474" x="1870" y="80" text-anchor="start">Julio</text>
      <text fill="#747474" x="2190" y="80" text-anchor="start">Agosto</text>
      <text fill="#747474" x="2510" y="80" text-anchor="start">Septiembre</text>
      <text fill="#747474" x="2820" y="80" text-anchor="start">Octubre</text>
      <text fill="#747474" x="3140" y="80" text-anchor="start">Noviembre</text>
      <text fill="#747474" x="3450" y="80" text-anchor="start">Diciembre</text>
    </g>
  </svg>
</template>
<script setup lang="ts">
import { defineProps } from "vue";
import type { NewsPaperBackFill } from "@/src/newsclient/hey";

type dataType = {
  [key: string]: {
    [key: string]: NewsPaperBackFill;
  };
};

defineProps({
  data: {
    type: Object as PropType<dataType> | null,
    required: true,
  },
  year: {
    type: Number | null,
    required: false,
    default: null,
  },
  showLabels: {
    type: Boolean,
    required: false,
    default: false,
  },
});
</script>
