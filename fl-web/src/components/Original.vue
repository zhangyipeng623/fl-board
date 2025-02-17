<script setup lang="ts">
import Background from "./Background.vue";
import { onMounted, ref, computed } from "vue";
import { center } from "@/utils/utils";
import { Plus } from "@element-plus/icons-vue";
import { state } from "@/utils/settings";
import type { UploadInstance } from "element-plus";

const tableData = ref([]);
const showOverlay = ref(false);
const hasHeader = ref(true);
const tableName = ref("");
const uploadUrl = computed(() => {
	return (
		"http://" +
		state.user.ip +
		":" +
		state.user.port +
		"/db/upload?session=" +
		localStorage.getItem("localSession") +
		"&userSession=" +
		localStorage.getItem("userSession")
	);
});
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

const handleUpload = () => {
	console.log("上传逻辑处理");
	console.log("是否有表头:", hasHeader.value);
	uploadRef.value!.submit();
};
const handleUploadError = (err: any, file: any) => {
	console.error("上传失败:", err); // 打印错误信息
	alert(`上传失败: ${file.name} - ${err.message || "未知错误"}`); // 显示错误提示
};

const handleUploadSuccess = (res: any) => {
	console.log("上传成功:", res);
	showOverlay.value = false;
	center
		.get(
			"/db/original",
			{
				params: {
					session: localStorage.getItem("userSession"),
				},
			}
		)
		.then((res) => {
			console.log(res);
			tableData.value = res.data.db_list;
		})
		.catch((error) => {
			console.error("请求数据失败:", error);
		});
};

onMounted(async () => {
	const res = await center.get(
		"http://" + state.center.ip + ":" + state.center.port + "/db/original",
		{
			params: {
				session: localStorage.getItem("userSession"),
			},
		}
	);

	console.log(res);
	tableData.value = res.data.db_list;
});

// 解析字段字符串为数组并格式化为字符串
const parseFields = (fieldString: string) => {
	if (fieldString.includes(",")) {
		const fieldsArray = fieldString.split(","); // 解析字符串为数组
		return fieldsArray.join("; "); // 将数组转换为以分号分隔的字符串
	} else {
		return [fieldString];
	}
};
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<Background />
			<el-table :data="tableData">
				<el-table-column
					fixed
					prop="db_name"
					label="数据库名称"
					align="center" />
				<el-table-column prop="username" label="节点名称" align="center" />
				<el-table-column prop="data_number" label="数据量" align="center" />
				<el-table-column label="字段" header-align="center" align="center">
					<template #default="{ row }">
						{{ parseFields(row.field) }}
					</template>
				</el-table-column>
				<el-table-column
					prop="created_at"
					sortable
					label="创建时间"
					align="center" />
				<el-table-column
					prop="updated_at"
					sortable
					label="更新时间"
					align="center" />
				<el-table-column
					fixed="right"
					label="操作"
					min-width="120"
					align="center">
					<template #header>
						操作
						<el-tooltip
							class="item"
							effect="light"
							content="添加数据集"
							placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon> <Plus /> </el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default>
						<el-button link type="primary" size="small" @click="handleClick">
							详细
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>
		<div v-if="showOverlay" class="overlay">
			<div class="overlay-content">
				<span class="node-title">上传数据集</span>
				<el-upload
					ref="uploadRef"
					class="upload-demo"
					:action="uploadUrl"
					:auto-upload="false"
					:before-upload="beforeUpload"
					:on-success="handleUploadSuccess"
					:on-error="handleUploadError"
					:data="{
						hasHeader: hasHeader,
						table_name: tableName,
						user_id: state.user.id,
					}"
					accept=".csv">
					<el-button size="small" type="primary">点击上传 CSV 文件</el-button>
				</el-upload>
				<el-checkbox v-model="hasHeader">是否有表头</el-checkbox>
				<el-input v-model="tableName" placeholder="数据库名称" />
				<div>
					<el-button type="primary" @click="handleUpload">上传</el-button>
					<el-button @click="showOverlay = false">关闭</el-button>
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
