<script setup lang="ts">
import { onMounted, ref } from "vue";
import { center } from "@/utils/utils";
import { getTypeTagStyle } from "@/utils/styleUtils";
import { Plus } from "@element-plus/icons-vue";
import AddRuler from '@/components/AddRuler.vue'
import RulerDetail from '@/components/RulerDetail.vue'

const rulerList = ref([]);
const playShow = ref(false);
const showAddRuler = ref(false);


const handleAdd = () => {
	showAddRuler.value = true;
};

const handleRulerSubmit = async () => {
	const res = await center.get("/ruler/list");
	rulerList.value = res.data.ruler_list;
};

onMounted(async () => {
	const res = await center.get("/ruler/list");
	rulerList.value = res.data.ruler_list;
});

interface DB {
	id: number;
	name: string;
	nodename: string;
}
const originalDb = ref<DB>()
const ruler_id = ref(0)
const alignedDb = ref()
const handelDetail = async (db: any, id: number, aligned_db: string) => {
	ruler_id.value = id;
	originalDb.value = db;
	alignedDb.value = aligned_db;
	playShow.value = true;
};




// 添加编辑状态变量
const editingField = ref<{ rowIndex: number; fieldIndex: number } | null>(null);
const typeOptions = ['int', 'float', 'string', 'datetime', "list"]; // 可选的类型列表

// 添加更新类型的方法
const handleUpdateType = async (row: any, field: string, newType: string) => {
	try {
		await center.post('/ruler/update-field-type', {
			id: row.id,
			field: field,
			type: newType
		});
		editingField.value = null;
		const res = await center.get("/ruler/list");
		rulerList.value = res.data.ruler_list;
	} catch (error) {
		alert('更新字段类型失败:' + error)
		console.error('更新字段类型失败:', error);
	}
};

</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="rulerList">
				<el-table-column fixed prop="ruler_name" label="对齐规则名称" align="center" />
				<el-table-column prop="aligned_db" label="对齐数据库" align="center"></el-table-column>/>
				<!-- 修改原始数据库列 -->
				<el-table-column label="原始数据库" header-align="center" align="center">
					<template #default="{ row }">
						<div class="field-container">
							<el-tag v-for="(item, index) in row.original_db" :key="index" class="database-tag"
								effect="plain" type="info">
								<span class="field-name">{{ item.name }}</span>
								<el-tag size="small" class="type-tag" effect="dark">
									{{ item.nodename }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>

				<!-- 修改字段列 -->
				<el-table-column label="字段" header-align="center" align="center">
					<template #default="{ row, $index }">
						<div class="field-container">
							<el-tag v-for="(field, fieldIndex) in row.ruler_field" :key="fieldIndex" class="field-tag"
								effect="plain" type="info">
								<span class="field-name">{{ field.field }}</span>
								<template
									v-if="editingField?.rowIndex === $index && editingField?.fieldIndex === fieldIndex">
									<el-select v-model="field.type" size="small"
										@change="(val: string) => handleUpdateType(row, field.field, val)"
										@blur="editingField = null">
										<el-option v-for="type in typeOptions" :key="type" :label="type"
											:value="type" />
									</el-select>
								</template>
								<el-tag v-else size="small" class="type-tag" :type="getTypeTagStyle(field.type)"
									@dblclick="editingField = { rowIndex: $index, fieldIndex }">
									{{ field.type }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>

				<!-- 修改对齐规则列 -->
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
						<div class="field-container">
							<el-tag v-for="(item, index) in row.original_db" :key="index" class="rule-tag"
								@click="handelDetail(item, row.id, row.aligned_db)" effect="plain" type="info"
								style="cursor: pointer">
								{{ item.name }} ({{ item.nodename }})
							</el-tag>
						</div>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>
	<AddRuler v-if="showAddRuler" v-model:show="showAddRuler" @ruler-submit="handleRulerSubmit" />
	<RulerDetail v-if="playShow" v-model:show="playShow" :db="originalDb!" :id="ruler_id" :alignedDb="alignedDb" />
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

.database-tag {
	margin: 2px;
	padding: 4px 8px;
	border-radius: 4px;
	background-color: var(--el-fill-color-light);
}

.rule-tag {
	margin: 2px;
	padding: 4px 8px;
	border-radius: 4px;
	transition: all 0.3s;
}

.rule-tag:hover {
	transform: translateY(-2px);
	box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.field-tag {
	margin: 2px;
	padding: 4px 8px;
	border-radius: 4px;
}

.type-tag {
	margin-left: 6px;
	font-style: normal;
	border-radius: 3px;
	cursor: pointer;
}

.el-select {
	margin-left: 6px;
	width: 80px;
}

.field-name {
	color: #606266;
	font-size: 13px;
}

/* 复用 Original.vue 的容器样式 */
.field-container {
	max-height: 150px;
	overflow-y: auto;
	padding: 4px;
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}
</style>
