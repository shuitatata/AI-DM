<script setup lang="ts">
import { onMounted } from 'vue';
import { useGameStore } from '@/stores/gameStore';
import LeftPanel from './components/LeftPanel.vue';
import ChatWindow from './components/ChatWindow.vue';
import RightPanel from './components/RightPanel.vue';

const gameStore = useGameStore();

onMounted(() => {
  gameStore.initializeSession();
});
</script>

<template>
  <div v-if="gameStore.isInitializing" class="loading-overlay">
    <p>正在初始化会话...</p>
  </div>
  <div v-else-if="gameStore.error" class="error-overlay">
    <p>错误: {{ gameStore.error }}</p>
    <button @click="gameStore.initializeSession">重试</button>
  </div>
  <div v-else id="app-container">
    <LeftPanel class="panel left" />
    <ChatWindow class="panel middle" />
    <RightPanel class="panel right" />
  </div>
</template>

<style scoped>
#app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.panel {
  height: 100%;
  overflow-y: auto;
}

.left {
  flex: 0 0 20%;
  min-width: 250px;
}

.middle {
  flex: 1 1 60%;
}

.right {
  flex: 0 0 20%;
  min-width: 250px;
}

.loading-overlay, .error-overlay {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 1.5rem;
}

.error-overlay button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  font-size: 1rem;
}
</style>
