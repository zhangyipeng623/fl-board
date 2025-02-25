<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import type { DbNode } from "@/utils/settings";
import * as echarts from 'echarts';


const props = defineProps<{
    node: DbNode | null
    isCenterNode: boolean
    systemInfo: {
        cpu: string;
        gpu: string;
        system: string;
    }
}>()

const nodeInfo = ref({
    mysql: "false",
    redis: "false",
    nginx: "false"
})
const selectedStat = ref<'cpu' | 'gpu'>('cpu')
const selectedGpuModel = ref<string>('') // 新增当前选中的GPU型号
const gpuModels = ref<string[]>([]) // 存储可用的GPU型号列表
const hasGPU = ref(false);
const nodeStatus = ref({
    cpu: {
        usage: 0,
        temp: 0,
        freq: 0
    },
    gpu: {
        usage: 0,
        temp: 0,
        mem_usage: ""
    }
});
type MetricPoint = { time: string; value: number };
const metricsHistory = ref<Record<'cpu' | 'gpu', MetricPoint[]>>({
    cpu: [],
    gpu: [],
});

const updateHistory = (arr: MetricPoint[], newVal: number, time: string) => {
    return [...arr.slice(-59), { time, value: newVal }]; // 保留60个数据点
};
// 实时数据获取
const fetchMetrics = async () => {
    try {
        const res = await axios.get(`http://${props.node?.ip}:${props.node?.port}/node/metrics`);
        const now = new Date().toLocaleTimeString();

        // 新增GPU存在性判断
        hasGPU.value = !!res.data.gpu_info && Object.keys(res.data.gpu_info).length > 0;

        // 处理CPU数据（新增部分）
        metricsHistory.value.cpu = updateHistory(
            metricsHistory.value.cpu,
            res.data.cpu.cpu_usage,
            now
        );

        // 更新CPU状态数据
        nodeStatus.value.cpu = {
            usage: res.data.cpu.cpu_usage,
            temp: res.data.cpu.temp || 0, // 根据实际接口字段调整
            freq: res.data.cpu.cpu_freq
        };

        // 处理GPU数据（优化后的部分）
        if (hasGPU.value) {
            const gpuList = Object.keys(res.data.gpu_info);
            gpuModels.value = gpuList;

            if (gpuList.length > 0 && !selectedGpuModel.value) {
                selectedGpuModel.value = gpuList[0];
            }

            if (selectedStat.value === 'gpu' && selectedGpuModel.value) {
                const gpu = res.data.gpu_info[selectedGpuModel.value];
                metricsHistory.value.gpu = updateHistory(
                    metricsHistory.value.gpu,
                    (gpu.used / gpu.total * 100),
                    now
                );

                nodeStatus.value.gpu = {
                    usage: Number((gpu.used / gpu.total * 100).toFixed(1)),
                    temp: gpu.temperature,
                    mem_usage: `${(gpu.used / 1024).toFixed(1)}/${(gpu.total / 1024).toFixed(1)}GB`
                }
            }
        }

        initChart();
    } catch (err) {
        console.error('获取指标失败:', err);
    }
};

let chart: echarts.ECharts;

const initChart = () => {
    const dom = document.getElementById('metrics-chart');
    if (!dom) return;

    // 销毁旧实例
    if (!chart) {
        chart = echarts.init(dom);
    }

    chart.setOption({
        xAxis: {
            type: 'category',
            data: metricsHistory.value[selectedStat.value].map(i => i.time)
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: selectedStat.value === 'cpu' ? '{value}%' : '{value}%'
            }
        },
        series: [{
            data: metricsHistory.value[selectedStat.value].map(i => i.value),
            type: 'line',
            smooth: true,
            showSymbol: false // 隐藏数据点
        }]
    });
};
const getNodeStatus = async () => {
    try {
        const res = await axios.get(`http://${props.node?.ip}:${props.node?.port}/status`)
        nodeInfo.value = res.data.data
    } catch (e) {
        console.error('获取节点状态失败:', e)
    }
}


onMounted(async () => {
    getNodeStatus();
    fetchMetrics();
    const timer = setInterval(fetchMetrics, 500); // 5秒轮询
    onUnmounted(() => clearInterval(timer));
})

</script>

<template>
    <div class="overlay" @click.self="$emit('close')">
        <div class="overlay-content">
            <div class="header">
                <span class="node-title">{{ props.node?.name }}</span>
                <div class="top-right-tag" :class="props.node?.is_connect ? 'connected' : 'disconnected'">
                    {{ props.node?.is_connect ? '在线' : '离线' }}
                </div>
            </div>

            <div class="info-row">
                <div class="address">
                    <span class="node-address">{{ props.node?.ip }}:{{ props.node?.port }}</span>
                </div>
                <div class="service-tags">
                    <div v-if="props.isCenterNode" class="service-tag small"
                        :class="nodeInfo.mysql ? 'active' : 'inactive'">
                        MySQL
                    </div>
                    <div class="service-tag small" :class="nodeInfo.redis ? 'active' : 'inactive'">
                        Redis
                    </div>
                    <div v-if="props.isCenterNode" class="service-tag small"
                        :class="nodeInfo.nginx ? 'active' : 'inactive'">
                        Nginx
                    </div>
                </div>
            </div>
            <div class="status-panel">
                <div class="stat-switcher">
                    <button v-for="stat in ['cpu', 'gpu'] as const" :key="stat" @click="selectedStat = stat" :class="{
                        active: selectedStat === stat,
                        disabled: stat === 'gpu' && !hasGPU
                    }" :disabled="stat === 'gpu' && !hasGPU">
                        {{ stat.toUpperCase() }}
                    </button>
                    <select v-if="selectedStat === 'gpu' && gpuModels.length > 0" v-model="selectedGpuModel"
                        class="gpu-selector">
                        <option v-for="model in gpuModels" :key="model" :value="model">
                            {{ model }}
                        </option>
                    </select>
                    <div class="selected-name">
                        {{ selectedStat === 'cpu' ? props.systemInfo.cpu : selectedGpuModel }}
                    </div>
                </div>

                <div id="metrics-chart" style="height: 300px; width: 100%"></div>
                <div class="stat-content" v-show="selectedStat === 'cpu'">
                    <div class="metric-row">
                        <div class="metric-item">
                            <span class="metric-label">使用率</span>
                            <span class="metric-value">{{ nodeStatus.cpu.usage }}%</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">频率</span>
                            <span class="metric-value">{{ nodeStatus.cpu.freq }}GHz</span>
                        </div>
                    </div>
                </div>
                <div class="stat-content" v-show="selectedStat === 'gpu'">
                    <div class="metric-row">
                        <div class="metric-item">
                            <span class="metric-label">使用率</span>
                            <span class="metric-value">{{ nodeStatus.gpu.usage }}%</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">温度</span>
                            <span class="metric-value">{{ nodeStatus.gpu.temp }}°C</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">显存使用</span>
                            <span class="metric-value">{{ nodeStatus.gpu.mem_usage }}GHz</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="button-container">
                <button class="close-btn" @click="$emit('close')">关闭面板</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.overlay {
    /*覆盖层样式 */
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
    backdrop-filter: blur(5px);
}

.overlay-content {
    width: 800px;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    margin-top: -25px;
}

.node-title {
    font-size: 40px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 auto;
}

.top-right-tag {
    border-radius: 0 10px 0 12px;
    color: #fff;
    font-family: PingFang HK;
    font-size: 16px;
    font-style: italic;
    font-weight: 500;
    line-height: 13px;
    padding: 6px 9px;
    position: absolute;
    right: -30px;
    top: -5px;
    width: -moz-fit-content;
    width: fit-content;

    &.connected {
        background: linear-gradient(145deg,
                rgba(52, 211, 153, 0.9) 0%,
                rgba(16, 185, 129, 0.95) 100%);
    }

    &.disconnected {
        background: linear-gradient(145deg,
                rgba(156, 163, 175, 0.9) 0%,
                rgba(107, 114, 128, 0.95) 100%);
    }
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 5px;
    border-bottom: 1px solid #eee;
}

.node-address {
    font-size: 12px;
    /* 缩小字体 */
    color: #7f8c8d;
    /* 改为灰色 */
}

.service-tags {
    display: flex;
    gap: 10px;

    &.compact {
        gap: 8px;
        /* 缩小间距 */
    }

    .service-tag {
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 12px;

        &.active {
            background: #e1f3d8;
            color: #67c23a;
        }

        &.inactive {
            background: #ebeef5;
            color: #909399;
        }

        &.small {
            padding: 4px 10px;
            /* 缩小内边距 */
            font-size: 10px;
            /* 缩小字体 */
            border-radius: 10px;
            /* 调整圆角 */
        }
    }
}

.status-panel {
    background: rgba(245, 245, 245, 0.6);
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    position: relative;
}

.stat-switcher {
    position: absolute;
    left: 15px;
    top: 15px;
    display: flex;
    flex-wrap: wrap;
    /* 允许换行 */
    gap: 8px;
    align-items: center;

    button {
        padding: 4px 12px;
        border-radius: 6px;
        border: 1px solid #ddd;
        background: white;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s;

        &.active {
            background: #4B9BFF;
            color: white;
            border-color: transparent;
        }
    }
}

.stat-switcher button.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #f0f0f0;
    border-color: #ddd;
    color: #999;
}

.stat-switcher button.disabled:hover {
    background: #f0f0f0;
    transform: none;
    box-shadow: none;
}

.gpu-selector {
    margin-left: 10px;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    background: white;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
        border-color: #4B9BFF;
    }
}

.selected-name {
    margin-left: 15px;
    font-size: 12px;
    color: #666;
    padding: 4px 8px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-content {
    margin-top: 40px;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.metric-item {
    background: rgba(255, 255, 255, 0.9);
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.metric-label {
    display: block;
    color: #7f8c8d;
    font-size: 12px;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
}

.button-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.close-btn {
    padding: 10px 30px;
    border-radius: 25px;
    background: #4B9BFF;
    color: white;
    border: none;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
        background: #3685e6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(75, 155, 255, 0.3);
    }
}
</style>