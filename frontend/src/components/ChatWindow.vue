<template>
  <div class="chat-window">
    <div class="messages">
      <div class="message dm">
        <p>DM: 你好，冒险者！欢迎来到AI Dungeon Master的世界。请先在左侧进行设置，然后在右侧创建你的世界和角色。</p>
      </div>
      <div class="message player">
        <p>You: 我准备好了！</p>
      </div>
    </div>
    <div class="input-area">
      <input type="text" placeholder="输入你的行动..." />
      <button>发送</button>
    </div>
  </div>
</template>

<script setup lang="ts">
// 未来这里将包含处理消息发送和接收的逻辑
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
}

.message {
  margin-bottom: 1rem;
}

.message p {
  margin: 0;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  max-width: 80%;
}

.message.dm p {
  background-color: #f1f1f1;
  text-align: left;
}

.message.player p {
  background-color: #d1e7ff;
  margin-left: auto;
  text-align: right;
}


.input-area {
  display: flex;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.input-area input {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 0.5rem;
}

.input-area button {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
}
</style> 