<script setup lang="ts">
import { onMounted, ref } from "vue"
import { center } from "@/utils/utils"
import { Plus } from "@element-plus/icons-vue"
import OriginalUpload from '@/components/OriginalUpload.vue'
import { getTypeTagStyle } from "@/utils/styleUtils"; // 新增类型样式工具函数

const tableData = ref([])
const showUpload = ref(false)

const handleAdd = () => {
	showUpload.value = true
}


const handleUploadSuccess = () => {
	// 刷新表格数据
	loadTableData()
}

const loadTableData = async () => {
	try {
		const res = await center.get("/db/original")
		tableData.value = res.data.db_list
	} catch (error) {
		console.error("请求数据失败:", error)
	}
}


onMounted(() => {
	loadTableData()
})
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="tableData">
				<!-- todo 添加分页、排序等功能 -->
				<el-table-column fixed prop="db_name" label="数据库名称" align="center" />
				<el-table-column prop="nodename" label="节点名称" align="center" />
				<el-table-column prop="data_number" label="数据量" align="center" />
				<el-table-column prop="field" label="字段" header-align="center" align="center">
					<template #default="{ row }">
						<div class="field-container">
							<el-tag v-for="(value, key) in row.field" :key="key" class="field-tag" effect="plain"
								type="info">
								<span class="field-name">{{ key }}</span>
								<el-tag size="small" :type="getTypeTagStyle(value)" class="type-tag">
									{{ value }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="详细" min-width="120" align="center">
					<template #header>
						详细
						<el-tooltip class="item" effect="light" content="添加数据集" placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon>
									<Plus />
								</el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default="{ row }">
						<el-tooltip :content="row.detail || '暂无描述'" placement="top" :disabled="!row.detail">
							<span class="detail-text">
								{{ row.detail ? row.detail.slice(0, 15) + (row.detail.length > 15 ? '...' : '') : '无详情'
								}}
							</span>
						</el-tooltip>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>
	<OriginalUpload v-model:show="showUpload" @upload-success="handleUploadSuccess" />
</template>


<style scoped>
/* 修改字段展示样式 */
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

/* 新增字段样式 */
.field-container {
	max-height: 150px;
	overflow-y: auto;
	padding: 4px 0;
}

.field-item {
	display: flex;
	justify-content: space-between;
	margin: 4px 0;
	font-size: 13px;
}

.field-name {
	color: #606266;
	padding-right: 8px;
}

.field-type {
	color: #909399;
	font-style: italic;
}


/* 修改detail展示样式 */
.detail-text {
	max-width: 120px;
	display: inline-block;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	color: #606266;
	/* 改为与字段名相同的颜色 */
	cursor: default;
}
</style>
