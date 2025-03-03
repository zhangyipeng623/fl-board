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
import { onMounted, ref, computed } from "vue";
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

const defaultOpeneds = ref(["data"]);
const isCollapse = ref(false);

// 计算属性，用于判断当前路由是否为登录页面
const isLoginPage = computed(() => route.path === '/login');
</script>

<template>
	<!-- 如果是登录页面，则只渲染 RouterView -->
	<div v-if="isLoginPage">
		<RouterView />
	</div>
	<!-- 否则渲染主布局 -->
	<div v-else class="app-container">
		<div class="background-container">
			<div class="background-gradient"></div>
			<!-- 新增背景图片层 -->
			<div class="background-image"></div>
			<div class="background-overlay"></div>
		</div>
		<el-menu :collapse="isCollapse" active-text-color="#51c4d3" class="el-menu-vertical"
			:default-active="route.path" text-color="black" :router="isRouter" :default-openeds="defaultOpeneds"
			@open="handleOpen" @close="handleClose">

			<div style="text-align: center; padding-top: 15px">
				<el-image :src="cuc2" class="cuc2" @click="goHome" v-if="!isCollapse"></el-image>
				<el-image :src="cuc1" class="cuc1" @click="goHome" v-if="isCollapse"></el-image>
			</div>
			<el-menu-item index="/node_info">
				<el-icon><icon-menu /></el-icon>
				<template #title>节点信息</template>
			</el-menu-item>
			<el-sub-menu index='data'>
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
	</div>
</template>

<style scoped>
.app-container {
	width: 100%;
	margin: 0;
	font-weight: normal;
	height: 100vh;
	display: flex;
}

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

.background-container {
	position: fixed;
	left: 0;
	top: 0;
	width: 100%;
	height: 100%;
	z-index: -2;
	overflow: hidden;
}

.background-gradient {
	position: absolute;
	width: 100%;
	height: 100%;
	background: linear-gradient(180deg, #d4e8f6, #def1f9);
}

.background-image {
	position: absolute;
	right: 0;
	top: 0;
	width: 80%;
	height: 100%;
	background-image: url("@/assets/images/cuc_1.png");
	background-repeat: no-repeat;
	background-size: 60%;
	/* 减小图片大小 */
	background-position: center;
	opacity: 0.15;
	/* 优化图片渲染 */
	image-rendering: -webkit-optimize-contrast;
	image-rendering: crisp-edges;
}

.background-overlay {
	position: absolute;
	width: 100%;
	height: 100%;
	backdrop-filter: blur(2px);
	/* 减小模糊程度 */
	background-color: rgba(255, 255, 255, 0.02);
	/* 降低遮罩层透明度 */
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