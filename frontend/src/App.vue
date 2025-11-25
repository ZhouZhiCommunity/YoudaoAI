<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
:root {
  --theme-yellow: #ffc107;
  --theme-yellow-light: #fff9c4;
  --theme-yellow-dark: #ffca28;
  --theme-bg-gradient: linear-gradient(135deg, #fffbe0 0%, #fff176 100%);
  --text-dark: #333;
  --text-light: #666;
  --highlight-color: #e67e22;
  --danger-red: #ff4d4f;
  --success-green: #52c41a;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

body {
  margin: 0;
  padding: 0;
}
</style>
