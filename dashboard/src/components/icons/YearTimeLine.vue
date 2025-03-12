<template>
  <svg :viewBox="viewBox">
    <title v-if="year">Timeline {{ year }}</title>
    <g class="bars">
      <rect
        v-for="item in display"
        :fill="item.color"
        :x="item.x"
        :width="item.width"
        height="25"
        @click="emit('clikOn', item.clickId)"
      >
        <title v-if="item.msg">{{ item.msg }}</title>
      </rect>
    </g>
    <g
      class="labels"
      style="font-size: 50px"
      text-anchor="middle"
      v-if="year != null && showLabels"
    >
      <text v-for="item in display" fill="#747474" :x="item.x" y="80" text-anchor="start">
        {{ item.label }}
      </text>
    </g>
  </svg>
</template>
<script setup lang="ts">
import {
  defineProps,
  ref,
  onMounted,
  watch,
  computed,
  type PropType,
} from "vue";
import type { NewsPaperBackFill } from "@/newsclient/hey";

type displayType = {
  x: number;
  width: number;
  fill?: string;
  label: string;
  color?: string;
  msg?: string;
  clickId?: string;
};

//const display = ref<displayType>([]);
const viewBox = ref<string>("0 0 3760 100");

type dataType = {
  [key: string]: {
    [key: string]: NewsPaperBackFill;
  };
};

const props = defineProps({
  data: {
    type: Object as PropType<dataType>,
    required: true,
  },
  year: {
    type: [Number, String],
    required: false,
    default: undefined,
  },
  showLabels: {
    type: Boolean,
    required: false,
    default: false,
  },
  short: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const months: { [key: string]: displayType } = {
  "1": { label: "Enero", x: 0, width: 310 },
  "2": { label: "Febrero", x: 320, width: 280 },
  "3": { label: "Marzo", x: 610, width: 310 },
  "4": { label: "Abril", x: 930, width: 300 },
  "5": { label: "Mayo", x: 1240, width: 310 },
  "6": { label: "Junio", x: 1560, width: 300 },
  "7": { label: "Julio", x: 1870, width: 310 },
  "8": { label: "Agosto", x: 2190, width: 310 },
  "9": { label: "Septiembre", x: 2510, width: 300 },
  "10": { label: "Octubre", x: 2820, width: 310 },
  "11": { label: "Noviembre", x: 3140, width: 300 },
  "12": { label: "Diciembre", x: 3450, width: 310 },
};

//function updateDisplay() {
const display = computed({
  get: () => {
    //console.log("updateDisplay");
    let d: displayType[] = [];
    if (props.short) {
      viewBox.value = "0 0 376 25";
    }
    if (props.year) {
      for (let month in props.data[props.year.toString()]) {
        let item: NewsPaperBackFill = props.data[props.year.toString()][month];
        let obj: displayType = { ...months[month] };
        obj.clickId = month;
        if (item.status == "OK") {
          obj.color = "green";
        } else if (item.status == "ERROR") {
          obj.color = "red";
        } else if (item.status == "Pending") {
          obj.color = "yellow";
        } else {
          obj.color = "white";
        }
        if (props.short) {
          obj.x = obj.x / 10;
          obj.width = obj.width / 10;
        }
        if (item.msg == null) {
          obj.msg = undefined;
        } else {
          obj.msg = item.msg;
        }
        d.push(obj);
      }
    } else if (props.data) {
      /*for (let year in props.data) {
      let x = 0;
      for (let day in props.data[month]) {
        let item = props.data[month][day];
        d.push({
          x: x,
          width: item.n_articles,
          fill: item.color,
          label: item.n_articles.toString(),
        });
        x += item.n_articles;
      }
    }*/
    }
    return d;
  },
  set: () => {},
});

onMounted(() => {
  //updateDisplay();
});
const emit = defineEmits<{
  clikOn: [selected: string | undefined];
}>();

// watch(
//   [props.data, props.year],
//   (value) => {
//     alert("props.data changed");
//   },
//   { deep: true }
// );
</script>
