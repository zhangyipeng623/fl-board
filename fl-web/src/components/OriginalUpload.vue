<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Upload, Close } from '@element-plus/icons-vue'
import { state } from "@/utils/settings"
import { genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'
interface ColumnInfo {
    name: string
    type: string
}

interface FileInfo {
    name: string
    size: number
    firstLine: string[]
    secondLine?: string[]
}

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
const hasHeader = ref(true)
const tableName = ref("")
const headers = ref<ColumnInfo[]>([])
const fileSelected = ref(false)
const currentFileInfo = ref<FileInfo | null>(null)
const uploadRef = ref<UploadInstance>()

// 计算属性
const uploadUrl = computed(() => {
    return "http://" + state.user.ip + ":" + state.user.port + "/db/upload"
})

const uploadHeaders = {
    authorization: localStorage.getItem("userSession")
}

const detectType = (value: string): string => {
    value = value.trim()
    if (!isNaN(Number(value))) {
        return value.includes('.') ? 'float' : 'int'
    }
    if (value.startsWith('[') && value.endsWith(']')) {
        return 'list'
    }
    if (value.startsWith('array(')) {
        return 'ndarray'
    }
    const dateRegex = /^\d{4}[-/](0?[1-9]|1[012])[-/](0?[1-9]|[12][0-9]|3[01])$/
    if (dateRegex.test(value)) {
        return 'datetime'
    }
    return 'str'
}

const processFileInfo = () => {
    if (!currentFileInfo.value) return

    const { firstLine, secondLine } = currentFileInfo.value
    const dataLine = hasHeader.value ? (secondLine || firstLine) : firstLine
    const headerRow = hasHeader.value ? firstLine : dataLine.map((_, index) => `field${index + 1}`)

    headers.value = headerRow.map((header, index) => ({
        name: header.trim(),
        type: detectType(dataLine[index])
    }))

    fileSelected.value = true
}

const handleFileChange = (uploadFile: any) => {
    headers.value = []
    fileSelected.value = false
    currentFileInfo.value = null
    const file = uploadFile.raw
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
        const content = e.target?.result as string
        const lines = content.split('\n')

        if (lines.length < 1) {
            alert('文件内容不能为空')
            return
        }

        currentFileInfo.value = {
            name: file.name,
            size: file.size,
            firstLine: lines[0].split(','),
            secondLine: lines.length > 1 ? lines[1].split(',') : undefined
        }

        processFileInfo()
    }

    const blob = file.slice(0, 1024 * 1024)
    reader.readAsText(blob)
}

const handleUpload = () => {
    uploadRef.value?.submit()
}

const handleUploadSuccess = () => {
    resetUploadForm()
    emit('upload-success')
}

const handleUploadError = (err: any, file: any) => {
    console.error("上传失败:", err)
    alert(`上传失败: ${file.name} - ${err.message || "未知错误"}`)
}

const resetUploadForm = () => {
    currentFileInfo.value = null
    headers.value = []
    fileSelected.value = false
    tableName.value = ""
    hasHeader.value = true

    if (uploadRef.value) {
        uploadRef.value.clearFiles()
    }
    emit('update:show', false)
}

const handleClose = () => {
    resetUploadForm()
}
watch(hasHeader, () => {
    if (currentFileInfo.value) {
        processFileInfo();
    }
});

const handleExceed: UploadProps['onExceed'] = (files) => {
    uploadRef.value!.clearFiles()
    const file = files[0] as UploadRawFile
    file.uid = genFileId()
    uploadRef.value!.handleStart(file)
    processFileInfo()
}



</script>

<template>
    <div v-if="show" class="overlay" @click.self="handleClose">
        <div class="overlay-content">
            <div class="upload-container">
                <div class="upload-header">
                    <h2>上传数据集</h2>
                    <el-button class="close-button" @click="handleClose">
                        <el-icon>
                            <Close />
                        </el-icon>
                    </el-button>
                </div>

                <div class="upload-body">
                    <el-upload ref="uploadRef" class="upload-area" :action="uploadUrl" :headers="uploadHeaders"
                        :auto-upload="false" :on-success="handleUploadSuccess" :on-error="handleUploadError"
                        :on-exceed="handleExceed" :on-change="handleFileChange" :limit="1" :multiple="false"
                        :drag="false" :data="{
                            hasHeader: hasHeader,
                            table_name: tableName,
                            user_id: state.user.id,
                        }" accept=".csv">
                        <el-button type="primary" class="upload-button">
                            <el-icon class="upload-icon">
                                <Upload />
                            </el-icon>
                            选择文件
                        </el-button>
                        <template #tip>
                            <div class="upload-tip">仅支持 CSV 格式文件</div>
                        </template>
                        <template #file="{ file }">
                            <div class="custom-file-item">
                                <span class="file-name">{{ file.name }}</span>
                                <el-progress v-if="file.status === 'uploading'" :percentage="file.percentage"
                                    class="custom-progress" />
                            </div>
                        </template>
                    </el-upload>

                    <div class="upload-options">
                        <el-form label-position="top">
                            <el-form-item label="数据库名称">
                                <el-input v-model="tableName" placeholder="请输入数据库名称" prefix-icon="Document" />
                            </el-form-item>

                            <el-form-item>
                                <el-checkbox v-model="hasHeader">CSV 文件包含表头</el-checkbox>
                            </el-form-item>

                            <el-form-item v-if="fileSelected" label="检测到的表头">
                                <el-card class="header-card">
                                    <div class="header-list">
                                        <el-tag v-for="(header, index) in headers" :key="index" class="header-tag"
                                            type="info" effect="plain">
                                            {{ header.name }}
                                            <el-tag size="small" type="success" class="type-tag">
                                                {{ header.type }}
                                            </el-tag>
                                        </el-tag>
                                    </div>
                                </el-card>
                            </el-form-item>
                        </el-form>
                    </div>

                    <div class="upload-footer">
                        <el-button type="primary" :icon="Upload" @click="handleUpload">开始上传</el-button>
                        <el-button :icon="Close" @click="handleClose">取消</el-button>
                    </div>
                </div>
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
    width: 100vw;
    /* 修改为视口宽度 */
    height: 100vh;
    /* 修改为视口高度 */
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    /* 提高 z-index 确保覆盖所有元素 */
    backdrop-filter: blur(5px);
}

.overlay-content {
    position: relative;
    /* 添加相对定位 */
    width: 800px;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    /* 确保内容在覆盖层之上 */
}

.upload-container {
    background: white;
    width: 100%;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    overflow: hidden;
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
    /* 改为居中对齐 */
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

/* 在已有的样式后添加以下内容 */
.header-card {
    background-color: var(--el-fill-color-blank);
    border: 1px solid var(--el-border-color-lighter);
}

.header-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 4px;
}

.header-tag {
    margin: 2px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.type-tag {
    font-size: 12px;
    padding: 0 4px;
    height: 20px;
    line-height: 20px;
}

:deep(.el-card__body) {
    padding: 12px;
}

.custom-file-item {
    width: 100%;
    padding: 8px;
    display: flex;
    flex-direction: column;
}

.file-name {
    white-space: normal;
    /* 允许换行 */
    word-break: break-all;
    /* 长单词强制换行 */
    max-height: 3em;
    /* 控制最大显示行数 */
    overflow-y: auto;
    /* 超出部分滚动 */
}
</style>