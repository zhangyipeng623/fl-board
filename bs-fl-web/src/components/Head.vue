<script setup lang="ts">
import { RouterView, useRouter } from "vue-router";
import { defineProps } from "vue";
const router = useRouter();
const user_click = () => {
	console.log("user click");
	router.push("/login");
};
const { title } = defineProps(["title"]);
</script>

<template>
	<div class="head">
		<h1 class="title" id="title">
			{{ title }}
		</h1>
		<el-avatar
			class="user-avatar"
			@click="user_click"
			src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
	</div>
	<RouterView />
</template>

<style scoped>
.head {
	width: calc(100% - 20px);
	top: 0;
	position: sticky;
	margin: 10px 10px 0 10px;
	border-radius: 10px;
	background-color: #ffffff;
	display: flex;
	justify-content: space-between;
	align-items: center;
	z-index: 10;
}
.title {
	margin-left: 10px;
}
.user-avatar {
	margin-right: 5px;
}
</style>
