<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Opciones de Mapa"
    :style="{ width: '25rem' }"
  >
    <div class="flex items-center gap-4 mb-4" v-if="config">
      <label for="config.layer" class="font-semibold w-24">Divisiones</label>
      <Select
        v-model="config.layer"
        :options="['Comunidades', 'Provincias']"
        class="w-full md:w-56"
      />
    </div>
  </Dialog>
</template>

<script lang="ts" setup>
import type { MapConfigOptions } from "@/model/selectors";
import { Select } from "primevue";
import { default as Dialog } from "primevue/dialog";
import { inject, ref, type Ref } from "vue";

const visible = ref(false);

defineExpose({ visible });
const config: Ref<MapConfigOptions> | undefined = inject("MapConfig");
</script>
