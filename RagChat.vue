<template>
  <div class="chat-container">
    <h2>APP 鏈嶅姟绔櫤鑳借瘖鏂笌杩愮淮骞冲彴</h2>
    <div class="chat-box" ref="chatBox">
      <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.role]">
        <div class="bubble">
          <div v-if="msg.sources" class="sources">
            <strong>[鍛戒腑鏉ユ簮]锛?/strong>
            <ul>
              <li v-for="doc in msg.sources" :key="doc.id">{{ doc.title }}</li>
            </ul>
          </div>
          <div class="content">{{ msg.content }}</div>
        </div>
      </div>
    </div>
    
    <div class="input-box">
      <input v-model="question" @keyup.enter="sendQuery" placeholder="杈撳叆 GPU銆丆UDA銆丏ocker 鎴栫洃鎺у憡璀﹂棶棰?.." :disabled="loading" />
      <button @click="sendQuery" :disabled="loading">{{ loading ? '鐢熸垚涓?..' : '鍙戦€? }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const question = ref('')
const messages = ref([])
const loading = ref(false)
const chatBox = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight
    }
  })
}

const sendQuery = async () => {
  if (!question.value.trim() || loading.value) return
  
  const userQ = question.value
  question.value = ''
  messages.value.push({ role: 'user', content: userQ })
  
  messages.value.push({ role: 'assistant', sources: null, content: '' })
  const assistantMsg = messages.value[messages.value.length - 1]
  
  loading.value = true

  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/ai/rag-stream-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (localStorage.getItem('gpuops_token') || '')
      },
      body: JSON.stringify({ question: userQ, top_k: 3 })
    })

    if (!response.ok) throw new Error('缃戠粶璇锋眰澶辫触')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() // 淇濈暀鏈畬鎴愮殑娈嬬墖

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const rawJson = line.substring(6)
          try {
            const data = JSON.parse(rawJson)
            if (data.type === 'sources') {
              assistantMsg.sources = data.data
            } else if (data.type === 'content') {
              assistantMsg.content += data.data
              scrollToBottom()
            } else if (data.type === 'done') {
              loading.value = false
            }
          } catch (e) {
            console.error('JSON 瑙ｆ瀽澶辫触', e)
          }
        }
      }
    }
  } catch (err) {
    assistantMsg.content = `[绯荤粺閿欒]: ${err.message}`
    loading.value = false
  }
}
</script>

<style scoped>
.chat-container { width: 600px; margin: 30px auto; font-family: sans-serif; }
.chat-box { height: 400px; border: 1px solid #ccc; border-radius: 8px; padding: 15px; overflow-y: auto; background: #f9f9f9; }
.msg { margin-bottom: 12px; display: flex; flex-direction: column; }
.msg.user { align-items: flex-end; }
.msg.assistant { align-items: flex-start; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 8px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.msg.user .bubble { background: #007bff; color: #fff; }
.sources { font-size: 12px; color: #666; margin-bottom: 6px; border-bottom: 1px dashed #ddd; padding-bottom: 4px; }
.input-box { display: flex; margin-top: 15px; gap: 10px; }
.input-box input { flex: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; }
.input-box button { padding: 8px 16px; background: #28a745; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
</style>


