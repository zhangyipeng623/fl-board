<script setup lang="ts">
import Background from "./Background.vue";
import { onMounted, ref, computed } from "vue";
import { center } from "@/utils/utils";
import { Plus, QuestionFilled } from "@element-plus/icons-vue";
import { state } from "@/utils/settings";
import type { UploadInstance } from "element-plus";
import Prism from "prismjs";
import "prismjs/components/prism-python.min.js";
import "prismjs/themes/prism.css";

const tableData = ref([]);
const showOverlay = ref(false);
const showNetDetail = ref(false);
const isLoad = ref(false);

const netName = ref("");
const inputNum = ref("");
const outputNum = ref("");
const detail = ref("");

const code = ref("");

const uploadUrl = computed(() => {
	return (
		"http://" +
		state.center.ip +
		":" +
		state.center.port +
		"/net/upload?session=" +
		localStorage.getItem("userSession")
	);
});
const netDetail = (net_id: number) => {
	showNetDetail.value = true;
	center
		.get(
			"/net/detail",
			{
				params: {
					session: localStorage.getItem("userSession"),
					net_id: net_id,
				},
			}
		)
		.then((res) => {
			code.value = Prism.highlight(
				res.data.code,
				Prism.languages.python,
				"python"
			);
			Prism.highlightAll();
		})
		.catch((error) => {
			console.error("请求数据失败:", error);
		});
	isLoad.value = true;
};

const handleAdd = () => {
	showOverlay.value = true;
};

const beforeUpload = (file: File): boolean => {
	const isPY = file.name.endsWith(".py");
	if (!isPY) {
		alert("上传文件只能是 py 格式!");
		return false;
	}
	return true;
};

const uploadRef = ref<UploadInstance>();

const handleUpload = () => {
	uploadRef.value!.submit();
};

const handleUploadError = (err: any, file: any) => {
	console.error("上传失败:", err); // 打印错误信息
	alert(`上传失败: ${file.name} - ${err.message || "未知错误"}`); // 显示错误提示
};

const handleUploadSuccess = (res: any) => {
	showOverlay.value = false;
	center
		.get("/net/list", {
			params: {
				session: localStorage.getItem("userSession"),
			},
		})
		.then((res) => {
			tableData.value = res.data.net_list;
		})
		.catch((error) => {
			console.error("请求数据失败:", error);
		});
};

onMounted(async () => {
	const res = await center.get(
		"/net/list",
		{
			params: {
				session: localStorage.getItem("userSession"),
			},
		}
	);
	tableData.value = res.data.net_list;
});
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="tableData">
				<el-table-column fixed prop="net_name" label="模型名称" align="center" />
				<el-table-column prop="node_name" label="上传节点" align="center" />
				<el-table-column prop="input_num" label="输入量" align="center" />
				<el-table-column prop="output_num" label="输出量" header-align="center" align="center" />
				<el-table-column prop="created_at" sortable label="创建时间" align="center" />
				<el-table-column prop="updated_at" sortable label="更新时间" align="center" />
				<el-table-column fixed="right" label="操作" min-width="120" align="center">
					<template #header>
						操作
						<el-tooltip class="item" effect="light" content="添加网络模型" placement="bottom">
							<el-button link type="primary" size="small" @click="handleAdd">
								<el-icon>
									<Plus />
								</el-icon>
							</el-button>
						</el-tooltip>
					</template>
					<template #default="{ row }">
						<el-button link type="primary" size="small" @click="netDetail(row.id)">
							详细
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>
		<div v-if="showOverlay" class="overlay">
			<div class="overlay-content">
				<span class="node-title">上传深度网络模型</span>
				<div class="net-input">
					<span>网络名称：</span>
					<el-input v-model="netName" placeholder="网络名称" />
				</div>
				<div class="net-input">
					<span>模型输入参数量：</span>
					<el-input v-model="inputNum" placeholder="模型输入参数量" />
				</div>
				<div class="net-input">
					<span>模型输出参数量：</span>
					<el-input v-model="outputNum" placeholder="模型输出参数量" />
				</div>
				<div class="net-input">
					<span>模型描述：</span>
					<el-input v-model="detail" placeholder="模型描述" />
				</div>
				<div class="net-input">
					<span>模型文件：</span>
					<el-upload ref="uploadRef" class="upload-demo" :action="uploadUrl" :auto-upload="false"
						:before-upload="beforeUpload" :on-success="handleUploadSuccess" :on-error="handleUploadError"
						:data="{
				netName: netName,
				inputNum: inputNum,
				outputNum: outputNum,
				detail: detail,
				user_id: state.user.id,
			}" accept=".py">
						<el-button size="small" type="primary">点击上传 py 文件</el-button>
						<el-tooltip effect="light" class="item" content="python文件中需要包含Net类和DataSet类" placement="right">
							<el-icon style="margin-left: 10px">
								<QuestionFilled />
							</el-icon>
						</el-tooltip>
					</el-upload>
				</div>
				<div>
					<el-button type="primary" @click="handleUpload">上传</el-button>
					<el-button @click="showOverlay = false">关闭</el-button>
				</div>
			</div>
		</div>
		<div v-if="showNetDetail" class="overlay">
			<div class="overlay-content">
				<div class="code-container">
					<!-- 展示从后端传来的python代码段，高亮显示，使用prismjs -->
					<pre v-if="isLoad" v-html="code"></pre>
					<!-- 将 code 绑定并以高亮显示 -->
				</div>
				<div>
					<el-button @click="showNetDetail = false">关闭</el-button>
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

:deep(.el-table) {
	background-color: transparent !important;
	border-radius: 10px;
}

:deep(.el-table th) {
	background-color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-table td) {
	background-color: rgba(255, 255, 255, 0.2) !important;
}

:deep(.el-table tr:hover td) {
	background-color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover>td) {
	background-color: rgba(255, 255, 255, 0.4) !important;
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
