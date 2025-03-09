<script setup lang="ts">
import { ref, watch } from "vue";
import { center } from "@/utils/utils";
import { ArrowLeft, ArrowRight, Check, QuestionFilled } from '@element-plus/icons-vue';

interface RulerField {
    field: string;
    type: string;
}

interface DB {
    id: number;
    aligned_db: string;
    ruler_field: RulerField[];
}

interface Net {
    id: number;
    net_name: string;
    detail: string;
}

const props = defineProps<{
    show: boolean;
}>();

const emit = defineEmits<{
    (e: 'update:show', value: boolean): void;
    (e: 'refresh'): void;
}>();

const db_list = ref<DB[]>([]);
const Field = ref<string[]>([]);
const netList = ref<Net[]>([]);

const inputField = ref([]);
const outputField = ref();
// 添加新的引用来存储字段类型信息
const fieldTypes = ref<Record<string, string>>({});
const db = ref<number>();
const net = ref();

// 新增字段
const round = ref<number>(10); // 交换轮次
const epochs = ref<number>(5); // 节点训练轮数
const currentPage = ref(0); // 当前页面，0表示第一页，1表示第二页

// 第二页字段
const strategy = ref<string>("FedAvg"); // 联邦学习策略
const fraction_fit = ref<number>(1.0); // 每轮训练中参与训练的客户端比例
const fraction_evaluate = ref<number>(1.0); // 每轮评估中参与评估的客户端比例
const min_fit_clients = ref<number>(1); // 每轮训练所需的最少客户端数量
const min_evaluate_clients = ref<number>(1); // 每轮评估所需的最少客户端数量
const min_available_clients = ref<number>(1); // 开始训练前需要连接的最少客户端数量
const min_completion_rate_fit = ref<number>(1.0); // 定义每轮训练中必须成功完成的客户端比例
const min_completion_rate_evaluate = ref<number>(1.0); // 定义每轮评估中必须成功完成的客户端比例
const accept_failure = ref<boolean>(false); // 是否允许部分客户端训练失败

// 策略选项
const strategyOptions = [
    { value: 'FedAvg', label: 'FedAvg' },
    { value: 'FedProx', label: 'FedProx' },
    { value: 'FedAdagrad', label: 'FedAdagrad' },
    { value: 'FedAdam', label: 'FedAdam' },
    { value: 'FedYogi', label: 'FedYogi' },
    { value: 'QFedAvg', label: 'QFedAvg' }
];


watch(db, (newDb) => {
    if (newDb) {
        inputField.value = [];
        outputField.value = [];
        Field.value = get_db_field(newDb);
        // 更新字段类型映射
        updateFieldTypes(newDb);
    }
});

const get_db_field = (db: number) => {
    const db_field = db_list.value.filter((item) => {
        return item.id == db;
    });
    return db_field[0].ruler_field.map(item => item.field);
};

// 添加新函数来更新字段类型映射
const updateFieldTypes = (db: number) => {
    const db_field = db_list.value.find((item) => item.id == db);
    if (db_field) {
        fieldTypes.value = {};
        db_field.ruler_field.forEach(item => {
            fieldTypes.value[item.field] = item.type;
        });
    }
};

const handleClose = () => {
    resetForm();
    emit('update:show', false);
};

const resetForm = () => {
    inputField.value = [];
    outputField.value = [];
    db.value = undefined;
    net.value = undefined;
    round.value = 10;
    epochs.value = 5;
    currentPage.value = 0;
    strategy.value = "FedAvg";
    fraction_fit.value = 1.0;
    fraction_evaluate.value = 1.0;
    min_fit_clients.value = 1;
    min_evaluate_clients.value = 1;
    min_available_clients.value = 1;
    min_completion_rate_fit.value = 1.0;
    min_completion_rate_evaluate.value = 1.0;
    accept_failure.value = false;
};

const handleNextStep = () => {
    if (!net.value) {
        alert('请选择网络模型');
        return;
    }
    if (!db.value) {
        alert('请选择数据库');
        return;
    }
    if (inputField.value.length === 0) {
        alert('请选择输入字段');
        return;
    }
    if (outputField.value.length === 0) {
        alert('请选择输出字段');
        return;
    }
    if (round.value <= 0) {
        alert('交换轮次必须大于0');
        return;
    }
    if (epochs.value <= 0) {
        alert('节点训练轮数必须大于0');
        return;
    }

    currentPage.value = 1;
};

const handlePreviousStep = () => {
    currentPage.value = 0;
};

const handleUpload = async () => {
    // 验证第二页参数
    if (fraction_fit.value <= 0 || fraction_fit.value > 1) {
        alert('训练客户端比例必须在0-1之间');
        return;
    }
    if (fraction_evaluate.value <= 0 || fraction_evaluate.value > 1) {
        alert('评估客户端比例必须在0-1之间');
        return;
    }
    if (min_fit_clients.value < 1) {
        alert('最少训练客户端数量必须大于0');
        return;
    }
    if (min_evaluate_clients.value < 1) {
        alert('最少评估客户端数量必须大于0');
        return;
    }
    if (min_available_clients.value < 1) {
        alert('最少可用客户端数量必须大于0');
        return;
    }
    if (min_completion_rate_fit.value <= 0 || min_completion_rate_fit.value > 1) {
        alert('训练完成率必须在0-1之间');
        return;
    }
    if (min_completion_rate_evaluate.value <= 0 || min_completion_rate_evaluate.value > 1) {
        alert('评估完成率必须在0-1之间');
        return;
    }
    const inputFieldWithTypes = inputField.value.map(field => ({
        field,
        type: fieldTypes.value[field] || ''
    }));

    const outputFieldWithTypes = {
        field: outputField.value,
        type: fieldTypes.value[outputField.value] || ''
    }
    await center
        .post(
            "/job/add",
            {
                db: db.value,
                input_field: inputFieldWithTypes,
                output_field: outputFieldWithTypes,
                net: net.value,
                round: round.value,
                epochs: epochs.value,
                strategy: strategy.value,
                server_config: {
                    fraction_fit: fraction_fit.value,
                    fraction_evaluate: fraction_evaluate.value,
                    min_fit_clients: min_fit_clients.value,
                    min_evaluate_clients: min_evaluate_clients.value,
                    min_available_clients: min_available_clients.value,
                    min_completion_rate_fit: min_completion_rate_fit.value,
                    min_completion_rate_evaluate: min_completion_rate_evaluate.value,
                    accept_failure: accept_failure.value
                }
            },
            {
                headers: {
                    'Content-Type': 'application/json'
                },
                params: {
                    'session': localStorage.getItem("userSession"),
                }
            }
        )
        .then((res) => {
            if (res.status == 200) {
                resetForm();
                alert("任务上传成功");
                emit('update:show', false);
                emit('refresh');
            }
        })
        .catch((error) => {
            alert("任务上传失败" + error);
        });
};

const fetchData = async () => {
    try {
        const [rulerRes, netRes] = await Promise.all([
            center.get("/ruler/list"),
            center.get("/net/list")
        ]);

        if (rulerRes.status === 200) {
            db_list.value = rulerRes.data.ruler_list;
        }
        if (netRes.status === 200) {
            netList.value = netRes.data.net_list;
        }
    } catch (error) {
        console.error("获取数据失败:", error);
        alert("获取数据失败");
    }
};

watch(() => props.show, (newVal) => {
    if (newVal) {
        fetchData();
        currentPage.value = 0;
    }
});
</script>

<template>
    <div v-if="show" class="overlay" @click.self="handleClose">
        <div class="overlay-content">
            <!-- 第一页 -->
            <div v-if="currentPage === 0">
                <div class="upload-header">
                    <h2>新建任务 - 基本设置</h2>
                </div>
                <div class="upload-body">
                    <el-form label-position="top" class="form-container">
                        <el-form-item label="使用网络模型：" required>
                            <el-select v-model="net" placeholder="请选择网络模型" class="form-input">
                                <el-option v-for="item in netList" :key="item.id" :label="item.net_name"
                                    :value="item.id" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="使用数据库：" required>
                            <el-select v-model="db" placeholder="请选择数据库" class="form-input">
                                <el-option v-for="item in db_list" :key="item.id" :label="item.aligned_db"
                                    :value="item.id" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="模型输入字段：" required>
                            <el-select v-model="inputField" placeholder="请选择输入字段" multiple class="form-input">
                                <el-option v-for="item in Field" :key="item" :label="item" :value="item" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="模型输出字段：" required>
                            <el-select v-model="outputField" placeholder="请选择输出字段" class="form-input">
                                <el-option v-for="item in Field" :key="item" :label="item" :value="item" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="交换轮次：" required>
                            <el-input-number v-model="round" :min="1" :step="1" class="form-input" />
                        </el-form-item>
                        <el-form-item label="节点训练轮数：" required>
                            <el-input-number v-model="epochs" :min="1" :step="1" class="form-input" />
                        </el-form-item>

                        <div class="action-buttons">
                            <el-button type="primary" @click="handleNextStep" class="next-btn">
                                下一步 <el-icon>
                                    <ArrowRight />
                                </el-icon>
                            </el-button>
                            <el-button @click="handleClose">取消</el-button>
                        </div>
                    </el-form>
                </div>
            </div>

            <!-- 第二页 -->
            <div v-else-if="currentPage === 1">
                <div class="upload-header">
                    <h2>新建任务 - 高级设置</h2>
                </div>
                <div class="upload-body">
                    <el-form label-position="top" class="form-container compact-form">
                        <el-form-item>
                            <template #label>
                                <div class="custom-label">
                                    <span class="required-marker">*</span>
                                    <span>联邦学习策略：</span>
                                    <el-tooltip placement="right" effect="light" max-width="500">
                                        <template #content>
                                            <div class="tooltip-strategy-description">
                                                <h4>联邦学习策略说明</h4>
                                                <ul>
                                                    <li><strong>FedAvg (联邦平均):</strong> 最基础和常用的策略，使用加权平均方式聚合客户端模型参数</li>
                                                    <li><strong>FedProx:</strong> FedAvg
                                                        的改进版本，增加了近端项来限制本地模型与全局模型的差异，更适合处理异构数据</li>
                                                    <li><strong>FedAdagrad:</strong> 基于 Adagrad 优化器的联邦学习策略，适用于稀疏数据场景
                                                    </li>
                                                    <li><strong>FedAdam:</strong> 基于 Adam 优化器的联邦学习策略，结合了动量和自适应学习率</li>
                                                    <li><strong>FedYogi:</strong> 基于 Yogi 优化器的联邦学习策略，对 Adam
                                                        的改进版本，更适合非凸优化问题</li>
                                                    <li><strong>QFedAvg:</strong> 基于性能的联邦学习策略，考虑客户端模型性能来调整聚合权重</li>
                                                </ul>
                                            </div>
                                        </template>
                                        <el-icon class="tip-icon">
                                            <QuestionFilled />
                                        </el-icon>
                                    </el-tooltip>
                                </div>
                            </template>
                            <el-select v-model="strategy" placeholder="请选择联邦学习策略" class="form-input">
                                <el-option v-for="item in strategyOptions" :key="item.value" :label="item.label"
                                    :value="item.value" />
                            </el-select>
                        </el-form-item>

                        <div class="form-row">
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            <span>训练客户端比例：</span>
                                            <el-tooltip content="每轮训练中参与训练的客户端比例，1.0 表示所有可用客户端都会参与训练" placement="right"
                                                effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="fraction_fit" :min="0.1" :max="1" :step="0.1"
                                        show-input />
                                </el-form-item>
                            </div>
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            评估客户端比例：
                                            <el-tooltip content="每轮评估中参与评估的客户端比例，1.0 表示所有可用客户端都会参与评估" placement="right"
                                                effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="fraction_evaluate" :min="0.1" :max="1" :step="0.1"
                                        show-input />
                                </el-form-item>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            训练完成率：
                                            <el-tooltip content="定义每轮训练中必须成功完成的客户端比例，例如：0.5 表示至少 50% 的客户端必须成功完成"
                                                placement="right" effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="min_completion_rate_fit" :min="0.1" :max="1" :step="0.1"
                                        show-input />
                                </el-form-item>
                            </div>
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            评估完成率：
                                            <el-tooltip content="定义每轮评估中必须成功完成的客户端比例，例如：0.5 表示至少 50% 的客户端必须成功完成"
                                                placement="right" effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="min_completion_rate_evaluate" :min="0.1" :max="1"
                                        :step="0.1" show-input />
                                </el-form-item>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            最少训练客户端数量：
                                            <el-tooltip content="每轮训练所需的最少客户端数量，必须 ≤ 实际可用的客户端总数" placement="right"
                                                effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="min_fit_clients" :min="1" :step="1" />
                                </el-form-item>
                            </div>
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            最少评估客户端数量：
                                            <el-tooltip content="每轮评估所需的最少客户端数量，必须 ≤ 实际可用的客户端总数" placement="right"
                                                effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="min_evaluate_clients" :min="1" :step="1" />
                                </el-form-item>
                            </div>
                        </div>

                        <!-- 修改最后两个表单项的布局结构 -->
                        <div class="form-row">
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            最少可用客户端数量：
                                            <el-tooltip content="开始训练前需要连接的最少客户端数量，服务器会等待直到达到这个数量才开始训练"
                                                placement="right" effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-input-number v-model="min_available_clients" :min="1" :step="1" />
                                </el-form-item>
                            </div>
                            <div class="form-col">
                                <el-form-item>
                                    <template #label>
                                        <div class="custom-label">
                                            <span class="required-marker">*</span>
                                            允许部分客户端训练失败：
                                            <el-tooltip content="是否允许部分客户端训练失败。True：即使有客户端失败也继续训练；False：任何客户端失败都会中断训练"
                                                placement="right" effect="light">
                                                <el-icon class="tip-icon">
                                                    <QuestionFilled />
                                                </el-icon>
                                            </el-tooltip>
                                        </div>
                                    </template>
                                    <el-switch v-model="accept_failure" style="margin-top: 8px;" />
                                </el-form-item>
                            </div>
                        </div>

                        <div class="action-buttons">
                            <el-button @click="handlePreviousStep" class="step-btn">
                                <el-icon>
                                    <ArrowLeft />
                                </el-icon> 上一步
                            </el-button>
                            <el-button type="success" @click="handleUpload" class="submit-btn">
                                <el-icon>
                                    <Check />
                                </el-icon> 提交任务
                            </el-button>
                            <el-button @click="handleClose">取消</el-button>
                        </div>
                    </el-form>
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
    backdrop-filter: blur(3px);
}

.overlay-content {
    width: 720px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    padding: 2rem 3rem;
    max-height: 90vh;
    overflow-y: auto;
}

.upload-header {
    padding: 15px;
    border-bottom: 1px solid #f0f0f0;
}

.upload-header h2 {
    margin: 0;
    font-size: 20px;
    color: #303133;
    text-align: center;
}

.upload-body {
    padding: 15px;
}

.form-container {
    width: 100%;
    max-width: 680px;
}

.form-input {
    width: 100%;
    margin-bottom: 0.5rem;
}

.footer {
    margin-top: 20px;
    text-align: center;
}

.action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
}

.next-btn,
.step-btn,
.submit-btn {
    padding: 10px 20px;
    font-size: 14px;
}

:deep(.el-select) {
    width: 100%;
}

:deep(.el-slider) {
    width: 100%;
}

/* 新增样式，优化第二页布局 */
.compact-form :deep(.el-form-item) {
    margin-bottom: 10px;
}

.form-row {
    display: flex;
    gap: 20px;
}

.form-col {
    flex: 1;
}


.required-marker {
    color: var(--el-color-danger);
    margin-right: 2px;
}

.tip-icon {
    color: var(--el-color-primary);
    cursor: pointer;
    font-size: 14px;
}

/* 移除 el-form-item 默认的必填标记 */
:deep(.el-form-item.is-required .el-form-item__label:before) {
    content: '';
    margin-right: 0;
}

:deep(.el-input-number) {
    width: 100%;
}

:deep(.el-switch) {
    display: flex;
    margin-top: 8px;
}

:deep(.tooltip-strategy-description) {
    padding: 5px;
    font-size: 14px;
}

:deep(.tooltip-strategy-description h4) {
    margin-top: 0;
    margin-bottom: 8px;
    color: var(--el-color-primary);
}

:deep(.tooltip-strategy-description ul) {
    margin: 0;
    padding-left: 20px;
}

:deep(.tooltip-strategy-description li) {
    margin-bottom: 6px;
    line-height: 1.5;
    white-space: normal;
    text-align: left;
}

:deep(.tooltip-strategy-description li:last-child) {
    margin-bottom: 0;
}

/* 增加 tooltip 的最大宽度 */
:deep(.el-tooltip__popper) {
    max-width: 500px;
}
</style>