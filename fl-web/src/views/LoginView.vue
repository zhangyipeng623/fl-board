<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { state } from "@/utils/settings";
import { center } from "@/utils/utils";
import { User, Lock, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'  // 添加 ElMessage 导入
import backgroundImage from "@/assets/images/login.jpg";
const username = ref("");
const password = ref("");
const showLoginDialog = ref(false); // 控制弹窗显示的状态
const loading = ref(false);
const router = useRouter();

const handleLogin = async () => {
	// 添加表单验证
	if (!username.value || !password.value) {
		ElMessage({
			message: '请输入用户名和密码',
			type: 'warning',
			showClose: true,
			duration: 2000
		});
		return;
	}

	loading.value = true;
	try {
		const res = await center.post("/login", {
			username: username.value,
			password: password.value,
		});

		localStorage.setItem("userSession", res.data.session);
		localStorage.setItem("username", username.value);
		localStorage.setItem("ip", res.data.ip);
		state.updateCenterInfo(true);
		state.updateUserInfo(
			res.data.id,
			username.value,
			res.data.ip,
			res.data.port,
			true
		);
		ElMessage({
			message: '登录成功',
			type: 'success',
			showClose: true,
			duration: 2000
		});
		router.push({ name: "home" });
	} catch (error: any) {
		console.error('登录错误详情:', {
			error,
			response: error?.response,
			data: error?.response?.data,
			message: error?.response?.data?.message
		});

		nextTick(() => {
			// 确保在控制台也能看到消息内容
			const message = error.response?.data?.detail || '登录失败：服务器连接异常';
			console.log('将要显示的错误消息:', message);

			alert('登录失败：' + message)
		});
	} finally {
		loading.value = false;
	}
};

// 在组件挂载时显示登录弹窗
onMounted(() => {
	showLoginDialog.value = true;
});
</script>

<template>
	<div class="login-view">
		<div class="background-container">
			<img :src="backgroundImage" alt="Background" class="background-image" />
			<div class="background-overlay"></div>
		</div>
		<div v-if="showLoginDialog" class="login-dialog">
			<span class="welcome">欢迎登录</span>
			<form @submit.prevent="handleLogin">
				<div class="input-group">
					<el-icon class="input-icon">
						<User />
					</el-icon>
					<input class="style-input" v-model="username" placeholder="用户名" />
				</div>
				<div class="input-group">
					<el-icon class="input-icon">
						<Lock />
					</el-icon>
					<input class="style-input" v-model="password" type="password" placeholder="密码" />
				</div>
				<div class="button-container">
					<button class="style-button" type="submit" :disabled="loading">
						<span v-if="!loading">登录</span>
						<el-icon v-else class="is-loading">
							<Loading />
						</el-icon>
					</button>
				</div>
			</form>
		</div>
	</div>
</template>

<style scoped>
.login-view {
	position: fixed;
	width: 100%;
	height: 100%;
	z-index: 9999;
	display: flex;
	justify-content: center;
	align-items: center;
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

.background-image {
	width: 100%;
	height: 100%;
	object-fit: cover;
	animation: starMove 3.5s cubic-bezier(0.22, 0.61, 0.36, 1) forwards;
	transform-origin: center center;
	will-change: transform, filter;
}

@keyframes starMove {
	0% {
		transform: scale(1.3) rotate(-8deg);
		filter: brightness(0.7);
	}

	100% {
		transform: scale(1.04) rotate(1deg);
		/* 最后稍微放大并轻微旋转 */
		filter: brightness(1);
	}
}

.background-overlay {
	position: absolute;
	width: 100%;
	height: 100%;
	backdrop-filter: blur(2px);
	background-color: rgba(0, 0, 0, 0.3);
	/* 降低初始透明度 */
	opacity: 0;
	animation: overlayFade 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes overlayFade {
	0% {
		opacity: 0;
		backdrop-filter: blur(1px);
		/* 初始就有轻微模糊 */
	}

	100% {
		opacity: 0.5;
		/* 降低最终透明度 */
		backdrop-filter: blur(2px);
	}
}

.login-dialog {
	width: 350px;
	padding: 40px 20px;
	/* 增加上下内边距 */
	border-radius: 10px;
	background-color: transparent;
	/* 设置为全透明 */
	box-shadow: none;
	/* 移除阴影 */
	text-align: center;
	/* 居中对齐 */
	opacity: 0;
	animation: fadeIn 1s ease-out 1s forwards;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(20px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.welcome {
	font-size: 32px;
	/* 增大字体 */
	color: #fff;
	text-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
	/* 添加文字阴影效果 */
}

.input-group {
	display: flex;
	align-items: center;
	margin-bottom: 20px;
	position: relative;
	border-radius: 20px;
}

.input-icon {
	position: absolute;
	left: 15px;
	color: rgba(255, 255, 255, 0.9);
	/* 增加透明度 */
	font-size: 18px;
	/* 调整图标大小 */
}

.style-input {
	padding: 12px 12px 12px 40px;
	border: 1px solid rgba(255, 255, 255, 0.5);
	border-radius: 50px;
	outline: none;
	transition: all 0.3s ease;
	width: 100%;
	background-color: rgba(255, 255, 255, 0.1);
	color: #ffffff;
	position: relative;
	z-index: 1;
	font-size: 16px;
	/* 增大字体大小 */
	font-weight: 400;
	/* 调整字重 */
	letter-spacing: 0.5px;
	/* 增加字间距 */
}

/* 移除输入框的模糊效果，只保留背景半透明 */
.style-input {
	backdrop-filter: none;
}

.style-input::placeholder {
	color: rgba(255, 255, 255, 0.7);
	font-size: 16px;
	/* 占位符字体大小也相应调整 */
}

.style-input:focus {
	border-color: #00F5A0;
	box-shadow: 0 0 10px rgba(0, 217, 245, 0.2);
	background-color: rgba(255, 255, 255, 0.15);
}

.button-container {
	margin-top: 20px;
	display: flex;
	justify-content: center;
}

.style-button {
	width: 120px;
	height: 40px;
	background: linear-gradient(45deg, #00F5A0, #00D9F5);
	color: white;
	border: none;
	border-radius: 50px;
	cursor: pointer;
	transition: all 0.3s ease;
	font-weight: 500;
	letter-spacing: 1px;
	box-shadow: 0 2px 10px rgba(0, 217, 245, 0.3);
}

.style-button:hover {
	background: linear-gradient(45deg, #00D9F5, #00F5A0);
	transform: translateY(-2px);
	box-shadow: 0 4px 15px rgba(0, 245, 160, 0.4);
}

.style-button:active {
	transform: scale(0.95) translateY(0);
	box-shadow: 0 2px 8px rgba(0, 217, 245, 0.3);
}

.style-button:disabled {
	opacity: 0.7;
	cursor: not-allowed;
}

.is-loading {
	animation: rotating 2s linear infinite;
}

@keyframes rotating {
	from {
		transform: rotate(0);
	}

	to {
		transform: rotate(360deg);
	}
}
</style>