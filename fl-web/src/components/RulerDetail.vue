<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { center } from '@/utils/utils';
import { getTypeTagStyle } from "@/utils/styleUtils"; // 添加类型样式工具

const props = defineProps<{
    show: boolean
    alignedDb: string
    db: DB
    id: number
}>();
interface OriginalField {
    field: string;
    file_name: string;
    node_id: number;
    nodename: string;
}

interface Operator {
    db: DB;
    aligned_field: {
        field: string;
        type: string;
    };
    operator: string;
    original_field: OriginalField | OriginalField[]; // 支持数组类型
}

interface DB {
    id: number;
    name: string;
    nodename: string;
}
const operator = ref<Operator[]>([]);
const emit = defineEmits(['update:show']);
const rulerTitle = ref('');

const loadData = async () => {
    const res = await center.get("/ruler/detail", {
        params: {
            data: JSON.stringify({
                ruler_id: props.id,
                original_db: JSON.stringify(props.db)
            })
        },
    })
    if (res.status === 200) {
        operator.value = res.data.operator;
        console.log(operator)
        // 设置标题
        rulerTitle.value = `${props.db.name} (${props.db.nodename}) → ${props.alignedDb}`;
    } else {
        console.log(res.data.msg);
    };
}

onMounted(() => {
    loadData();
});

const handleClose = () => {
    emit('update:show', false);
};

// 新增辅助方法处理字段展示
// 修改辅助方法
const formatOriginalFields = (fields: OriginalField | OriginalField[], operator: string) => {
    const formatWithUsername = (f: OriginalField) => {
        // 当操作符是聚合函数时显示用户名
        return ['avg', 'max', 'min', 'sum'].includes(operator.toLowerCase())
            ? `${f.field} (${f.nodename})`
            : f.field;
    };

    if (Array.isArray(fields)) {
        return fields.map(f => formatWithUsername(f)).join(` ${operator} `);
    }
    return formatWithUsername(fields);
};
</script>

<template>
    <div class="overlay" @click.self="handleClose">
        <div class="overlay-content">
            <div class="header-container">
                <span class="ruler-title">{{ rulerTitle }}</span>
            </div>

            <div class="rule-container">
                <div v-for="(rule, index) in operator" :key="index" class="rule-item">
                    <div class="field-pair">
                        <!-- 修改原始字段部分 -->
                        <div class="field-box original">
                            <span class="field-name">
                                {{ formatOriginalFields(rule.original_field, rule.operator) }}
                            </span>
                        </div>

                        <!-- 操作符箭头保持不变 -->
                        <span class="operator-arrow">→</span>

                        <!-- 对齐字段保持不变 -->
                        <div class="field-box aligned">
                            <span class="field-name">{{ rule.aligned_field.field }}</span>
                            <el-tag size="small" effect="dark" :type="getTypeTagStyle(rule.aligned_field.type)">
                                {{ rule.aligned_field.type }}
                            </el-tag>
                        </div>
                    </div>
                    <div class="operator-sign">
                        {{ rule.operator === '=' ? '' : rule.operator }}
                    </div>
                </div>
            </div>

            <div class="button-container">
                <el-button @click="handleClose">关闭</el-button>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 修正标题容器样式 */
.header-container {
    width: 100%;
    display: flex;
    justify-content: center;
    /* 新增居中属性 */
    position: relative;
    /* 保持相对定位 */
    margin-bottom: 20px;
    padding: 20px 0;
    /* 增加内边距 */
    border-bottom: 1px solid #ebeef5;
}

/* 调整关闭按钮定位 */
.close-btn {
    position: absolute;
    right: 20px;
    /* 从边缘保持间距 */
    top: 50%;
    transform: translateY(-50%);
    /* 垂直居中 */
}

/* 修正按钮容器样式 */
.button-container {
    width: 100%;
    margin-top: 20px;
    display: flex;
    justify-content: center;
    /* 新增居中属性 */
}

/* 标题样式优化 */
.ruler-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 关闭按钮优化 */
.close-btn {
    position: absolute;
    right: -20px;
    top: -20px;
    box-shadow: 0 2px 12px rgba(255, 73, 73, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-btn:hover {
    transform: scale(1.1) rotate(90deg);
    box-shadow: 0 4px 16px rgba(255, 73, 73, 0.4);
}

.rule-container {
    width: 100%;
    margin-top: 20px;
}

.rule-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    margin: 8px 0;
    background: #f8f9fa;
    border-radius: 6px;
    transition: all 0.2s;
}

.rule-item:hover {
    transform: translateX(5px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.field-pair {
    display: flex;
    align-items: center;
    gap: 15px;
}

.field-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 4px;
}

.original .field-name {
    color: #606266;
}

.aligned .field-name {
    color: #409eff;
}

.operator-arrow {
    color: #67c23a;
    font-weight: bold;
}

.operator-sign {
    font-size: 18px;
    color: #e6a23c;
    font-weight: bold;
    margin-left: 20px;
}

.overlay {
    /*覆盖层样式 */
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.45);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(3px);
    /* 添加毛玻璃效果 */
}

.overlay-content {
    align-items: center;
    width: 800px;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.button-container {
    margin-top: 10px;
}

.ruler-title {
    font-size: 30px;
    font-weight: bold;
    text-align: center;
}

/* 新增样式 */
.original .field-name {
    max-width: 200px;
    white-space: normal;
}

.operator-sign {
    min-width: 40px;
    text-align: center;
}
</style>
