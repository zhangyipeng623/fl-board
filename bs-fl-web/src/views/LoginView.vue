<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { state } from "@/utils/ settings";
import axios from "axios";
const username = ref("");
const password = ref("");
const showLoginDialog = ref(false); // 控制弹窗显示的状态
const router = useRouter();

const handleLogin = async () => {
	// 这里可以添加实际的登录逻辑，比如调用 API
	try {
		const res = await axios.post(state.local_ip_port + "/login", {
			username: username.value,
			password: password.value,
		});
		console.log(res.data);
		localStorage.setItem("userToken", res.data.token); // 示例: 登录后设置 token
		state.updateUserInfo(username.value, res.data.token, true);
		router.push({ name: "home" }); // 登录后重定向到主页
	} catch (error) {
		console.log(error);
		alert("登录失败，请检查用户名和密码");
	}
};

// 在组件挂载时显示登录弹窗
onMounted(() => {
	showLoginDialog.value = true;
});
</script>

<template>
	<div class="login-view">
		<div v-if="showLoginDialog" class="login-dialog">
			<span class="title">账号登录</span>
			<form @submit.prevent="handleLogin">
				<div class="input-group">
					<span class="input-title">用户名:</span>
					<input class="style-input" v-model="username" placeholder="用户名" />
				</div>
				<p></p>
				<div class="input-group">
					<span class="input-title">密码:</span>
					<input
						class="style-input"
						v-model="password"
						type="password"
						placeholder="密码" />
				</div>
				<p></p>
				<div class="button-container">
					<button class="style-button" type="submit">登录</button>
					<p style="text-align: center">
						<button class="style-button" type="button">忘记密码</button>
					</p>
				</div>
			</form>
		</div>
	</div>
</template>

<style scoped>
.button-container {
	margin-top: 20px;
	display: flex;
	justify-content: space-between;
}

.style-button {
	width: 60px;
	height: 30px;
	background-color: #ffffff; /* 按钮的背景颜色 */
	color: black; /* 按钮的文字颜色 */
	border: none; /* 去掉默认边框 */
	border-radius: 5px; /* 圆角边框 */
	cursor: pointer; /* 鼠标悬浮时显示为手型 */
	justify-content: center;
	transition: background-color 0.3s; /* 增加背景颜色变化效果 */
}
.style-button:active {
	transform: scale(0.95); /* 按下时缩小 */
	background-color: grey; /* 按下时背景颜色变化 */
}

.style-input {
	padding: 10px; /* 内边距 */
	border: 2px solid #ebd7d8; /* 边框颜色和大小 */
	border-radius: 5px; /* 圆角边框 */
	outline: none; /* 去掉聚焦时的默认轮廓 */
	transition: border-color 0.3s; /* 增加边框颜色变化效果 */
}
.input-group {
	display: flex; /* 使用 flex 布局 */
	align-items: center; /* 垂直居中对齐 */
}
.input-title {
	width: 80px; /* 标签宽度 */
	margin-right: 10px; /* 标签和输入框之间的间距 */
}

.title {
	font-size: 20px;
	margin-bottom: 20px;
	text-align: center;
}

.login-view {
	position: fixed;
	width: 100%;
	height: 100%;
	z-index: 9999;
}

.login-dialog {
	width: 450x;
	height: 220px;
	border-radius: 10px;
	border: 1px solid #ccc;
	padding: 20px;
	justify-content: center;
	background-color: #ebd7d8;
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
	z-index: 1000;
	/* 确保在最上层 */
}
</style>
