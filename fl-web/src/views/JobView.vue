<script setup lang="ts">
import { ref } from "vue";
import Job from "@/components/Job.vue";
import Head from "@/components/Head.vue";
const title = ref("任务");
</script>

<template>
	<main>

		<Head :title="title"></Head>
		<Job />
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
