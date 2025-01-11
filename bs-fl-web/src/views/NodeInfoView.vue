<script setup lang="ts">
import { ref } from "vue";
import NodeInfo from "@/components/NodeInfo.vue";
import Head from "@/components/Head.vue";
const title = ref("节点信息");
</script>

<template>
	<main>
		<Head :title="title"></Head>
		<NodeInfo />
	</main>
</template>

<style scoped>
main {
	position: relative;
	overflow-y: auto;
	min-height: 100vh;
}
</style>
