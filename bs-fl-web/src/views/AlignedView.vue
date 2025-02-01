<script setup lang="ts">
import { ref } from "vue";
import Aligned from "@/components/Aligned.vue";
import Head from "@/components/Head.vue";
const title = ref("对齐数据集");
</script>

<template>
	<main>
		<Head :title="title"></Head>
		<Aligned />
	</main>
</template>
<style scoped>
main {
	position: relative;
	overflow-y: auto;
	min-height: 100vh;
}
</style>
