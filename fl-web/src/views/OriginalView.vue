<script setup lang="ts">
import { ref } from "vue";
import Original from "@/components/Original.vue";
import Head from "@/components/Head.vue";
const title = ref("原始数据集");
</script>

<template>
	<main>

		<Head :title="title"></Head>
		<Original />
	</main>
</template>
<style scoped>
main {
	width: 100%;
	position: sticky;
	min-height: 100vh;
}
</style>
