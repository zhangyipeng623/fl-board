<script setup lang="ts">
import { ref, onUnmounted, watch } from 'vue';
import { center } from '@/utils/utils';
import axios from 'axios';

const props = defineProps<{
    show: boolean
    job: any
}>();

const emit = defineEmits(['update:show']);

const nodeList = ref<Node[]>([]);
const centerProgress = ref(0);
const nodeProgress = ref({});
const selectedLogSource = ref('center');
const logContent = ref('');

interface Node {
    ip: string;
    port: number;
    node_name: string;
}
interface CenterProgress {
    total: number;
    finished: number;
}
interface NodeProgress {
    ip: string;
    port: number;
    node_name: string;
    total: number;
    finished: number;
}
interface Progress {
    status: string;
    center: CenterProgress;
    nodes: NodeProgress[];
}

const pollInterval = ref<number | null>(null);

const processProgressData = (data: Progress) => {
    // 更新任务状态
    props.job.status = data.status;

    // 计算中心节点进度
    const centerData = data.center;
    centerProgress.value = centerData.total > 0 ? Math.round((centerData.finished / centerData.total) * 100) : 0;

    // 计算各节点进度
    const nodeProgressData = {};
    data.nodes.forEach((node: NodeProgress) => {
        (nodeProgressData as Record<string, number>)[node.node_name] = node.total > 0 ? Math.round((node.finished / node.total) * 100) : 0;
    });
    nodeProgress.value = nodeProgressData;

    // 更新节点列表
    nodeList.value = [
        ...data.nodes.map(node => ({
            ip: node.ip,
            port: node.port,
            node_name: node.node_name,
        }))
    ];
};

const processLogData = (data: { log: string }) => {
    logContent.value = data.log;
};

const fetchProgress = async () => {
    try {
        const res = await center.get(`/job/progress/${props.job.job_id}`);
        if (res.status === 200) {
            processProgressData(res.data);
        }
    } catch (error) {
        console.error('获取进度失败:', error);
    }
};

const fetchLog = async () => {
    try {
        let res;
        if (selectedLogSource.value === 'center') {
            // 中心节点的日志从center请求
            const endpoint = `/job/log/${props.job.job_id}`;
            res = await center.get(endpoint);
        } else {
            // 从节点列表中找到对应的节点
            const selectedNode = nodeList.value.find(node => node.node_name === selectedLogSource.value);
            if (selectedNode) {
                // 直接向对应节点请求日志
                const nodeUrl = `http://${selectedNode.ip}:${selectedNode.port}`;
                res = await axios.get(`${nodeUrl}/job/log/${props.job.job_id}`);
            }
        }

        if (res && res.status === 200) {
            processLogData(res.data);
        }
    } catch (error) {
        console.error('获取日志失败:', error);
    }
};

const startPolling = () => {
    fetchProgress();
    fetchLog();
    pollInterval.value = setInterval(() => {
        fetchProgress();
        fetchLog();
    }, 5000);
};

const stopPolling = () => {
    if (pollInterval.value) {
        clearInterval(pollInterval.value);
        pollInterval.value = null;
    }
};

const handleClose = () => {
    stopPolling();
    emit('update:show', false);
};

const handleLogSourceChange = () => {
    fetchLog();
};

watch(() => props.show, (newVal) => {
    if (newVal) {
        startPolling();
    } else {
        stopPolling();
    }
});

onUnmounted(() => {
    stopPolling();
});

</script>

<template>
    <div v-if="show" class="overlay" @click.self="handleClose">
        <div class="overlay-content">
            <div class="detail-header">
                <h2>任务详情</h2>
            </div>
            <!-- 上部分：左侧任务信息，右侧进度 -->
            <div class="detail-top">
                <el-row :gutter="20">
                    <!-- 左侧：任务基本信息 -->
                    <el-col :span="12" class="info-panel">
                        <h3 class="section-title">任务信息</h3>
                        <el-descriptions :column="1" border>
                            <el-descriptions-item label="任务ID">{{ job.job_id }}</el-descriptions-item>
                            <el-descriptions-item label="上传节点">{{ job.node_name }}</el-descriptions-item>
                            <el-descriptions-item label="关联数据库">{{ job.db_name }}</el-descriptions-item>
                            <el-descriptions-item label="任务状态">
                                <el-tag
                                    :type="job.status === 'finished' ? 'success' : job.status === 'running' ? 'warning' : 'info'"
                                    effect="light">
                                    {{ job.status === 'finished' ? '已完成' : job.status === 'running' ? '运行中' : '等待中' }}
                                </el-tag>
                            </el-descriptions-item>
                            <el-descriptions-item label="输入字段">
                                <div class="field-list">
                                    <el-tag v-for="(field, index) in job.input_field" :key="index" class="field-item"
                                        effect="plain" type="info">
                                        {{ field.field }}: {{ field.type }}
                                    </el-tag>
                                </div>
                            </el-descriptions-item>
                            <el-descriptions-item label="输出字段">
                                <el-tag class="field-item" effect="plain" type="info">
                                    {{ job.output_field.field }}: {{ job.output_field.type }}
                                </el-tag>
                            </el-descriptions-item>
                        </el-descriptions>
                    </el-col>

                    <!-- 右侧：训练进度 -->
                    <el-col :span="12" class="progress-panel">
                        <h3 class="section-title">训练进度</h3>
                        <el-descriptions :column="1" border>
                            <el-descriptions-item label="中心节点进度">
                                <el-progress :percentage="centerProgress" />
                            </el-descriptions-item>
                            <el-descriptions-item v-for="node in nodeList" :key="node.node_name"
                                :label="`${node.node_name} 进度`">
                                <el-progress
                                    :percentage="(nodeProgress as Record<string, number>)[node.node_name] || 0" />
                            </el-descriptions-item>
                        </el-descriptions>
                    </el-col>
                </el-row>
            </div>

            <!-- 下部分：日志内容 -->
            <div class="detail-bottom">
                <div class="log-header">
                    <h3 class="section-title">日志内容</h3>
                    <el-select v-model="selectedLogSource" placeholder="选择日志来源" @change="handleLogSourceChange">
                        <el-option label="中心节点" value="center" />
                        <el-option v-for="node in nodeList" :key="node.node_name" :label="node.node_name"
                            :value="node.node_name" />
                    </el-select>
                </div>
                <div class="log-section">
                    <div class="log-container">
                        <div class="log-content">
                            <pre>{{ logContent }}</pre>
                        </div>
                    </div>
                </div>
            </div>

            <div class="detail-footer">
                <el-button @click="handleClose">关闭</el-button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.overlay-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.detail-header {
    margin-bottom: 20px;
    text-align: center;
}

/* 上部分样式 */
.detail-top {
    margin-bottom: 20px;
}

/* 下部分样式 */
.detail-bottom {
    flex: 1;
    margin-bottom: 20px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
}

.log-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    width: 100%;
}

.log-header .el-select {
    width: 200px;
}

.info-panel,
.progress-panel {
    height: 100%;
    overflow-y: auto;
}

.detail-footer {
    text-align: right;
}

.field-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.field-item {
    margin: 2px;
}

.section-title {
    margin: 10px 0;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
}

.log-section {
    max-height: 450px;
}

.log-container {
    display: flex;
    gap: 10px;
    height: 400px;
}

.log-content {
    flex: 1;
    background-color: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 15px;
    overflow-y: auto;
}

.log-sidebar {
    width: 200px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.log-content pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #303133;
}
</style>