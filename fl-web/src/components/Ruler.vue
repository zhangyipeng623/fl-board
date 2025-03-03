<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { center } from "@/utils/utils";
import { Plus } from "@element-plus/icons-vue";
import { ElTreeSelect } from "element-plus";
import type Node from "element-plus/es/components/tree/src/model/node";

interface Operator {
	db_name_id: string;
	field_name_id: string;
	operator: string;
	field_value: string | string[];
}
interface RulerEntry {
	name_id: string;
	operator: Operator[];
}
type Ruler = RulerEntry[];

const rulerList = ref([]);
const currentOriginalDbIndex = ref(-2);
const playShow = ref(false);

const rulerName = ref("");
const alignedDb = ref("");
const originalDb = ref([]);
const alignedField = ref("");
const ruler = ref<Ruler>([]);

const rulerDetail = ref();
const detailTitle = ref("");

const selectedOperators = ref<string[]>([]);
const selectedData = ref<any[]>([]);

const handleClick = () => {
	console.log("click");
};

const handleAdd = () => {
	currentOriginalDbIndex.value = -1;
};

const rulerTitle = (rulerName: string) => {
	// rulername 为name-index 返回name
	return rulerName.split("-")[0] + "=>" + alignedDb.value;
};

const isMultiple = (index: number) => {
	const operator = selectedOperators.value[index];
	return (
		operator === "+" || operator === "-" || operator === "*" || operator === "/"
	);
};

const props = {
	label: "label",
	value: "value",
	children: "children",
	isLeaf: "isLeaf",
};

const loadNode = async (node: any, resolve: any) => {
	if (node.data.isLeaf) return resolve([]);
	if (node.level === 0) {
		try {
			const res = await center.get("/node/list");
			if (res.status === 200) {
				const formattedNodeList = res.data.node_list.map((item: any) => ({
					...item,
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
			const res = await center.get("/db/list",
				{
					params: {
						node_id: node.data.value,
					},
				}
			);
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
		if (selectedOperators.value[index] === "+" ||
			selectedOperators.value[index] === "-" ||
			selectedOperators.value[index] === "*" ||
			selectedOperators.value[index] === "/" ||
			selectedOperators.value[index] === "="
		) {
			resolve([{
				value: originalDb.value[currentOriginalDbIndex.value],
				label: originalDb.value[currentOriginalDbIndex.value],
				disabled: true,
			}]);

		} else {
			for (let i = 0; i < originalDb.value.length; i++) {
				originalDbList.push({
					value: originalDb.value[i],
					label: originalDb.value[i],
					disabled: true,
				});
			}
			resolve(originalDbList);
		}
	} else {
		try {
			const res = await center.get("/db/field",
				{
					params: {
						name_id: node.data.value,
					},
				}
			);
			if (res.status === 200) {
				const formattedNodeList = res.data.field_list.map((item: any) => ({
					...item,
					isLeaf: true,
				}));
				resolve(formattedNodeList);
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
	if (rulerName.value === "") {
		alert("请输入对齐规则名称");
		return;
	}
	if (alignedDb.value === "") {
		alert("请输入对齐数据库名称");
		return;
	}
	if (alignedField.value === "") {
		alert("请输入对齐字段");
		return;
	}
	if (originalDb.value.length === 0) {
		alert("请选择原始数据库");
		return;
	}
	if (currentOriginalDbIndex.value === -1) {
		for (let i = 0; i < originalDb.value.length; i++) {
			const dbName = originalDb.value[i]; // 获取当前数据库名称
			// 初始化 ruler 中的每个 dbName 为一个空数组
			if (!ruler.value.find((item) => item.name_id === dbName)) {
				ruler.value.push({
					name_id: dbName,
					operator: [],
				});
			}
		}
		currentOriginalDbIndex.value = 0;
	} else if (currentOriginalDbIndex.value < originalDb.value.length - 1) {
		const currentDb = originalDb.value[currentOriginalDbIndex.value]; // 获取当前数据库名称
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
				db_name_id: currentDb,
				field_name_id: alignedFieldArray.value[i],
				operator: selectedOperators.value[i],
				field_value: selectedData.value[i],
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
	const currentDb = originalDb.value[currentOriginalDbIndex.value]; // 获取当前数据库名称
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
			db_name_id: currentDb,
			field_name_id: alignedFieldArray.value[i],
			operator: selectedOperators.value[i],
			field_value: selectedData.value[i],
		});
	}
	try {
		const res = await center.post("/ruler/add",
			{
				ruler_name: rulerName.value,
				aligned_db: alignedDb.value,
				original_db: originalDb.value,
				field: alignedField.value,
				ruler: ruler.value,
			}
		);
		if (res.status === 200) {
			selectedOperators.value = [];
			selectedData.value = [];
			alert("提交规则成功");
			currentOriginalDbIndex.value = -2;
		}
	} catch (error) {
		ruler.value[currentOriginalDbIndex.value].operator = [];
		selectedOperators.value = [];
		selectedData.value = [];
		alert("提交规则失败" + error);
	}
};

onMounted(async () => {
	const res = await center.get("/ruler/list");

	console.log(res);
	rulerList.value = res.data.ruler_list;
});
const handelDetail = async (item: string, row: any) => {
	try {
		const res = await center.get("/ruler/detail",
			{
				params: {
					ruler_id: row.id,
					original_node: item,
				},
			}
		);
		detailTitle.value = item + "===>" + row.aligned_db;
		rulerDetail.value = JSON.parse(res.data);
		console.log(rulerDetail.value, "rulerDetail");
		playShow.value = true;
	} catch (error) {
		console.log(error);
		alert("获取对齐规则详情失败" + error);
	}
};

const showDetail = (item: any) => {
	let field = item.field_name_id;
	let db = item.db_name_id;
	let operator = item.operator;
	let value = "";
	if (operator === "avg" || operator === "max" || operator === "min") {
		value = operator + "(" + db + "[" + item.field_value.split(",")[0] + "])";
	} else if (operator === "=") {
		value = db + "[" + item.field_value.split(",")[0] + "]";
	} else {
		for (let i = 0; i < item.field_value.length; i++) {
			value +=
				db + "[" + item.field_value[i].split(",")[0] + "]" + operator + " ";
		}
		value = value.slice(0, -2);
	}
	console.log(value, "value");
	console.log(field + " " + operator + " " + value);
	return field + " = " + value;
};

// 解析字段字符串为数组并格式化为字符串
const parseFields = (fieldString: string) => {
	if (fieldString.includes(",")) {
		const fieldsArray = fieldString.split(","); // 解析字符串为数组
		return fieldsArray.join("; "); // 将数组转换为以逗号分隔的字符串
	} else {
		return fieldString;
	}
};

const parseRuler = (rulerString: string) => {
	if (rulerString.includes(",")) {
		const rulerArray = rulerString.split(","); // 解析字符串为数组
		return rulerArray;
	} else {
		return [rulerString];
	}
};

// 重置数据到原始状态
const resetData = () => {
	rulerName.value = "";
	alignedDb.value = "";
	alignedField.value = "";
	originalDb.value = [];
	currentOriginalDbIndex.value = -2;
	selectedOperators.value = [];
	selectedData.value = [];
};

// 计算属性，将以逗号分隔的字符串转换为数组
const alignedFieldArray = computed(() => {
	return alignedField.value
		.split(",")
		.map((field) => field.trim())
		.filter((field) => field); // 去除空字段
});
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="rulerList">
				<el-table-column fixed prop="ruler_name" label="对齐规则名称" align="center" />
				<el-table-column prop="aligned_db" label="对齐数据库" align="center"></el-table-column>/>
				<el-table-column label="原始数据库" header-align="center" align="center">
					<template #default="{ row }">
						{{ parseFields(row.original_db) }}
					</template> </el-table-column>/>
				<el-table-column label="字段" header-align="center" align="center">
					<template #default="{ row }">
						{{ parseFields(row.ruler_field) }}
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="对齐规则" align="center">
					<template #header>
						对齐规则
						<el-tooltip class="item" effect="light" content="添加数据集" placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon>
									<Plus />
								</el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default="{ row }">
						<div v-for="item in parseRuler(row.original_db)">
							<span @click="handelDetail(item, row)" style="cursor: pointer">{{
								item
							}}</span>
						</div>
					</template>
				</el-table-column>
			</el-table>
		</div>
		<div v-if="currentOriginalDbIndex > -2" class="overlay">
			<div class="overlay-content" v-if="currentOriginalDbIndex === -1">
				<span class="ruler-title">新增对齐规则</span>
				<div class="ruler-input">
					<span>对齐规则名称：</span>
					<el-input v-model="rulerName" placeholder="对齐规则名称" />
				</div>
				<div class="ruler-input">
					<span>对齐数据库：</span>
					<el-input v-model="alignedDb" placeholder="对齐数据库" />
				</div>
				<div class="ruler-input">
					<span>对齐字段：</span>
					<el-input v-model="alignedField" placeholder="对齐字段(以,分隔)" />
				</div>
				<div class="ruler-input">
					<span>原始数据库：</span>
					<el-tree-select v-model="originalDb" lazy :props="props" :load="loadNode" multiple />
				</div>

				<div class="button-container">
					<el-button type="primary" @click="handleNextStep">下一步</el-button>
					<el-button @click="resetData">关闭</el-button>
				</div>
			</div>

			<div v-if="currentOriginalDbIndex >= 0" class="overlay-content">
				<span class="ruler-title">{{
					rulerTitle(originalDb[currentOriginalDbIndex])
				}}</span>
				<h3>当前选中的原始数据库: {{ originalDb[currentOriginalDbIndex] }}</h3>
				<div class="ruler-input" v-for="(field, index) in alignedFieldArray">
					<span>对齐字段({{ field }}):</span>
					<el-select v-model="selectedOperators[index]" placeholder="选择符号" style="width: 100px">
						<el-option label="+" value="+" />
						<el-option label="-" value="-" />
						<el-option label="*" value="*" />
						<el-option label="/" value="/" />
						<el-option label="=" value="=" />
						<el-option label="avg" value="avg" />
						<el-option label="max" value="max" />
						<el-option label="min" value="min" />
						<el-option label="sum" value="sum" />
					</el-select>
					<el-tree-select lazy :props="props" :multiple="isMultiple(index)" v-model="selectedData[index]"
						:disabled="!selectedOperators[index]"
						:load="(node: Node, resolve: any) => handleLoad(node, resolve, index)"
						:key="`tree-select-${index}-${selectedOperators[index]}`" />
				</div>
				<div class="button-container">
					<el-button @click="handlePreviousStep" v-if="currentOriginalDbIndex >= 0">上一步</el-button>
					<el-button type="primary" @click="handleNextStep"
						v-if="currentOriginalDbIndex < originalDb.length - 1">下一步</el-button>
					<el-button @click="handleSubmit"
						v-if="currentOriginalDbIndex === originalDb.length - 1">提交</el-button>
					<el-button @click="resetData">关闭</el-button>
				</div>
			</div>
		</div>
		<div v-if="playShow" class="overlay">
			<div class="overlay-content">
				<span class="ruler-title">{{ detailTitle }}</span>
				<div v-if="rulerDetail.ruler_detail && rulerDetail.ruler_detail.operator">
					<div v-for="item in rulerDetail.ruler_detail.operator">
						<div>{{ showDetail(item) }}</div>
					</div>
				</div>

				<div class="button-container">
					<el-button @click="playShow = false">关闭</el-button>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.container {
	position: sticky;
	z-index: 1;
	margin: 10px 10px 0 10px;
	width: calc(100% - 20px);
	background-color: rgba(255, 255, 255, 0.4);
	border-radius: 10px;
	height: calc(100vh - 80px);
	backdrop-filter: blur(3px);
}

.scrollable-content {
	height: 100%;
	width: auto;
}

.overlay {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	border-radius: 10px;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 1000;
}

.overlay-content {
	background: white;
	padding: 20px;
	width: 500px;
	border-radius: 8px;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.button-container {
	margin-top: 10px;
}

.ruler-title {
	font-size: 30px;
	font-weight: bold;
	text-align: center;
}

.ruler-input {
	margin-top: 10px;
	margin-bottom: 5px;
	display: flex;
}

.ruler-input span {
	width: 300px;
	text-align: right;
	font-size: 18px;
}
</style>
