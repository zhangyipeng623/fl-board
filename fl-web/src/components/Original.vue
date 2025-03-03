<script setup lang="ts">
import { onMounted, ref } from "vue"
import { center } from "@/utils/utils"
import { Plus } from "@element-plus/icons-vue"
import OriginalUpload from '@/components/OriginalUpload.vue'

const tableData = ref([])
const showUpload = ref(false)

const handleAdd = () => {
	showUpload.value = true
}

const handleClick = () => {
	console.log("click")
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
				<el-table-column fixed prop="db_name" label="数据库名称" align="center" />
				<el-table-column prop="username" label="节点名称" align="center" />
				<el-table-column prop="data_number" label="数据量" align="center" />
				<el-table-column prop="field" label="字段" header-align="center" align="center" />
				<el-table-column fixed="right" label="操作" min-width="120" align="center">
					<template #header>
						操作
						<el-tooltip class="item" effect="light" content="添加数据集" placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon>
									<Plus />
								</el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default>
						<el-button link type="primary" size="small" @click="handleClick">详细</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>
	<OriginalUpload v-model:show="showUpload" @upload-success="handleUploadSuccess" />
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
</style>
