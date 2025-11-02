<template>
  <router-view />
</template>

<script setup>
// App.vue 现在只作为路由容器
// 所有页面逻辑都在各自的路由视图中
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
