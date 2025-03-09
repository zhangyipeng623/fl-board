<script setup lang="ts">
import { ref, watch } from "vue";
import { center } from "@/utils/utils";
import Prism from "prismjs";
import "prismjs/components/prism-python.min.js";
import "prismjs/themes/prism.css";

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    netId: {
        type: Number,
        required: true
    }
});

const emit = defineEmits(['update:visible']);

const code = ref("");
const isLoading = ref(false);

const fetchNetDetail = async () => {
    if (!props.netId) return;

    isLoading.value = true;
    try {
        const res = await center.get("/net/detail", {
            params: {
                session: localStorage.getItem("userSession"),
                net_id: props.netId,
            },
        });

        code.value = Prism.highlight(
            res.data.code,
            Prism.languages.python,
            "python"
        );

        // 确保代码高亮应用
        setTimeout(() => {
            Prism.highlightAll();
        }, 0);

    } catch (error) {
        console.error("请求数据失败:", error);
    } finally {
        isLoading.value = false;
    }
};

const closeDialog = () => {
    emit('update:visible', false);
};

watch(() => props.visible, (newVal) => {
    if (newVal && props.netId) {
        fetchNetDetail();
    }
}, { immediate: true });
</script>

<template>
    <div v-if="visible" class="overlay" @click.self="closeDialog">
        <div class="overlay-content">
            <div class="detail-header">
                <h2>网络模型详情</h2>
            </div>

            <div class="code-container">
                <div v-if="isLoading" class="loading">加载中...</div>
                <pre v-else v-html="code"></pre>
            </div>

            <div class="detail-footer">
                <el-button @click="closeDialog">关闭</el-button>
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
    width: 800px;
    max-height: 80vh;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.detail-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 24px;
}

.detail-header h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
}

.code-container {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 24px;
    max-height: 60vh;
}

.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: #909399;
    font-size: 16px;
}

.detail-footer {
    display: flex;
    justify-content: center;
    padding-top: 16px;
}
</style>