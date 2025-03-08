<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import type { DbNode } from "@/utils/settings";
import * as echarts from 'echarts';


const props = defineProps<{
    node: DbNode | null
    isCenterNode: boolean
}>()

const nodeInfo = ref({
    mysql: "false",
    redis: "false",
    nginx: "false"
})
const selectedStat = ref<'cpu' | 'gpu'>('cpu')
const selectedGpuModel = ref<string>('') // 当前选中的GPU型号
const gpuModels = ref<string[]>([]) // 存储可用的GPU型号列表
const hasGPU = ref(false);

// 添加metricsHistory的声明
type MetricPoint = { time: string; value: number };
const metricsHistory = ref<{
    cpu: MetricPoint[];
    gpu: Record<string, MetricPoint[]>;
    gpu_mem: Record<string, MetricPoint[]>;
}>({
    cpu: [],
    gpu: {},
    gpu_mem: {},
});

// 添加nodeStatus的声明
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

// 添加updateHistory函数
const updateHistory = (arr: MetricPoint[], newVal: number, time: string) => {
    return [...arr.slice(-49), { time, value: newVal }]; // 保留50个数据点
};

// 修改系统信息状态
const systemInfo = ref({
    cpuName: ''
});

let chart: echarts.ECharts | null = null;
let socket: WebSocket | null = null;

const initChart = () => {
    const dom = document.getElementById('metrics-chart');
    if (!dom) return;

    if (!chart) {
        chart = echarts.init(dom);
    }

    const currentData = selectedStat.value === 'cpu'
        ? metricsHistory.value.cpu
        : (metricsHistory.value.gpu[selectedGpuModel.value] || []);

    // 更新图表配置
    chart.setOption({
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: currentData.map(i => i.time)
        },
        yAxis: {
            type: 'value',
            axisLabel: {
                formatter: '{value}%'
            },
            max: 100
        },
        series: [{
            type: 'line',
            data: currentData.map(i => i.value),
            smooth: true,
            showSymbol: false,
            itemStyle: {
                color: '#409EFF'
            }
        }]
    });
};

// 添加一个新的 ref 来存储 GPU 信息
const gpuInfo = ref<Record<string, any>>({});

// 使用WebSocket替代轮询
const setupWebSocket = () => {
    if (!props.node?.ip || !props.node?.port) return;

    // 关闭已存在的连接
    if (socket) {
        socket.close();
    }

    // 创建新的WebSocket连接
    socket = new WebSocket(`ws://${props.node.ip}:${props.node.port}/node/ws`);

    socket.onopen = () => {
        console.log('WebSocket连接已建立');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        processMetricsData(data);
    };

    socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
        // 连接失败时尝试使用HTTP轮询作为备选方案
        // fetchMetrics();
    };

    socket.onclose = () => {
        console.log('WebSocket连接已关闭');
    };
};

// 处理接收到的指标数据
const processMetricsData = (res: any) => {
    const now = new Date().toLocaleTimeString();

    // 更新CPU名称
    systemInfo.value.cpuName = res.cpu.name || '未知CPU';

    // 更新CPU数据
    metricsHistory.value.cpu = updateHistory(
        metricsHistory.value.cpu,
        res.cpu.cpu_usage,
        now
    );

    nodeStatus.value.cpu = {
        usage: res.cpu.cpu_usage,
        temp: res.cpu.temp || 0,
        freq: res.cpu.cpu_freq
    };

    // GPU 处理
    if (res.gpu_info && Object.keys(res.gpu_info).length > 0) {
        gpuInfo.value = res.gpu_info;
        const gpuList = Object.keys(res.gpu_info);
        gpuModels.value = gpuList;
        hasGPU.value = true;

        if (gpuList.length > 0 && (!selectedGpuModel.value || !gpuList.includes(selectedGpuModel.value))) {
            selectedGpuModel.value = gpuList[0];
        }

        // 为每个 GPU 更新数据
        gpuList.forEach(gpuKey => {
            const gpu = res.gpu_info[gpuKey];
            if (gpu) {
                // 初始化该 GPU 的历史数据数组（如果不存在）
                if (!metricsHistory.value.gpu[gpuKey]) {
                    metricsHistory.value.gpu[gpuKey] = [];
                }
                if (!metricsHistory.value.gpu_mem[gpuKey]) {
                    metricsHistory.value.gpu_mem[gpuKey] = [];
                }

                // 计算GPU使用率
                const gpuUsage = Number(((gpu.used / gpu.total) * 100).toFixed(1));

                // 更新GPU使用率历史
                metricsHistory.value.gpu[gpuKey] = updateHistory(
                    metricsHistory.value.gpu[gpuKey],
                    gpuUsage,
                    now
                );

                // 如果是当前选中的 GPU，更新状态显示
                if (gpuKey === selectedGpuModel.value) {
                    nodeStatus.value.gpu = {
                        usage: gpuUsage,
                        temp: gpu.temperature,
                        mem_usage: `${(gpu.used / 1024).toFixed(1)}/${(gpu.total / 1024).toFixed(1)}GB`
                    };
                }
            }
        });
    }

    // 使用 setTimeout 确保 DOM 已更新
    setTimeout(() => {
        initChart();
    }, 0);
};


// 添加监听器，当切换 CPU/GPU 时更新图表
watch(selectedStat, () => {
    setTimeout(() => {
        initChart();
    }, 0);
});

// 修改 GPU 监听器
watch(selectedGpuModel, (newGpu) => {
    if (newGpu && gpuInfo.value[newGpu]) {
        const gpu = gpuInfo.value[newGpu];
        nodeStatus.value.gpu = {
            usage: Number(((gpu.used / gpu.total) * 100).toFixed(1)),
            temp: gpu.temperature,
            mem_usage: `${(gpu.used / 1024).toFixed(1)}/${(gpu.total / 1024).toFixed(1)}GB`
        };
        setTimeout(() => {
            initChart();
        }, 0);
    }
});

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
    setupWebSocket();
});

onUnmounted(() => {
    // 组件卸载时关闭WebSocket连接
    if (socket) {
        socket.close();
        socket = null;
    }
    // 销毁图表实例
    if (chart) {
        chart.dispose();
        chart = null;
    }
});

// 监听节点变化，重新建立WebSocket连接
watch(() => props.node, (newNode) => {
    if (newNode) {
        setupWebSocket();
    }
}, { deep: true });
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
                <div class="stat-header">
                    <div class="stat-switcher">
                        <button v-for="stat in ['cpu', 'gpu'] as const" :key="stat" @click="selectedStat = stat" :class="{
        active: selectedStat === stat,
        disabled: stat === 'gpu' && !hasGPU
    }" :disabled="stat === 'gpu' && !hasGPU">
                            {{ stat.toUpperCase() }}
                        </button>
                        <select v-if="selectedStat === 'gpu' && gpuModels.length > 0" v-model="selectedGpuModel"
                            class="gpu-selector">
                            <option v-for="key in gpuModels" :key="key" :value="key">
                                {{ key }}
                            </option>
                        </select>
                        <div class="selected-name">
                            {{ selectedStat === 'cpu' ?
        systemInfo.cpuName :
        (gpuInfo[selectedGpuModel]?.name || '') }}
                        </div>
                    </div>
                </div>

                <div class="chart-container">
                    <div id="metrics-chart" style="height: 300px; width: 100%"></div>
                </div>
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
                            <span class="metric-value">{{ nodeStatus.gpu.mem_usage }}</span>
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
}

.stat-switcher {
    position: static;
    /* 移除绝对定位 */
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}

.chart-container {
    margin-top: 20px;
    /* 增加与按钮的间距 */
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

.gpu-selector {
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    margin-left: 8px;
}

.selected-name {
    margin-left: 10px;
    font-size: 14px;
    color: #606266;
}
</style>