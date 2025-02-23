<script setup lang="ts">
import { ref } from "vue";
import Ruler from "@/components/Ruler.vue";
import Head from "@/components/Head.vue";
const title = ref("对齐规则");
</script>

<template>
	<main>

		<Head :title="title"></Head>
		<Ruler />
	</main>
</template>
<style scoped>
main {
	width: 100%;
	position: relative;
	overflow-y: auto;
	min-height: 100vh;
}
</style>
