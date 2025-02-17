<script setup lang="ts">
import { ref } from "vue";
import Net from "@/components/Net.vue";
import Head from "@/components/Head.vue";
const title = ref("网络模型管理");
</script>

<template>
	<main>

		<Head :title="title"></Head>
		<Net />
	</main>
</template>
<style scoped>
main {
	position: relative;
	overflow-y: auto;
	min-height: 100vh;
}
</style>
