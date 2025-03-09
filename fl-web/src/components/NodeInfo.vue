<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue";
import { state } from "@/utils/settings";
import type { DbNode } from "@/utils/settings";
import { center } from "@/utils/utils";
import NodeCard from "@/components/NodeCard.vue";
import NodeStatus from '@/components/NodeStatus.vue';


const loading = ref(true);

const db_node = ref([] as DbNode[]); //node_list

const system_info = ref<Record<string, {
	cpu: string;
	gpu: string;
	system: string;
}>>({}); //存储系统信息

const showNodeStatus = ref(false)
const current_node = ref<DbNode | null>(null)
const isCenterNode = ref(false)
const showNode = (node: DbNode) => {
	showNodeStatus.value = true;
	current_node.value = node
	isCenterNode.value = node.name === 'center'
}

const getNodeStatus = async () => {
	try {
		const res = await center.get("/node/status");
		state.updateCenterInfo(true);
		db_node.value = res.data.node_list;
		system_info.value = res.data.system;
		loading.value = false; // 新增：请求成功直接关闭loading
	} catch (e) {
		console.error(e);
		loading.value = true; // 新增：请求失败保持loading
	}
};

onMounted(async () => {
	// 设置每 5 秒自动运行一次 getNodeStatus 函数
	getNodeStatus();
	const intervalId = setInterval(() => {
		getNodeStatus();
		if (db_node.value.length > 0) {
			loading.value = false;
		} else {
			loading.value = true;
		}
	}, 5000);

	// 在组件卸载时清除定时器
	onBeforeUnmount(() => {
		clearInterval(intervalId);
	});
});
</script>


<template>
	<div class="container">
		<div class="center-node">
			<NodeCard :node="state.center" :system-info="[
				{ label: '系统', value: system_info.center?.system },
				{ label: 'CPU', value: system_info.center?.cpu },
				{ label: 'GPU', value: system_info.center?.gpu }
			]" @click="showNode(state.center)" />
			<NodeCard :node="state.user" :is-location="true" :system-info="[
				{ label: '系统', value: system_info[state.user.name]?.system },
				{ label: 'CPU', value: system_info[state.user.name]?.cpu },
				{ label: 'GPU', value: system_info[state.user.name]?.gpu }
			]" @click="showNode(state.user)" />
		</div>

		<el-divider style="margin-top: 10px;margin-bottom: 10px;" />

		<div class="db-node" v-loading="loading" element-loading-text="Loading..."
			element-loading-background="rgba(0, 0, 0, 0)">
			<NodeCard v-for="(node, index) in db_node.filter(n => n.name !== state.user.name && n.name !== 'center')"
				:key="index" :node="node" :system-info="[
				{ label: '系统', value: system_info[node.name]?.system },
				{ label: 'CPU', value: system_info[node.name]?.cpu },
				{ label: 'GPU', value: system_info[node.name]?.gpu }
			]" @click="showNode(node)"></NodeCard>
		</div>
	</div>
	<!-- 覆盖层 -->
	<NodeStatus v-if="showNodeStatus" :node="current_node" @close="showNodeStatus = false"
		:isCenterNode="isCenterNode" />
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

.center-node {
	display: flex;
	padding-top: 10px;
	background-color: rgba(137, 134, 134, 0);
	min-height: 20%;
	margin: 5px;
	border-radius: 10px;
	align-items: flex-start;
	/* 顶部对齐 */
	align-content: flex-start;
	/* 顶部开始换行 */
}

.db-node {
	display: flex;
	padding-top: 10px;
	background-color: rgba(137, 134, 134, 0);
	min-height: 70%;
	margin: 5px;
	border-radius: 10px;
	align-items: flex-start;
	/* 顶部对齐 */
	align-content: flex-start;
	/* 顶部开始换行 */
}
</style>
