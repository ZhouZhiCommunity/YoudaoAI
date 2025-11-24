<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { rewriteFile } from '@/api'

const router = useRouter()
const route = useRoute()

// 状态管理
const progress = ref(0)
const status = ref('processing') // processing, success, error
const fileName = ref('')
const fileSize = ref(0)
const errorMessage = ref('')
const resultData = ref(null)

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 处理文件
const processFile = async (file) => {
  try {
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 15
        if (progress.value > 90) progress.value = 90
      }
    }, 500)
    
    // 调用API
    const response = await rewriteFile(file, 0.5, true)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    if (response.success) {
      status.value = 'success'
      resultData.value = response
      
      // 1秒后跳转到结果页
      setTimeout(() => {
        router.push({
          name: 'result',
          query: {
            mode: 'file',
            data: JSON.stringify(response)
          }
        })
      }, 1000)
    } else {
      status.value = 'error'
      errorMessage.value = response.error || '处理失败'
    }
  } catch (error) {
    status.value = 'error'
    errorMessage.value = '网络错误或后端服务未启动'
    console.error('处理失败:', error)
  }
}

// 返回首页
const goBack = () => {
  router.push({ name: 'home' })
}

onMounted(() => {
  // 从路由state获取文件
  const file = history.state.file
  
  if (!file) {
    // 如果没有文件，尝试从sessionStorage获取文件信息
    const fileInfo = sessionStorage.getItem('uploadFile')
    if (fileInfo) {
      const info = JSON.parse(fileInfo)
      fileName.value = info.name
      fileSize.value = info.size
      
      // 注意：这里无法获取实际的File对象，需要重新上传
      alert('文件信息丢失，请返回重新上传')
      router.push({ name: 'home' })
    } else {
      alert('未找到上传文件')
      router.push({ name: 'home' })
    }
  } else {
    fileName.value = file.name
    fileSize.value = file.size
    processFile(file)
  }
})
</script>

<template>
  <div class="process-page">
    <div id="background-container">
      <div class="ambient-blobs">
        <div class="blob"></div>
        <div class="blob"></div>
        <div class="blob"></div>
      </div>
      <canvas id="particle-canvas"></canvas>
    </div>

    <div class="processing-card">
    <!-- 处理中状态 -->
    <div v-if="status === 'processing'">
      <div class="spinner-container">
        <div class="spinner"></div>
      </div>

      <div class="status-title">正在处理文件...</div>

      <div class="file-info" v-if="fileName">
        <div class="file-name">📄 {{ fileName }}</div>
        <div class="file-size">文件大小: {{ formatFileSize(fileSize) }}</div>
      </div>

      <div class="progress-wrapper">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>

      <div class="loading-text">{{ Math.round(progress) }}% 完成</div>

      <div class="tip-text">
        正在使用高级重写智能算法改写您的文档，请稍候...
      </div>
    </div>

    <!-- 成功状态 -->
    <div v-if="status === 'success'" style="text-align: center;">
      <div style="font-size: 60px; margin-bottom: 20px;">✅</div>
      <div class="status-title" style="color: var(--success-green);">处理完成！</div>
      <div class="loading-text">正在跳转到结果页面...</div>
    </div>

    <!-- 错误状态 -->
    <div v-if="status === 'error'" style="text-align: center;">
      <div style="font-size: 60px; margin-bottom: 20px;">❌</div>
      <div class="status-title" style="color: var(--danger-red);">处理失败</div>
      <div class="loading-text" style="color: var(--danger-red);">{{ errorMessage }}</div>
      <button @click="goBack" style="margin-top: 30px; padding: 12px 40px; background: var(--theme-yellow); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600;">
        返回首页
      </button>
    </div>
    </div>
  </div>
</template>

<style scoped>
    /* --- 1. 全局变量与背景 (与首页完全保持一致) --- */
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

    /* 页面容器 - 居中显示 */
    .process-page {
        background: var(--theme-bg-gradient);
        color: var(--text-dark);
        min-height: 100vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* --- 背景动效层 (复用首页代码) --- */
    #background-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -5;
    }

    .ambient-blobs {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        filter: blur(80px);
        opacity: 0.7;
    }

    .blob {
        position: absolute;
        background: rgba(255, 215, 0, 0.5);
        border-radius: 50%;
        animation: blob-float 20s infinite ease-in-out alternate;
    }

    .blob:nth-child(1) { width: 500px; height: 500px; top: -10%; left: -10%; background: rgba(255, 235, 59, 0.4); animation-duration: 25s; }
    .blob:nth-child(2) { width: 600px; height: 600px; bottom: -15%; right: -15%; background: rgba(255, 193, 7, 0.3); animation-duration: 30s; animation-delay: -5s; }
    .blob:nth-child(3) { width: 400px; height: 400px; bottom: 30%; left: 20%; background: rgba(255, 160, 0, 0.25); animation-duration: 22s; animation-delay: -10s; }

    @keyframes blob-float {
        0% { transform: translate(0, 0) scale(1) rotate(0deg); }
        100% { transform: translate(50px, -50px) scale(1.05) rotate(10deg); }
    }

    #particle-canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }

    /* --- 2. 处理状态卡片 (参考图样式) --- */
    .processing-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        width: 600px; /* 稍微宽一点，显得大气 */
        padding: 50px 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(255, 193, 7, 0.2), inset 0 0 20px rgba(255, 255, 255, 0.8);
        border: 2px solid rgba(255, 243, 224, 0.6);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        animation: card-entry 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    @keyframes card-entry {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    /* 加载圈 Spinner */
    .spinner-container {
        margin-bottom: 25px;
        position: relative;
    }

    .spinner {
        width: 60px;
        height: 60px;
        border: 5px solid #fff3e0; /* 浅底色 */
        border-top: 5px solid var(--theme-yellow); /* 主题色 */
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* 状态文字 */
    .status-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 30px;
        letter-spacing: 1px;
    }

    /* 进度条容器 */
    .progress-wrapper {
        width: 100%;
        background-color: #f0f0f0;
        height: 10px;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 20px;
        position: relative;
    }

    /* 进度条本体 */
    .progress-bar {
        height: 100%;
        width: 0%; /* 初始宽度 */
        background: linear-gradient(90deg, var(--theme-yellow) 0%, var(--highlight-color) 100%);
        border-radius: 10px;
        transition: width 0.4s ease;
        position: relative;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.5);
    }

    /* 进度条上的流光动画 */
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(
            45deg, 
            rgba(255,255,255,0.2) 25%, 
            transparent 25%, 
            transparent 50%, 
            rgba(255,255,255,0.2) 50%, 
            rgba(255,255,255,0.2) 75%, 
            transparent 75%, 
            transparent
        );
        background-size: 20px 20px;
        animation: progress-stripe 1s linear infinite;
    }

    @keyframes progress-stripe {
        0% { background-position: 0 0; }
        100% { background-position: 20px 20px; }
    }

    /* 加载状态描述 */
    .loading-text {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 15px;
    }

    /* 底部提示小字 */
    .tip-text {
        font-size: 12px;
        color: #999;
        line-height: 1.6;
        max-width: 90%;
    }

    /* 文件信息样式 */
    .file-info {
        width: 100%;
        margin-bottom: 25px;
        padding: 15px;
        background: rgba(255, 243, 224, 0.3);
        border-radius: 10px;
        border: 1px solid rgba(255, 193, 7, 0.2);
    }

    .file-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-dark);
        margin-bottom: 8px;
        word-break: break-all;
    }

    .file-size {
        font-size: 14px;
        color: var(--text-light);
    }

</style>
