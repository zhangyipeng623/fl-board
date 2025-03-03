<template>
    <el-card class="node-card" body-class="card-body">
        <!-- 状态标签部分保持不变 -->
        <div v-if="showStatusTag" :class="{
            'online-tag': node.is_connect,
            'offline-tag': !node.is_connect
        }" class="top-right-tag">
            {{ node.is_connect ? "在线" : "离线" }}
        </div>

        <div class="card-content">
            <div class="node-header">
                <span class="node-name">
                    <span v-if="isLocation" class="location-tag">本机</span>
                    {{ node.name }}
                </span>
                <span class="node-address">{{ node.ip }}:{{ node.port }}</span>
            </div>

            <!-- 系统信息封装 -->
            <div v-if="systemInfo?.length" class="system-info">
                <div v-for="(info, index) in systemInfo" :key="index" class="info-item">
                    <span class="info-label">{{ info.label }}</span>
                    <span class="info-value">{{ info.value }}</span>
                </div>
            </div>

            <!-- 保留自定义插槽 -->
        </div>

        <!-- 悬停按钮部分保持不变 -->
        <div v-if="showHoverButton" class="hover-button">
            <el-button type="primary" size="default" @click.stop="emit('click')">
                点击查看详情
            </el-button>
        </div>
    </el-card>
</template>

<script setup lang="ts">
import type { DbNode } from "@/utils/settings";

const props = defineProps({
    node: {
        type: Object as () => DbNode,
        required: true
    },
    showHoverButton: {
        type: Boolean,
        default: true
    },
    showStatusTag: {
        type: Boolean,
        default: true
    },
    systemInfo: {
        type: Array as () => Array<{ label: string, value: string }>,
        default: () => []
    },
    isLocation: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['click']);
</script>

<style scoped>
.location-tag {
    background: #4B9BFF;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    margin-right: 8px;
    vertical-align: middle;
}

.node-card {
    padding: 10px;
    width: 23%;
    height: 230px;
    margin: 10px;
    cursor: pointer;
    background: linear-gradient(145deg,
            rgba(255, 255, 255, 0.85) 0%,
            rgba(255, 255, 255, 0.95) 100%);
    backdrop-filter: blur(6px);
    animation: fadeIn-_7d981 .5s ease-in-out;
    border: 1px solid #eaedf1;
    border-radius: 12px;
    box-shadow: 0 2px 6px 0 rgba(0, 0, 0, .04);
    min-width: 100px;
    overflow: hidden;
    padding: 16px;
    position: relative;
    overflow: visible !important;
    transition: all .3s ease-in-out;
    z-index: 1;
}

.node-card:hover {
    transform: translateY(-2px) scale(1.02);
    background: linear-gradient(220deg, #f3f7ff .79%, #fff 63.4%);
    border: 1px solid rgba(24, 81, 238, 0.6);
    z-index: 3;
    /* 白色主题悬停加强阴影 */
    box-shadow: 0 15px 35px -2px rgba(72, 117, 231, .1), 0 5px 15px 0 rgba(66, 81, 162, .1)
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
    right: 0;
    top: 0;
    z-index: -1;
    width: -moz-fit-content;
    width: fit-content;
}

.online-tag {
    background: linear-gradient(145deg,
            rgba(52, 211, 153, 0.9) 0%,
            rgba(16, 185, 129, 0.95) 100%);
}

.offline-tag {
    background: linear-gradient(145deg,
            rgba(156, 163, 175, 0.9) 0%,
            rgba(107, 114, 128, 0.95) 100%);
}

.hover-button {
    position: absolute;
    bottom: -5px;
    /* 初始位置更低 */
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition:
        opacity 0.3s ease,
        bottom 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    /* 更平滑的动画曲线 */
    pointer-events: auto;
    z-index: 4;
    /* 确保在卡片上方 */
    width: max-content;
}

.node-card:hover .hover-button {
    opacity: 1;
    /* 最终位置上移 */
    bottom: 5px;
}

.hover-button .el-button {
    background: rgba(64, 158, 255, 0.9);
    backdrop-filter: blur(2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

:deep(.card-body) {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}

.card-content {
    height: calc(100% - 30px);
    overflow: visible;
    position: relative;
    z-index: 1;
    /* 保留底部状态栏空间 */
}

.node-header {
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    text-align: center;
}

.node-name {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    display: block;
    margin-bottom: 4px;
    text-align: center;
}

.node-address {
    font-size: 12px;
    color: #7f8c8d;
    display: block;
    text-align: left
}

.system-info {
    margin: 15px 0;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 5px 0;
    padding: 6px 10px;
    background: rgba(245, 245, 245, 0.5);
    border-radius: 6px;
}

.info-label {
    font-size: 12px;
    color: #95a5a6;
    font-weight: 500;
}

.info-value {
    font-size: 13px;
    color: #34495e;
    font-weight: 600;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 其他原有样式保持不变 */
</style>