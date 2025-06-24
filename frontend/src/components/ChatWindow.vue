<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer">
      <div v-for="message in gameStore.messages" :key="message.id" class="message" :class="message.sender === 'Player' ? 'player' : 'dm'">
        <p v-html="formatMessage(message.text)"></p>
      </div>
      <div v-if="gameStore.isReplying" class="message dm">
        <p><i>DM 正在思考中...</i></p>
      </div>
    </div>
    <div class="input-area">
      <input 
        type="text" 
        v-model="userInput"
        @keyup.enter="sendMessage"
        :disabled="gameStore.isReplying || gameStore.gamePhase === 'GAME_OVER'"
        placeholder="输入你的想法..." 
      />
      <button 
        @click="sendMessage"
        :disabled="gameStore.isReplying || gameStore.gamePhase === 'GAME_OVER'">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useGameStore } from '@/stores/gameStore';
import DOMPurify from 'dompurify';

const gameStore = useGameStore();
const userInput = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

const sendMessage = () => {
  if (userInput.value.trim() && !gameStore.isReplying) {
    if (gameStore.gamePhase === 'WORLD_CREATION') {
        gameStore.sendAgentMessage(userInput.value, 'world-builder');
    } else if (gameStore.gamePhase === 'CHARACTER_CREATION') {
        gameStore.sendAgentMessage(userInput.value, 'character-manager');
    }
    // TODO: Add other game phases
    userInput.value = '';
  }
};

const formatMessage = (text: string) => {
    const sanitized = DOMPurify.sanitize(text.replace(/\n/g, '<br>'));
    return sanitized;
}

const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
    });
};

watch(() => gameStore.messages, scrollToBottom, { deep: true });
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 改为视口高度 */
  max-height: 100vh;
}

.messages {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  background-color: #fff;
}

.message {
  margin-bottom: 1rem;
  display: flex;
}

.message p {
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 85%;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.dm {
    justify-content: flex-start;
}
.message.dm p {
  background-color: #f1f1f1;
  color: #333;
  border-bottom-left-radius: 2px;
}

.message.player {
    justify-content: flex-end;
}
.message.player p {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 2px;
}

.input-area {
  display: flex;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: #fcfcfc;
}

.input-area input {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
}
.input-area input:disabled {
    background-color: #eee;
}

.input-area button {
  margin-left: 1rem;
  padding: 0.5rem 1.5rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1rem;
}
.input-area button:hover {
    background-color: #0056b3;
}
.input-area button:disabled {
    background-color: #a0a0a0;
    cursor: not-allowed;
}
</style> 