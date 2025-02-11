<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { RouterView, useRouter } from "vue-router";
import {
	Document,
	Menu as IconMenu,
	Location,
	Setting,
} from "@element-plus/icons-vue";
import cuc2 from "@/assets/images/cuc_2.png"; /* 大图标 */
const router = useRouter();
const handleOpen = (key: string, keyPath: string[]) => {
	console.log(key, keyPath);
};
const handleClose = (key: string, keyPath: string[]) => {
	console.log(key, keyPath);
};

const goOriginal = () => {
	router.push({ path: "/original" });
};
const goRuler = () => {
	router.push({ path: "/ruler" });
};
const goAlignData = () => {
	router.push({ path: "/aligned" });
};
const goNodeInfo = () => {
	console.log("goNodeInfo");
	router.push({ path: "/node_info" });
};
const goHome = () => {
	console.log("goHome");
	router.push({ path: "/home" });
};
const goNetInfo = () => {
	console.log("goNetInfo");
	router.push({ path: "/net" });
};
</script>

<template>
	<div class="background"></div>
	<el-row class="tac">
		<el-col :span="24">
			<div style="text-align: center; padding-top: 10px">
				<el-image :src="cuc2" class="cuc2" @click="goHome"></el-image>
			</div>
			<h2 class="mb-2">面向联邦学习的数据交换系统</h2>
			<el-menu
				border-right="0"
				background-color="#a7535a"
				active-text-color="#51c4d3"
				class="el-menu-vertical-demo"
				:default-active="1"
				text-color="#fff"
				@open="handleOpen"
				@close="handleClose">
				<el-menu-item index="1" @click="goNodeInfo">
					<el-icon><icon-menu /></el-icon>
					<span>节点信息</span>
				</el-menu-item>
				<el-sub-menu index="2">
					<template #title>
						<el-icon><location /></el-icon>
						<span>数据集管理</span>
					</template>
					<el-menu-item index="2-1" @click="goOriginal"
						>原始数据集</el-menu-item
					>
					<el-menu-item index="2-2" @click="goRuler">对齐规则</el-menu-item>
					<el-menu-item index="2-3" @click="goAlignData"
						>对齐数据集</el-menu-item
					>
				</el-sub-menu>
				<el-menu-item index="3" @click="goNetInfo">
					<el-icon><document /></el-icon>
					<span>网络模型管理</span>
				</el-menu-item>
				<el-menu-item index="4">
					<el-icon><setting /></el-icon>
					<span>Navigator Four</span>
				</el-menu-item>
			</el-menu>
		</el-col>
	</el-row>

	<RouterView />
</template>

<style scoped>
.background {
	/* 最下面的背景 */
	position: absolute;
	left: 0;
	top: 0;
	width: 100%;
	height: 100%;
	background-color: #f6eded;
	z-index: -2;
}
.tac {
	/* 左边导航栏 */
	margin-right: 10px;
	width: 350px;
}

.cuc2 {
	margin: auto;
	width: 90%;
}
.el-menu {
	border-right: 0;
}

.mb-2 {
	font-weight: bold;
	padding-top: 10px;
	text-align: center;
	color: #221815;
	padding-bottom: 20px;
}

.el-menu-item.is-active {
	background-color: #c3868b;
}

.tac .el-col-24 {
	margin: 10px 0 8px 3px;
	max-width: 350px;
	background-color: #a7535a;
	border-radius: 20px;
}
</style>
