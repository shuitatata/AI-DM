<template>
  <div class="right-panel">
    <h2>状态</h2>
    <div class="state-section">
      <h3>世界状态</h3>
      <div v-if="Object.keys(gameStore.worldState).length > 0">
        <p v-for="(value, key) in gameStore.worldState" :key="key">
            <span class="state-key">{{ worldStateMap[key] || key }}:</span>
            <span class="state-value">{{ value || '...' }}</span>
        </p>
      </div>
      <p v-else>世界尚未被创造...</p>
    </div>
    <hr/>
    <div class="state-section">
      <h3>角色状态</h3>
      <div v-if="Object.keys(gameStore.characterState).length > 0">
         <p v-for="(value, key) in gameStore.characterState" :key="key">
            <span class="state-key">{{ characterStateMap[key] || key }}:</span>
            <span class="state-value">{{ value || '...' }}</span>
        </p>
      </div>
      <p v-else>角色尚未被创造...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from '@/stores/gameStore';

const gameStore = useGameStore();

const worldStateMap: Record<string, string> = {
    name: "世界名称",
    geography: "地理环境",
    history: "历史背景",
    cultures: "文化设定",
    magic_system: "魔法体系",
    additional_info: "额外信息"
};

const characterStateMap: Record<string, string> = {
    name: "角色名称",
    physical_appearance: "外貌描述",
    background: "背景故事",
    internal_motivation: "内在动机",
    unique_traits: "独特特征",
    additional_info: "额外信息"
};

</script>

<style scoped>
.right-panel {
  padding: 1rem;
  border-left: 1px solid var(--border-color);
  background-color: #fcfcfc;
}

h2, h3 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.state-section {
  margin-bottom: 1.5rem;
}
.state-section p {
    margin: 0.5rem 0;
    line-height: 1.6;
}
.state-key {
    font-weight: bold;
    margin-right: 0.5rem;
    color: #333;
}
.state-value {
    color: #555;
}
hr {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 1.5rem 0;
}
</style> 