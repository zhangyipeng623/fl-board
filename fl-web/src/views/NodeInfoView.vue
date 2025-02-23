<script setup lang="ts">
import { ref } from "vue";
import NodeInfo from "@/components/NodeInfo.vue";
import Head from "@/components/Head.vue";
// import Background from "@/components/Background.vue";
// import { onMounted, onBeforeUnmount, ref } from "vue";
// import { state } from "@/utils/settings";
// import type { DbNode } from "@/utils/settings";
// import { center } from "@/utils/utils";
// import NodeCard from "@/components/NodeCard.vue";
// import NodeStatus from '@/components/NodeStatus.vue';
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
	width: 100%;
	overflow-y: auto;
	min-height: 100vh;
}
</style>
