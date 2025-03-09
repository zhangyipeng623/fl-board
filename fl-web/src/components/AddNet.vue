<script setup lang="ts">
import { ref, computed } from "vue";
import { Plus, QuestionFilled } from "@element-plus/icons-vue";
import { state } from "@/utils/settings";
import { genFileId } from 'element-plus';
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:visible', 'refresh']);

const netName = ref("");
const inputNum = ref("");
const outputNum = ref("");
const detail = ref("");

const uploadUrl = computed(() => {
    return (
        "http://" +
        state.center.ip +
        ":" +
        state.center.port +
        "/net/upload"
    );
});

const uploadHeaders = computed(() => {
    return {
        "Authorization": localStorage.getItem("userSession"),
    };
});

const beforeUpload = (file: File): boolean => {
    const isPY = file.name.endsWith(".py");
    if (!isPY) {
        alert("上传文件只能是 py 格式!");
        return false;
    }
    return true;
};

const uploadRef = ref<UploadInstance>();
const isUploading = ref(false);

const handleUpload = () => {
    if (!netName.value.trim()) {
        alert('请输入网络名称');
        return;
    }
    isUploading.value = true;
    uploadRef.value!.submit();
};

const handleUploadSuccess = (res: any) => {
    isUploading.value = false;
    refreshData();
    emit('update:visible', false);
    emit('refresh');
};

const handleUploadError = (err: any, file: any) => {
    isUploading.value = false;
    console.error("上传失败:", err);
    alert(`上传失败: ${file.name} - ${err.message || "未知错误"}`);
};

const handleExceed: UploadProps['onExceed'] = (files) => {
    uploadRef.value!.clearFiles();
    const file = files[0] as UploadRawFile;
    file.uid = genFileId();
    uploadRef.value!.handleStart(file);
};
const refreshData = () => {
    netName.value = "";
    inputNum.value = "";
    outputNum.value = "";
    detail.value = "";
};

const closeDialog = () => {
    refreshData();
    emit('update:visible', false);
};
</script>

<template>
    <div v-if="visible" class="overlay" @click.self="closeDialog">
        <div class="overlay-content">
            <div class="upload-header">
                <h2>上传深度网络模型</h2>
            </div>
            <div class="upload-body">
                <el-form label-position="top">
                    <el-form-item label="网络名称" required>
                        <el-input v-model="netName" placeholder="请输入网络名称" />
                    </el-form-item>
                    <el-form-item label="输入参数量" required>
                        <el-input v-model="inputNum" placeholder="请输入输入参数量" />
                    </el-form-item>
                    <el-form-item label="输出参数量" required>
                        <el-input v-model="outputNum" placeholder="请输入输出参数量" />
                    </el-form-item>
                    <el-form-item label="模型描述">
                        <el-input v-model="detail" type="textarea" :rows="3" placeholder="请输入模型描述（网络结构、适用场景等）"
                            show-word-limit maxlength="200" />
                    </el-form-item>
                </el-form>

                <div class="upload-area">
                    <el-upload ref="uploadRef" class="upload-demo" :action="uploadUrl" :auto-upload="false"
                        :headers="uploadHeaders" :before-upload="beforeUpload" :on-success="handleUploadSuccess"
                        :on-error="handleUploadError" :limit="1" :on-exceed="handleExceed" :data="{
        netName: netName,
        inputNum: inputNum,
        outputNum: outputNum,
        detail: detail,
        user_id: state.user.id,
    }" accept=".py">
                        <template #trigger>
                            <el-button type="primary" class="upload-button">
                                <el-icon>
                                    <Plus />
                                </el-icon>
                                选择 Python 文件
                            </el-button>
                            <div class="upload-info">
                                <div class="upload-tip">仅支持 .py 格式文件</div>
                                <el-tooltip effect="light"
                                    content="python文件中需要包含Net类和transform_x、transform_y、get_optimizer、get_criterion函数"
                                    placement="bottom">
                                    <el-icon class="tip-icon">
                                        <QuestionFilled />
                                    </el-icon>
                                </el-tooltip>
                            </div>
                        </template>
                    </el-upload>
                </div>

                <div class="upload-footer">
                    <el-button type="primary" @click="handleUpload" :loading="isUploading">
                        {{ isUploading ? '上传中...' : '开始上传' }}
                    </el-button>
                    <el-button @click="closeDialog">取消</el-button>
                </div>
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
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.upload-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 24px;
}

.upload-header h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
}

.upload-body {
    padding: 24px;
}

.upload-area {
    margin: 24px 0;
    padding: 20px;
    border: 1px dashed var(--el-border-color);
    border-radius: 8px;
    text-align: center;
    width: 100%;
}

.upload-demo {
    width: 100%;
}

.upload-info {
    margin-left: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.upload-tip {
    color: #909399;
    font-size: 14px;
}

.tip-icon {
    color: var(--el-color-primary);
    cursor: pointer;
}

.upload-footer {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
}
</style>