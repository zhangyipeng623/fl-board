<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Plus } from "@element-plus/icons-vue";
import { center } from "@/utils/utils";
import AddJob from "@/components/AddJob.vue";
import JobDetail from "@/components/JobDetail.vue";
import { getTypeTagStyle } from "@/utils/styleUtils"; // 新增类型样式工具函数

const tableData = ref([]);
const showAddJob = ref(false);
const showDetail = ref(false);
const currentJob = ref(null);

const handleAdd = () => {
	showAddJob.value = true;
};
const refreshList = async () => {
	try {
		const res = await center.get("/job/list");
		if (res.status == 200) {
			tableData.value = res.data.job_list;
		}
	} catch (error) {
		console.error("请求数据失败:", error);
	}
};
const handleDetail = (row: any) => {
	currentJob.value = row;
	showDetail.value = true;
};

onMounted(refreshList);
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="tableData" height="100%" style="width: 100%">
				<el-table-column fixed prop="job_id" label="任务ID" align="center" />
				<el-table-column prop="node_name" label="上传节点" align="center" />
				<el-table-column prop="db_name" label="关联数据库" align="center" />
				<el-table-column prop="input_field" label="输入字段" header-align="center" align="center">
					<template #default="{ row }">
						<div class="field-container">
							<el-tag v-for="(field, index) in row.input_field" :key="index" class="field-tag"
								effect="plain" type="info">
								<span class="field-name">{{ field.field }}</span>
								<el-tag size="small" :type="getTypeTagStyle(field.type)" class="type-tag">
									{{ field.type }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="output_field" label="输出字段" header-align="center" align="center">
					<template #default="{ row }">
						<div class="field-container">
							<el-tag class="field-tag" effect="plain" type="info">
								<span class="field-name">{{ row.output_field.field }}</span>
								<el-tag size="small" :type="getTypeTagStyle(row.output_field.type)" class="type-tag">
									{{ row.output_field.type }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>
				<el-table-column prop="status" label="状态" align="center">
					<template #default="{ row }">
						<el-tag
							:type="row.status === 'finished' ? 'success' : row.status === 'running' ? 'warning' : 'info'"
							effect="light" size="medium">
							{{ row.status === 'finished' ? '已完成' : row.status === 'running' ? '运行中' : '等待中' }}
						</el-tag>
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="操作" min-width="120" align="center">
					<template #header>
						操作
						<el-tooltip class="item" effect="light" content="新建任务" placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon>
									<Plus />
								</el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default="{ row }">
						<el-button link type="primary" size="small" @click="handleDetail(row)">
							查看详情
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>

	</div>
	<AddJob v-model:show="showAddJob" @refresh="refreshList" />
	<JobDetail v-model:show="showDetail" :job="currentJob" />
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

/* 字段展示样式 */
.field-container {
	max-height: 150px;
	overflow-y: auto;
	padding: 4px;
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}

.field-tag {
	margin: 2px;
	padding: 4px 8px;
	border-radius: 4px;
	background-color: var(--el-fill-color-light);
}

.type-tag {
	margin-left: 6px;
	font-style: normal;
	border-radius: 3px;
}

.field-name {
	color: #606266;
	font-size: 13px;
}


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
	background: white;
	padding: 20px;
	border-radius: 8px;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.button-container {
	margin-top: 20px;
}

.node-title {
	font-size: 30px;
	font-weight: bold;
	text-align: center;
}

.uploaded-file-name {
	margin-top: 10px;
	color: #333;
}

.net-input {
	width: 450px;
	margin-top: 10px;
	margin-bottom: 5px;
	display: flex;
}

.net-input span {
	width: 200px;
	text-align: right;
	font-size: 18px;
}

.code-container {
	width: 800px;
	height: 600px;
	/* 设置容器高度，可以根据需要调整 */
	overflow-y: auto;
	/* 允许垂直滚动 */
	background-color: #f5f5f5;
	/* 给容器一个背景色，以便更好地查看代码 */
	border: 1px solid #ccc;
	/* 可选：添加边框以分隔内容 */
	border-radius: 5px;
	/* 可选：添加圆角 */
	padding: 10px;
	/* 可选：添加内边距 */
}
</style>
