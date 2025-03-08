<template>
    <div class="overlay" @click.self="resetData">
        <div class="overlay-content" v-if="currentOriginalDbIndex === -1">
            <h1 class="form-title">新建对齐规则</h1>

            <el-form label-position="top" class="form-container">
                <!-- 规则名称 -->
                <el-form-item label="规则名称" required>
                    <el-input v-model="rulerName" placeholder="请输入规则名称" clearable class="form-input" />
                </el-form-item>

                <!-- 对齐数据库 -->
                <el-form-item label="对齐数据库" required>
                    <el-input v-model="alignedDb" placeholder="请输入对齐数据库" clearable class="form-input" />
                </el-form-item>

                <!-- 原始数据库选择 -->
                <el-form-item label="源数据库" required>
                    <el-tree-select v-model="originalDb" lazy :props="treeProps" :load="loadNode" multiple
                        class="database-selector" placeholder="请选择源数据库" />
                </el-form-item>

                <!-- 字段定义区域 -->
                <div class="section-header">
                    <h3>字段定义</h3>
                    <el-button @click="addField" type="primary" size="small" class="add-btn">
                        <el-icon>
                            <Plus />
                        </el-icon>添加字段
                    </el-button>
                </div>
                <div class="field-section">


                    <!-- 字段列表 -->
                    <div v-for="(field, index) in alignedField" :key="index" class="field-item">
                        <el-space :size="16">
                            <el-input v-model="field.field" placeholder="字段名称" style="width: 180px" clearable />
                            <el-select v-model="field.type" placeholder="选择类型" style="width: 120px">
                                <el-option label="字符串" value="str" />
                                <el-option label="整数" value="int" />
                                <el-option label="浮点数" value="float" />
                                <el-option label="列表" value="list" />
                            </el-select>
                            <el-button @click="removeField(index)" type="danger" circle size="small" :icon="Delete" />
                        </el-space>
                    </div>
                </div>

                <!-- 操作按钮 -->
                <div class="action-buttons">
                    <el-button type="primary" @click="handleNextStep" class="next-btn">
                        下一步 <el-icon>
                            <ArrowRight />
                        </el-icon>
                    </el-button>
                    <el-button @click="resetData">取消</el-button>
                </div>
            </el-form>
        </div>

        <div v-if="currentOriginalDbIndex >= 0" class="overlay-content">
            <div class="header-container">
                <span class="ruler-title">{{ rulerTitle(originalDb[currentOriginalDbIndex]) }}</span>
            </div>

            <el-card class="database-card">
                <template #header>
                    <div class="card-header">
                        <span class="current-db-label">当前原始数据库:</span>
                        {{ getDbName(originalDb[currentOriginalDbIndex])?.name }}({{
        getDbName(originalDb[currentOriginalDbIndex])?.nodename }})
                    </div>
                </template>

                <div class="ruler-container">
                    <el-row :gutter="20" v-for="(field, index) in alignedFieldArray" :key="index" class="ruler-row">
                        <el-col :span="5">
                            <div class="field-label">
                                <el-text class="field-name">{{ field }}</el-text>
                                <el-text class="field-type" type="info">
                                    ({{ alignedField[index].type }})
                                </el-text>
                            </div>
                        </el-col>
                        <el-col :span="19">
                            <el-space :size="12" class="operator-group">
                                <el-select v-model="selectedOperators[index]" placeholder="运算符" class="operator-select"
                                    style="width: 110px" @change="selectedData[index] = undefined">
                                    <el-option label="+" value="+" />
                                    <el-option label="-" value="-" />
                                    <el-option label="*" value="*" />
                                    <el-option label="/" value="/" />
                                    <el-option label="=" value="=" />
                                    <el-option label="avg" value="avg" />
                                    <el-option label="max" value="max" />
                                    <el-option label="min" value="min" />
                                </el-select>

                                <el-tree-select lazy :props="treeProps" :multiple="isMultiple(index)"
                                    v-model="selectedData[index]" :disabled="!selectedOperators[index]"
                                    :load="(node: Node, resolve: any) => handleLoad(node, resolve, index)"
                                    :key="`tree-select-${index}-${selectedOperators[index]}`" class="data-tree-select"
                                    placeholder="选择字段" clearable />
                            </el-space>
                        </el-col>
                    </el-row>
                </div>
            </el-card>

            <div class="action-buttons">
                <el-button @click="handlePreviousStep" class="step-btn" :disabled="currentOriginalDbIndex === 0">
                    <el-icon>
                        <ArrowLeft />
                    </el-icon>上一步
                </el-button>

                <el-button type="primary" @click="handleNextStep" class="step-btn"
                    v-if="currentOriginalDbIndex < originalDb.length - 1">
                    下一步<el-icon>
                        <ArrowRight />
                    </el-icon>
                </el-button>

                <el-button type="success" @click="handleSubmit" class="submit-btn"
                    v-if="currentOriginalDbIndex === originalDb.length - 1">
                    <el-icon>
                        <Check />
                    </el-icon>{{ isSubmitting ? '正在对齐数据库...' : '提交规则' }}
                </el-button>

                <el-button @click="resetData" class="close-btn">关闭</el-button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { center } from "@/utils/utils";
import type Node from "element-plus/es/components/tree/src/model/node";
import { Delete, Check, Plus, ArrowRight } from '@element-plus/icons-vue'


interface OriginalField {
    field: string;
    file_name: string;
    node_id: number;
    nodename: string
}

interface AlignedField {
    field: string;
    type: string
}

interface Operator {
    db: DB;
    aligned_field: AlignedField;
    operator: string;
    original_field: OriginalField | OriginalField[];
}
const props = defineProps<{
    show: boolean
}>();

interface DB {
    id: number;
    name: string;
    nodename: string;
}

interface RulerEntry {
    db: DB;
    operator: Operator[];
}

type Ruler = RulerEntry[];


const emit = defineEmits(["update:show", "submit-success"]);

const currentOriginalDbIndex = ref(-1);
const rulerName = ref("");
const alignedDb = ref("");
const originalDb = ref([]);
const alignedField = ref<AlignedField[]>([
    {
        field: '',
        type: 'str'
    },
    {
        field: '',
        type: 'str'
    }
]);
const ruler = ref<Ruler>([]);
const selectedOperators = ref<string[]>([]);
const selectedData = ref<any[]>([]);
const isSubmitting = ref(false);
const treeProps = {
    label: "label",
    value: "value",
    children: "children",
    isLeaf: "isLeaf",
};

const rulerTitle = (rulerName: string) => {
    let db = getDbName(rulerName);
    return `${db.name} (${db.nodename}) → ${alignedDb.value}`
};

const isMultiple = (index: number) => {
    const operator = selectedOperators.value[index];
    return (
        operator === "+" || operator === "-" || operator === "*" || operator === "/"
    );
};

const loadNode = async (node: any, resolve: any) => {
    if (node.data.isLeaf) return resolve([]);
    if (node.level === 0) {
        try {
            const res = await center.get("/node/list");
            if (res.status === 200) {
                const formattedNodeList = res.data.node_list.map((item: any) => ({
                    value: item.id,
                    label: item.nodename,
                    disabled: true,
                }));
                resolve(formattedNodeList);
            } else {
                alert("获得数据错误1" + res.data.msg);
            }
        } catch (error) {
            console.log(error);
            alert("获得数据错误2" + error);
        }
    } else if (node.level === 1) {
        try {
            const res = await center.get("/db/list", {
                params: {
                    node_id: node.data.value,
                },
            });
            if (res.status === 200) {
                const formattedDbList = res.data.db_list.map((item: any) => ({
                    ...item,
                    isLeaf: true,
                }));
                resolve(formattedDbList);
            } else {
                alert("获得数据错误3" + res.data.msg);
            }
        } catch (error) {
            alert("获得数据错误4" + error);
        }
    }
};

const handleLoad = async (node: Node, resolve: any, index: number) => {
    if (node.isLeaf) {
        return resolve([]);
    }
    if (node.level == 0) {
        const originalDbList = [];
        if (
            selectedOperators.value[index] === "+" ||
            selectedOperators.value[index] === "-" ||
            selectedOperators.value[index] === "*" ||
            selectedOperators.value[index] === "/" ||
            selectedOperators.value[index] === "="
        ) {
            resolve([
                {
                    value: originalDb.value[currentOriginalDbIndex.value],
                    label: getDbName(originalDb.value[currentOriginalDbIndex.value])
                        ?.name,
                    disabled: true,
                },
            ]);
        } else {
            for (let i = 0; i < originalDb.value.length; i++) {
                originalDbList.push({
                    value: originalDb.value[i],
                    label: getDbName(originalDb.value[i])?.name,
                    disabled: true,
                });
            }
            resolve(originalDbList);
        }
    } else {
        try {
            const res = await center.get("/db/field", {
                params: {
                    db: node.data.value,
                },
            });
            if (res.status === 200) {
                if (selectedOperators.value[index] === "=") {
                    const formattedNodeList = res.data.field_list.map((item: any) => ({
                        ...item,
                        isLeaf: true,
                    }));
                    resolve(formattedNodeList);
                } else {
                    const formattedNodeList = res.data.field_list
                        .filter((item: any) => item.label.endsWith('int') || item.label.endsWith('float'))
                        .map((item: any) => ({
                            ...item,
                            isLeaf: true,
                        }));
                    resolve(formattedNodeList);
                }

            } else {
                alert("获得数据错误5" + res.data.msg);
            }
        } catch (error) {
            console.log(error);
            alert("获得数据错误6" + error);
        }
    }
};

const handleNextStep = async () => {

    if (currentOriginalDbIndex.value === -1) {
        if (rulerName.value === "") {
            alert("请输入对齐规则名称");
            return;
        }
        if (alignedDb.value === "") {
            alert("请输入对齐数据库名称");
            return;
        }
        if (originalDb.value.length === 0) {
            alert("请选择原始数据库");
            return;
        }
        let fieldNames = new Set();
        for (const item of alignedField.value) {
            if (item.field === "") {
                alert("请输入对齐字段");
                return;
            }
            if (fieldNames.has(item.field)) {
                alert("字段名称不能重复");
                return;
            }
            fieldNames.add(item.field);
        }
        for (let i = 0; i < originalDb.value.length; i++) {
            const dbName = getDbName(originalDb.value[i]); // 获取当前数据库名称
            // 初始化 ruler 中的每个 dbName 为一个空数组
            if (!ruler.value.find((item) => item.db === dbName)) {
                ruler.value.push({
                    db: dbName,
                    operator: [],
                });
            }
        }
        currentOriginalDbIndex.value = 0;
    } else if (currentOriginalDbIndex.value < originalDb.value.length - 1) {
        const currentDb = getDbName(originalDb.value[currentOriginalDbIndex.value]);
        ruler.value[currentOriginalDbIndex.value].operator = [];
        for (let i = 0; i < alignedFieldArray.value.length; i++) {
            if (selectedOperators.value[i] === undefined) {
                alert("请选择对齐字段符号(" + alignedFieldArray.value[i] + ")");
                return;
            }
            if (selectedData.value[i] === undefined) {
                alert("请选择对齐字段值(" + alignedFieldArray.value[i] + ")");
                return;
            }
            console.log(selectedData.value[i])
            ruler.value[currentOriginalDbIndex.value].operator.push({
                db: currentDb,
                aligned_field: alignedField.value[i],
                operator: selectedOperators.value[i],
                original_field: OriginalFieldArray(i),
            });
        }
        selectedOperators.value = [];
        selectedData.value = [];
        currentOriginalDbIndex.value++;
    }
};

const handlePreviousStep = () => {
    if (currentOriginalDbIndex.value >= 0) {
        selectedOperators.value = [];
        selectedData.value = [];
    }
    currentOriginalDbIndex.value--;
};

const handleSubmit = async () => {
    const currentDb = getDbName(originalDb.value[currentOriginalDbIndex.value]);
    ruler.value[currentOriginalDbIndex.value].operator = [];
    for (let i = 0; i < alignedFieldArray.value.length; i++) {
        if (selectedOperators.value[i] === undefined) {
            alert("请选择对齐字段符号(" + alignedFieldArray.value[i] + ")");
            return;
        }
        if (selectedData.value[i] === undefined) {
            alert("请选择对齐字段值(" + alignedFieldArray.value[i] + ")");
            return;
        }
        ruler.value[currentOriginalDbIndex.value].operator.push({
            db: currentDb,
            aligned_field: alignedField.value[i],
            operator: selectedOperators.value[i],
            original_field: OriginalFieldArray(i),
        });
    }
    try {
        isSubmitting.value = true;
        const res = await center.post("/ruler/add", {
            ruler_name: rulerName.value,
            aligned_db: alignedDb.value,
            original_db: originalDb.value.map(db => JSON.parse(db)),
            field: alignedField.value,
            ruler: ruler.value,
        });
        if (res.status === 200) {
            selectedOperators.value = [];
            selectedData.value = [];
            alert("提交规则成功");
            currentOriginalDbIndex.value = -2;
            handleSubmitSuccess()
        }
    } catch (error) {
        ruler.value[currentOriginalDbIndex.value].operator = [];
        selectedOperators.value = [];
        selectedData.value = [];
        alert("提交规则失败" + error);
    } finally {
        isSubmitting.value = false;
    }
};

const getDbName = (original_db: string): DB => {
    return JSON.parse(original_db);
};

// 在提交成功后触发父组件的更新
const handleSubmitSuccess = () => {
    resetData();
    emit("submit-success");
};

// 添加新的方法
const addField = () => {
    alignedField.value.push({
        field: '',
        type: 'str'
    });
};

const removeField = (index: number) => {
    alignedField.value.splice(index, 1);
};

// 修改 resetData 方法
const resetData = () => {
    rulerName.value = "";
    alignedDb.value = "";
    alignedField.value = []; // 清空字段数组
    originalDb.value = [];
    currentOriginalDbIndex.value = -1;
    selectedOperators.value = [];
    selectedData.value = [];
    ruler.value = [];
    emit("update:show", false);
};

// 修改 alignedFieldArray 计算属性
const alignedFieldArray = computed(() => {
    return alignedField.value.map(field => field.field);
});

const OriginalFieldArray = (index: number) => {
    if (isMultiple(index)) {
        if (selectedData.value[index].length >= 1) {
            return selectedData.value[index].map((item: string) => JSON.parse(item))
        } else {
            alert("请选择原始字段值(" + alignedFieldArray.value[index] + ")");
            return [];
        }
    } else {
        return JSON.parse(selectedData.value[index])
    }

}
</script>

<style scoped>
.form-title {
    color: #2c3e50;
    margin-bottom: 2rem;
    text-align: center;
}

.form-container {
    width: 100%;
    max-width: 680px;
}

.form-input {
    width: 100%;
    margin-bottom: 1.5rem;
}

.database-selector {
    width: 100%;
    margin-bottom: 2rem;
}

.field-section {
    border: 1px solid #ebeef5;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    background: #fafafa;
    max-height: 250px;
    overflow-y: auto;
}

.field-item {
    padding: 1rem;
    margin: 0.5rem 0;
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    /* 加强阴影效果 */
    border: 1px solid #ebeef5;
    /* 增加边框 */
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
    width: 800px;
    padding: 30px;
    border-radius: 16px;
    background: linear-gradient(145deg, #f8f9fa, #ffffff);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

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

/* 优化标题文字样式 */
.ruler-title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.field-item {
    padding: 1rem;
    margin: 0.5rem 0;
    background: white;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;
}

.next-btn {
    padding: 12px 24px;
    font-size: 14px;
}

.add-btn {
    margin-left: auto;
}

/* 优化现有样式 */
.overlay-content {
    width: 720px;
    padding: 2rem 3rem;
}

.ruler-input {
    align-items: center;
    margin: 1rem 0;
}

.ruler-input span {
    width: 120px;
    font-size: 14px;
    color: #606266;
}

.data-tree-select {
    width: 250px !important;
}

:deep(.el-select-dropdown) {
    min-width: 300px !important;
}
</style>
