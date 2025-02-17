<script setup lang="ts">
import { RouterView, useRouter } from "vue-router";
import { defineProps } from "vue";
import { center ,user} from "@/utils/utils";
import { state } from "@/utils/settings"
import head from "@/assets/images/head.png";
const router = useRouter();

const user_click = () => {
	console.log("user click");
	if (state.user.is_connect) {
		router.push("/");
	} else {
		router.push("/login");
	}
};
const logout = () => {
	console.log("logout");
	center
		.get("/logout", {
			params: {
				session: localStorage.getItem("userSession"),
			},
		})
		.then(() => {
			user.get( "/logout", {
				params: {
					session: localStorage.getItem("localSession"),
				},
			});
		})
		.catch((error) => {
			console.error("Error logging out:", error);
		});
	localStorage.removeItem("userSession"); // 示例: 登录后设置 token
	localStorage.removeItem("username");
	localStorage.removeItem("ip");
	state.updateUserInfo(0, "本地节点", "", "", false);
	router.push("/login");
};
const { title } = defineProps(["title"]);
</script>

<template>
	<div class="head">
		<h1 class="title" id="title">
			{{ title }}
		</h1>
		<el-dropdown size="large" type="primary">
			<el-avatar
				class="user-avatar"
				@click="user_click"
				:src = head />
			<template #dropdown>
				<el-dropdown-menu v-if="state.user.is_connect">
					<el-dropdown-item>{{ state.user.name }}</el-dropdown-item>
					<el-dropdown-item @click="logout">登出</el-dropdown-item>
				</el-dropdown-menu>
				<el-dropdown-menu v-else>
					<el-dropdown-item @click="router.push('/login')"
						>登录</el-dropdown-item
					>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
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
	background-color: rgba(255, 255, 255, 0.5);
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
	cursor: pointer;
}
</style>
