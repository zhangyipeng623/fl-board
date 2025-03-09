<script setup lang="ts">
import { onMounted, ref } from "vue";
import { center } from "@/utils/utils";
import { getTypeTagStyle } from "@/utils/styleUtils";

const alignedList = ref([]);

onMounted(async () => {
	const res = await center.get("/ruler/aligned",);
	alignedList.value = res.data.aligned_data;
});



</script>

<template>
	<div class="container">
		<div class="scrollable-content">
			<el-table :data="alignedList" height="100%" style="width: 100%">
				<el-table-column fixed prop="aligned_db" label="数据库名称" align="center" />
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
				</el-table-column>/>
				<el-table-column prop="data_count" label="数据量" align="center" />
				<el-table-column label="字段" header-align="center" align="center">
					<template #default="{ row }">
						<div class="field-container">
							<el-tag v-for="(field, index) in row.ruler_field" :key="index" class="field-tag"
								effect="plain" type="info">
								<span class="field-name">{{ field.field }}</span>
								<el-tag size="small" class="type-tag" :type="getTypeTagStyle(field.type)">
									{{ field.type }}
								</el-tag>
							</el-tag>
						</div>
					</template>
				</el-table-column>
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
