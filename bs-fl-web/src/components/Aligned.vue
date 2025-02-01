<script setup lang="ts">
import Background from "./Background.vue";
import { onMounted, ref, computed } from "vue";
import axios from "axios";
import { Plus } from "@element-plus/icons-vue";
import { state } from "@/utils/settings";
import type { UploadInstance } from "element-plus";

const alignedList = ref([]);
const showOverlay = ref(false);

const handleClick = () => {
	console.log("click");
};

const handleAdd = () => {
	showOverlay.value = true;
};

const beforeUpload = (file: File): boolean => {
	const isCSV = file.type === "text/csv";
	if (!isCSV) {
		alert("上传文件只能是 CSV 格式!");
		return false;
	}
	return true;
};

const uploadRef = ref<UploadInstance>();

onMounted(async () => {
	const res = await axios.get(
		"http://" + state.center.ip + ":" + state.center.port + "/ruler/aligned",
		{
			params: {
				session: localStorage.getItem("userSession"),
			},
		}
	);

	console.log(res.data.aligned_data);
	alignedList.value = res.data.aligned_data;
});

// 解析字段字符串为数组并格式化为字符串
const parseFields = (fieldString: string) => {
	if (fieldString.includes(",")) {
		const fieldsArray = fieldString.split(","); // 解析字符串为数组
		return fieldsArray.join("; "); // 将数组转换为以分号分隔的字符串
	} else {
		return fieldString;
	}
};
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<Background />
			<el-table :data="alignedList">
				<el-table-column
					fixed
					prop="aligned_db"
					label="数据库名称"
					width="200"
					align="center" />
				<el-table-column
					label="原始数据库"
					width="300"
					header-align="center"
					align="center">
					<template #default="{ row }">
						{{ parseFields(row.original_db) }}
					</template> </el-table-column
				>/>
				<el-table-column
					prop="data_count"
					label="数据量"
					width="120"
					align="center" />
				<el-table-column
					label="字段"
					width="300"
					header-align="center"
					align="center">
					<template #default="{ row }">
						{{ parseFields(row.ruler_field) }}
					</template>
				</el-table-column>
				<el-table-column
					prop="created_at"
					sortable
					label="创建时间"
					width="200"
					align="center" />
				<el-table-column
					prop="updated_at"
					sortable
					label="更新时间"
					align="center" />
			</el-table>
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
}
.scrollable-content {
	height: 100%;
	width: auto;
}
.el-table {
	background-color: rgba(255, 255, 255, 0.4);
	border-radius: 10px;
	width: 100%;
	height: 100%;
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
</style>
