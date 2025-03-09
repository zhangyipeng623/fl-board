<script setup lang="ts">
import { onMounted, ref } from "vue";
import { center } from "@/utils/utils";
import { Plus } from "@element-plus/icons-vue";
import AddNet from "@/components/AddNet.vue";
import NetDetail from "@/components/NetDetail.vue";

const tableData = ref([]);
const showAddNet = ref(false);
const showNetDetail = ref(false);
const currentNetId = ref(0);

const handleAdd = () => {
	showAddNet.value = true;
};

const handleNetDetail = (net_id: number) => {
	currentNetId.value = net_id;
	showNetDetail.value = true;
};

const refreshNetList = async () => {
	try {
		const res = await center.get("/net/list", {
			params: {
				session: localStorage.getItem("userSession"),
			},
		});
		tableData.value = res.data.net_list;
	} catch (error) {
		console.error("请求数据失败:", error);
	}
};

onMounted(async () => {
	await refreshNetList();
});
</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="tableData" height="100%" style="width: 100%">
				<el-table-column fixed prop="net_name" label="模型名称" align="center" />
				<el-table-column prop="nodename" label="上传节点" align="center" />
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
						<el-button link type="primary" size="small" @click="handleNetDetail(row.id)">
							详细
						</el-button>
					</template>
				</el-table-column>
			</el-table>
		</div>

		<!-- 使用子组件 -->

	</div>
	<AddNet v-if="showAddNet" v-model:visible="showAddNet" @refresh="refreshNetList" />

	<NetDetail v-if="showNetDetail" v-model:visible="showNetDetail" :net-id="currentNetId" />
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