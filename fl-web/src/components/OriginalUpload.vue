<script setup lang="ts">
import { ref, computed } from 'vue'
import { Upload, Close } from '@element-plus/icons-vue'
import { state } from "@/utils/settings"

// Props 定义
const props = defineProps<{
    show: boolean
}>()

// Emits 定义
const emit = defineEmits<{
    (e: 'update:show', value: boolean): void
    (e: 'upload-success'): void
}>()

// 响应式变量
const tableName = ref("")
const fileType = ref("")
const description = ref("")
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const ws = ref<WebSocket | null>(null)
const chunkSize = 1024 * 1024 // 1MB
const currentChunk = ref(0)
const totalChunks = ref(0)
const uploadProgress = ref(0)
const serverFileName = ref('')
const isUploading = ref(false)
const uploadError = ref('')
const isProcessing = ref(false)  // 新增：文件处理状态

const acceptFileTypes = computed(() => {
    return ".csv,.h5,.hdf5"
})

// 文件选择处理
const handleFileSelect = (event: Event) => {
    const input = event.target as HTMLInputElement
    if (input.files && input.files.length > 0) {
        selectedFile.value = input.files[0]
        uploadProgress.value = 0
        uploadError.value = ''
    }
}

// WebSocket连接
const connectWebSocket = () => {
    if (ws.value) {
        ws.value.close()
    }

    ws.value = new WebSocket(`ws://${state.user.ip}:${state.user.port}/upload_big_file`)

    ws.value.onopen = () => {
        console.log('WebSocket connected')
        startUpload()
    }

    ws.value.onerror = (error) => {
        console.error('WebSocket error:', error)
        uploadError.value = '连接服务器失败'
        isUploading.value = false
    }

    ws.value.onclose = () => {
        console.log('WebSocket closed')
    }

    ws.value.onmessage = (event) => {
        try {
            const response = JSON.parse(event.data)
            if (response.type === 'start') {
                serverFileName.value = response.filename
                uploadNextChunk()
            } else if (response.type === 'chunk') {
                uploadProgress.value = Math.floor((currentChunk.value / totalChunks.value) * 100)
                uploadNextChunk()
            } else if (response.type === 'complete') {
                uploadProgress.value = 100
                handleUploadSuccess()
            } else if (response.type === 'error') {
                uploadError.value = response.message || '上传失败'
                isUploading.value = false
            }
        } catch (e) {
            console.error('解析服务器消息失败:', e)
            uploadError.value = '服务器响应格式错误'
            isUploading.value = false
        }
    }
}

// 开始上传
const handleUpload = () => {
    if (!selectedFile.value) {
        uploadError.value = '请先选择文件'
        return
    }

    if (!tableName.value.trim()) {
        uploadError.value = '请输入数据库名称'
        return
    }

    uploadError.value = ''
    isUploading.value = true
    connectWebSocket()
}

// 开始上传流程
const startUpload = () => {
    if (!selectedFile.value || !ws.value) return

    totalChunks.value = Math.ceil(selectedFile.value.size / chunkSize)
    currentChunk.value = 0
    fileType.value = selectedFile.value.name.split('.').pop() || ''
    // 发送开始信号
    ws.value.send(JSON.stringify({
        type: 'start',
        fileType: fileType.value,
        fileName: selectedFile.value.name,
        totalChunks: totalChunks.value,
    }))
}

// 上传下一个分块
const uploadNextChunk = async () => {
    if (!selectedFile.value || !ws.value) return

    if (currentChunk.value >= totalChunks.value) {
        // 发送结束信号
        ws.value.send(JSON.stringify({
            type: 'stop',
            filename: serverFileName.value,
            fileType: fileType.value,
        }))
        return
    }

    const start = currentChunk.value * chunkSize
    const end = Math.min(start + chunkSize, selectedFile.value.size)
    const chunk = selectedFile.value.slice(start, end)

    try {
        const arrayBuffer = await chunk.arrayBuffer()

        ws.value.send(JSON.stringify({
            type: 'chunk',
            filename: serverFileName.value,
            chunkIndex: currentChunk.value,
            totalChunks: totalChunks.value,
            size: arrayBuffer.byteLength
        }))

        // 发送二进制数据
        ws.value.send(arrayBuffer)

        currentChunk.value++
    } catch (e) {
        console.error('处理文件块失败:', e)
        uploadError.value = '文件读取失败'
        isUploading.value = false
    }
}

// 修改上传成功处理函数
const handleUploadSuccess = () => {
    if (ws.value) {
        ws.value.close()
        ws.value = null
    }

    // 文件上传完成后，提交元数据到 /db/upload
    submitFileMetadata()
}

// 添加提交元数据的函数
// 修改 submitFileMetadata 函数
const submitFileMetadata = async () => {
    if (!serverFileName.value) {
        uploadError.value = '文件上传失败，未获取到服务器文件ID'
        isUploading.value = false
        return
    }

    try {
        isProcessing.value = true  // 开始处理文件
        uploadProgress.value = 100  // 保持进度条显示完成

        // 创建表单数据
        const jsonData = {
            file_name: serverFileName.value,
            db_name: tableName.value,
            user_id: state.user.id,
            detail: description.value,
            file_type: fileType.value,
        }

        // 发送请求
        const response = await fetch(`http://${state.user.ip}:${state.user.port}/db/upload`, {
            method: 'POST',
            headers: {
                'Authorization': localStorage.getItem('userSession') || "",
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '提交元数据失败')
        }

        // 处理成功响应
        isProcessing.value = false  // 处理完成
        isUploading.value = false
        resetUploadForm()
        emit('upload-success')

    } catch (error) {
        console.error('提交元数据失败:', error)
        uploadError.value = `提交元数据失败: ${error instanceof Error ? error.message : '未知错误'}`
        isProcessing.value = false
        isUploading.value = false
    }
}

// 重置表单
const resetUploadForm = () => {
    selectedFile.value = null
    description.value = ""
    tableName.value = ""
    uploadProgress.value = 0
    uploadError.value = ''

    if (fileInput.value) {
        fileInput.value.value = ''
    }

    emit('update:show', false)
}

// 关闭弹窗
const handleClose = () => {
    if (isUploading.value) {
        if (confirm('文件正在上传中，确定要取消吗？')) {
            if (ws.value) {
                ws.value.close()
                ws.value = null
            }
            isUploading.value = false
            resetUploadForm()
        }
    } else {
        resetUploadForm()
    }
}
</script>

<template>
    <div v-if="show" class="overlay" @click.self="handleClose">
        <div class="overlay-content">
            <div class="upload-header">
                <h2>上传数据集</h2>
            </div>
            <div class="upload-body">
                <div class="upload-area">
                    <input ref="fileInput" type="file" :accept="acceptFileTypes" class="file-input"
                        @change="handleFileSelect" :disabled="isUploading" />

                    <el-button type="primary" class="upload-button" @click="() => fileInput?.click()"
                        :disabled="isUploading">
                        <el-icon class="upload-icon">
                            <Upload />
                        </el-icon>
                        选择文件
                    </el-button>

                    <div v-if="selectedFile" class="selected-file">
                        <div class="file-info">
                            <span class="file-name">{{ selectedFile.name }}</span>
                            <span class="file-size">{{ (selectedFile.size / 1024 / 1024).toFixed(3) }} MB</span>
                        </div>

                        <el-progress v-if="uploadProgress > 0" :percentage="uploadProgress"
                            :format="(p: number) => isProcessing ? '文件转化存储中...' : `${p}%`"
                            :status="uploadError ? 'exception' : undefined" />
                    </div>

                    <div v-if="uploadError" class="upload-error">
                        {{ uploadError }}
                    </div>

                    <div class="upload-tip">仅支持 CSV 和 hdf5 格式文件</div>
                </div>

                <div class="upload-options">
                    <el-form label-position="top">
                        <el-form-item label="数据库名称" required>
                            <el-input v-model="tableName" placeholder="请输入数据库名称" prefix-icon="Document"
                                :disabled="isUploading" />
                        </el-form-item>
                        <el-form-item label="详细介绍" prop="description">
                            <el-input v-model="description" type="textarea" :rows="3"
                                placeholder="请输入数据集描述（包含数据来源、采集方式、适用场景等）" show-word-limit maxlength="200"
                                :disabled="isUploading" />
                        </el-form-item>
                    </el-form>
                </div>

                <div class="upload-footer">
                    <el-button type="primary" :icon="Upload" @click="handleUpload" :loading="isUploading"
                        :disabled="!selectedFile || isUploading">
                        {{ isUploading ? '上传中...' : '开始上传' }}
                    </el-button>
                    <el-button :icon="Close" @click="handleClose" :disabled="isUploading">取消</el-button>
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
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    backdrop-filter: blur(5px);
}

.overlay-content {
    position: relative;
    width: 800px;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    z-index: 10000;
}

.upload-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
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
    width: 100%;
    margin-bottom: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.file-input {
    display: none;
}

.upload-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    font-size: 16px;
}

.upload-icon {
    font-size: 20px;
}

.selected-file {
    margin-top: 16px;
    width: 100%;
    padding: 16px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    background-color: var(--el-fill-color-light);
}

.file-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.file-name {
    font-weight: 500;
    white-space: normal;
    word-break: break-all;
    max-height: 3em;
    overflow-y: auto;
}

.file-size {
    color: var(--el-text-color-secondary);
    font-size: 0.9em;
}

.upload-error {
    margin-top: 8px;
    color: var(--el-color-danger);
    font-size: 14px;
    text-align: center;
}

.upload-tip {
    margin-top: 12px;
    color: #909399;
    font-size: 14px;
}

.upload-options {
    margin-bottom: 24px;
}

:deep(.el-form-item__label) {
    font-weight: 500;
}

.upload-footer {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
    padding-bottom: 20px;
}

:deep(.el-button) {
    padding: 10px 30px;
    border-radius: 25px;
    transition: all 0.3s;
}

:deep(.el-button--primary) {
    background: #4B9BFF;

    &:hover {
        background: #3685e6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(75, 155, 255, 0.3);
    }
}

:deep(.el-button--default) {
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
}
</style>