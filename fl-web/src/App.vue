<script setup lang="ts">
import { RouterView, useRoute, useRouter } from "vue-router";
import {
	Document,
	Menu as IconMenu,
	Coin,
	Odometer,
	Fold,
	Expand
} from "@element-plus/icons-vue";
import cuc2 from "@/assets/images/cuc_2.png"; /* 大图标 */
import cuc1 from "@/assets/images/cuc_1.png";
import { onMounted, ref } from "vue";
const router = useRouter();
const route = useRoute();
const isRouter = ref(true);
const goHome = () => {
	console.log("goHome");
	router.push({ path: "/" });
};
const handleOpen = (key: string, keyPath: string[]) => {
	console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
	console.log(key, keyPath)
}

onMounted(() => {
	console.log("App mounted");
});
const isCollapse = ref(false);
</script>

<template>
	<div class="background"></div>
	<el-menu :collapse="isCollapse" active-text-color="#51c4d3" class="el-menu-vertical" :default-active="route.path"
		text-color="black" :router="isRouter" @open="handleOpen" @close="handleClose">

		<div style="text-align: center; padding-top: 15px">
			<el-image :src="cuc2" class="cuc2" @click="goHome" v-if="!isCollapse"></el-image>
			<el-image :src="cuc1" class="cuc1" @click="goHome" v-if="isCollapse"></el-image>
		</div>
		<el-menu-item index="/node_info">
			<el-icon><icon-menu /></el-icon>
			<template #title>节点信息</template>
		</el-menu-item>
		<el-sub-menu index="/data">
			<template #title>
				<el-icon>
					<Coin />
				</el-icon>
				<span>数据集管理</span>
			</template>
			<el-menu-item index="/original">原始数据集</el-menu-item>
			<el-menu-item index="/ruler">对齐规则</el-menu-item>
			<el-menu-item index="/aligned">对齐数据集</el-menu-item>
		</el-sub-menu>
		<el-menu-item index="/net">
			<el-icon>
				<document />
			</el-icon>
			<template #title>网络模型管理</template>
		</el-menu-item>
		<el-menu-item index="/job">
			<el-icon>
				<Odometer />
			</el-icon>
			<template #title>任务</template>
		</el-menu-item>

		<div style="margin-top: auto;margin-bottom: 5px;"> <!-- 移动到最下边 -->
			<el-divider style="margin-top: 10px;margin-bottom: 10px;" />
			<el-tooltip class="box-item" effect="dark" content="折叠导航" placement="top">
				<el-icon v-if="!isCollapse" @click="isCollapse = !isCollapse" class="icon-large">
					<Fold />
				</el-icon>
			</el-tooltip>
			<el-tooltip class="box-item" effect="dark" content="展开导航" placement="top">
				<el-icon v-if="isCollapse" @click="isCollapse = !isCollapse" class="icon-large">
					<Expand />
				</el-icon>
			</el-tooltip>
		</div>
	</el-menu>
	<RouterView />
</template>

<style scoped>
.icon-large {
	cursor: pointer;
	margin-left: 10px;
	/* 添加样式 */
	font-size: 24px;
	/* 根据需要调整大小 */
	width: 24px;
	/* 根据需要调整大小 */
	height: 24px;
	/* 根据需要调整大小 */
}

.el-menu-vertical {
	margin: 10px 0 10px 5px;
	max-width: 200px;
	border-radius: 20px;
	display: flex;
	flex-direction: column;
}


.background {
	/* 最下面的背景 */
	position: absolute;
	left: 0;
	top: 0;
	width: 100%;
	height: 100%;
	background: linear-gradient(180deg, #d4e8f6, #def1f9);
	/* 渐变效果：浅蓝色到更浅的蓝色 */
	z-index: -2;
}


.cuc2 {
	margin: auto;
	width: 90%;
	cursor: pointer;
}

.cuc1 {
	margin: auto;
	width: 45%;
	cursor: pointer;
}
</style>