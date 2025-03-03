<script setup lang="ts">
const props = defineProps({
    data: {
        type: Array,
        required: true,
        default: () => []
    }
});

// 添加 watchEffect 来监控数据变化
import { watchEffect } from 'vue';
watchEffect(() => {
    console.log("BaseTable data:", props.data);
});
</script>

<template>
    <slot></slot>
</template>

<style scoped>
:deep(.el-table) {
    background-color: transparent !important;
    border-radius: 10px;
}

:deep(.el-table th) {
    background-color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-table td) {
    background-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.el-table tr:hover td) {
    background-color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover>td) {
    background-color: rgba(255, 255, 255, 0.4) !important;
}
</style>