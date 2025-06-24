<template>
  <div class="left-panel">
    <h2>设置</h2>
    <div class="setting-item">
      <label for="model-select">模型选择</label>
      <select id="model-select">
        <option>GPT-4o</option>
        <option>GPT-3.5-Turbo</option>
      </select>
    </div>
    <div class="setting-item">
      <label for="temperature">温度</label>
      <input type="range" id="temperature" min="0" max="1" step="0.1" />
    </div>
  </div>
</template>

<script setup lang="ts">
// 未来这里将包含处理设置变化的逻辑
</script>

<style scoped>
.left-panel {
  padding: 1rem;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

h2 {
  margin-top: 0;
}

.setting-item {
  display: flex;
  flex-direction: column;
}

.setting-item label {
  margin-bottom: 0.5rem;
}
</style> 