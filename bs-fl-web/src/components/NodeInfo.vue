<script setup lang="ts">
import Background from "./Background.vue";
import { onMounted, onBeforeUnmount, ref } from "vue";
import axios from "axios";
import { getNodeStatus } from "@/utils/utils";
import { state } from "@/utils/settings";
import type { DbNode } from "@/utils/settings";

const loading = ref(true);
const showOverlay = ref(false);
const node_status = ref({} as DbNode);
const node_info = ref({
	mysql: "false",
	redis: "false",
	nginx: "false",
});

const display_node_status = async (node: DbNode) => {
	node_status.value = node;
	showOverlay.value = true;
	if (node.is_connect) {
		try {
			const res = await axios.get(
				"http://" + node.ip + ":" + node.port + "/status",
				{
					params: {
						session: localStorage.getItem("userSession"),
						username: localStorage.getItem("username"),
						ip: localStorage.getItem("ip"),
					},
				}
			);
			node_info.value.mysql = res.data.data.mysql;
			node_info.value.redis = res.data.data.redis;
			node_info.value.nginx = res.data.data.nginx;
			console.log(node_info.value, "node_info");
			console.log(res.data, "res");
		} catch (e) {
			console.log(e);
			node.is_connect = false;
		}
	}
};

onMounted(async () => {
	if (state.db_node.length > 0) {
		loading.value = false;
	} else {
		loading.value = true;
	}
	// 设置每 3 秒自动运行一次 getNodeStatus 函数
	const intervalId = setInterval(() => {
		getNodeStatus();
		if (state.db_node.length > 0) {
			loading.value = false;
		} else {
			loading.value = true;
		}
	}, 5000);

	const intervalNodeStatus = setInterval(() => {
		if (showOverlay.value) {
			display_node_status(node_status.value);
		}
	}, 5000);

	// 在组件卸载时清除定时器
	onBeforeUnmount(() => {
		clearInterval(intervalId);
		clearInterval(intervalNodeStatus);
	});
});
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<Background />
			<div class="node-list">
				<div class="center-node">
					<!-- 居中显示 中心节点 -->
					<span class="node-title">中心节点</span>
					<div class="node-item">
						<el-card
							style="width: 230px; height: 80px; margin: 10px; cursor: pointer"
							@click="display_node_status(state.center)">
							<span class="node-name">
								{{ state.center.name }}:{{ state.center.ip }} :{{
									state.center.port
								}}
							</span>
							<span
								class="node-status"
								:class="{
									connected: state.center.is_connect,
									disconnected: !state.center.is_connect,
								}">
								{{ state.center.is_connect ? "连接" : "断开" }}
							</span>
						</el-card>
					</div>
				</div>
				<div class="db-node">
					<span class="node-title">数据集节点</span>
					<div
						style="
							display: flex;
							flex-wrap: wrap;
							background-color: rgba(137, 134, 134, 0);
							margin-top: 15px;
						"
						v-loading="loading"
						element-loading-text="Loading..."
						element-loading-background="rgba(0, 0, 0, 0)">
						<div v-if="loading" style="margin-top: 15px">
							<el-skeleton style="width: 100%" />
							<el-skeleton style="width: 100%" />
							<el-skeleton style="width: 100%" />
							<el-skeleton style="width: 100%" />
							<el-skeleton style="width: 100%" />
						</div>
						<div
							v-for="(node, index) in state.db_node"
							:key="index"
							class="node-item">
							<el-card
								style="
									width: 230px;
									height: 80px;
									margin: 10px;
									cursor: pointer;
								"
								@click="display_node_status(node)">
								<div>
									<span class="node-name">
										{{ node.name }}: {{ node.ip }}:{{ node.port }}
									</span>
									<span
										class="node-status"
										:class="{
											connected: node.is_connect,
											disconnected: !node.is_connect,
										}">
										{{ node.is_connect ? "连接" : "断开" }}
									</span>
								</div>
							</el-card>
						</div>
					</div>
				</div>
				<!-- 覆盖层 -->
				<div v-if="showOverlay" class="overlay">
					<div class="overlay-content">
						<span class="node-title">节点信息</span>
						<div class="node-status-container">
							<div class="status-row">
								<span class="label">名称:</span>
								<span class="value">{{ node_status.name }}</span>
							</div>
							<div class="status-row">
								<span class="label">IP:</span>
								<span class="value">{{ node_status.ip }}</span>
							</div>
							<div class="status-row">
								<span class="label">端口:</span>
								<span class="value">{{ node_status.port }}</span>
							</div>
							<div class="status-row">
								<span class="label">状态:</span>
								<span class="value">{{
									node_status.is_connect ? "连接" : "断开"
								}}</span>
							</div>
							<div v-if="node_status.is_connect" class="status-row">
								<span class="label">MySQL:</span>
								<span class="value">{{
									node_info.mysql ? "连接" : "断开"
								}}</span>
							</div>
							<div v-if="node_status.is_connect" class="status-row">
								<span class="label">Redis:</span>
								<span class="value">{{
									node_info.redis ? "连接" : "断开"
								}}</span>
							</div>
							<div v-if="node_status.is_connect" class="status-row">
								<span class="label">Nginx:</span>
								<span class="value">{{
									node_info.nginx ? "连接" : "断开"
								}}</span>
							</div>
						</div>
						<div class="button-container">
							<button @click="showOverlay = false">关闭</button>
						</div>
					</div>
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
	overflow-y: scroll;
}
.node-list {
	height: 100%;
	margin: 10px;
	border-radius: 10px;
}
.center-node {
	background-color: rgba(137, 134, 134, 0);
	min-height: 20%;
	margin: 5px;
	border-radius: 10px;
}
.db-node {
	background-color: rgba(137, 134, 134, 0);
	min-height: 65%;
	margin: 10px 5px 5px 5px;
	border-radius: 10px;
}
.node-title {
	font-size: 30px;
	font-weight: bold;
	text-align: center;
}
.node-name {
	text-align: center; /* 使文本居中 */
	display: block; /* 使其成为块级元素，以便应用宽度 */
}
.node-status {
	text-align: center; /* 使文本居中 */
	display: block; /* 使其成为块级元素，以便应用宽度 */
	width: 100%; /* 确保宽度为 100% */
	font-size: 20px;
}
.connected {
	color: blue; /* 连接状态的颜色 */
}

.disconnected {
	color: red; /* 断开状态的颜色 */
}

.node-item {
	display: flex; /* 使用 Flexbox 布局 */
}

.overlay {
	position: fixed; /* 固定定位 */
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0); /* 半透明背景 */
	display: flex; /* 使用 Flexbox 居中内容 */
	justify-content: center; /* 水平居中 */
	align-items: center; /* 垂直居中 */
	z-index: 1000; /* 确保在最上层 */
}

.overlay-content {
	background-color: white; /* 白色背景 */
	padding: 20px; /* 内边距 */
	border-radius: 8px; /* 圆角 */
	box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* 阴影 */
}

.button-container {
	display: flex;
	justify-content: center;
	margin-top: 15px;
}

.button-container button {
	padding: 8px 20px;
	border-radius: 4px;
	border: none;
	background-color: #409eff;
	color: white;
	cursor: pointer;
}

.node-status-container {
	display: flex;
	flex-direction: column; /* 垂直排列 */
	gap: 8px; /* 每行之间的间距 */
}

.status-row {
	display: flex; /* 使用 Flexbox 布局 */
	justify-content: space-between; /* 标签和内容之间的空间 */
}

.label {
	width: 80px; /* 设置标签的固定宽度 */
	font-weight: bold; /* 标签加粗 */
}

.value {
	flex-grow: 1; /* 让值占据剩余空间 */
}
</style>
