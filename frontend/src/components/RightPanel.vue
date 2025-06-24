<template>
  <div class="right-panel">
    <h2>状态</h2>
    <div class="state-section">
      <h3>世界状态</h3>
      <p>名称: 尚未创建</p>
      <p>地理: ...</p>
    </div>
    <div class="state-section">
      <h3>角色状态</h3>
      <p>姓名: 尚未创建</p>
      <p>背景: ...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// 未来这里将包含从API获取并显示状态的逻辑
</script>

<style scoped>
.right-panel {
  padding: 1rem;
  border-left: 1px solid var(--border-color);
}

h2, h3 {
  margin-top: 0;
}

.state-section {
  margin-bottom: 1.5rem;
}
</style> 