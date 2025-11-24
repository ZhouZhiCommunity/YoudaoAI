<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { rewriteText, rewriteFile } from '@/api'

const router = useRouter()

// 状态管理
const currentMode = ref('text')
const textInput = ref('')
const uploadedFile = ref(null)
const uploadTime = ref('')
const isDragging = ref(false)
const isProcessing = ref(false)
const fileInput = ref(null)
const particleCanvas = ref(null)

// 切换模式
const switchMode = (mode) => {
  currentMode.value = mode
}

// 更新字数
const updateCount = () => {
  // 字数通过v-model自动更新
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}

// 文件处理
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    handleFileSelect(file)
  }
}

const handleFileSelect = (file) => {
  const allowedExtensions = ['.pdf', '.docx', '.txt', '.md']
  const maxFileSize = 10 * 1024 * 1024
  
  const fileName = file.name
  const fileExtension = fileName.substring(fileName.lastIndexOf('.')).toLowerCase()
  
  if (!allowedExtensions.includes(fileExtension)) {
    alert(`文件格式错误：只支持 ${allowedExtensions.join(', ')} 格式`)
    return
  }
  
  if (file.size > maxFileSize) {
    alert(`文件太大：最大上传限制为 ${formatFileSize(maxFileSize)}`)
    return
  }
  
  uploadedFile.value = file
  uploadTime.value = getCurrentTimeStr()
}

const resetFileSelection = () => {
  uploadedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 拖拽处理
const handleDragEnter = () => {
  isDragging.value = true
}

const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFileSelect(files[0])
  }
}

// 工具函数
const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getCurrentTimeStr = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hour = String(now.getHours()).padStart(2, '0')
  const minute = String(now.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hour}:${minute}`
}

// 提交任务
const submitJob = async () => {
  if (isProcessing.value) return
  
  try {
    isProcessing.value = true
    
    if (currentMode.value === 'text') {
      const content = textInput.value.trim()
      if (!content) {
        alert('请先输入文本内容')
        return
      }
      
      const response = await rewriteText(content, 0.5, true)
      
      if (response.success) {
        router.push({
          name: 'result',
          query: {
            mode: 'text',
            data: JSON.stringify(response)
          }
        })
      } else {
        alert('改写失败: ' + response.error)
      }
    } else {
      if (!uploadedFile.value) {
        alert('请先选择文件')
        return
      }
      
      // 将文件信息存储到sessionStorage，因为路由参数不能传递File对象
      sessionStorage.setItem('uploadFile', JSON.stringify({
        name: uploadedFile.value.name,
        size: uploadedFile.value.size,
        type: uploadedFile.value.type
      }))
      
      // 创建FormData并存储
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      
      // 跳转到处理页面
      router.push({
        name: 'process',
        state: { file: uploadedFile.value }
      })
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请检查后端服务是否启动')
  } finally {
    isProcessing.value = false
  }
}

// Canvas粒子动画
let particles = []
let mouse = { x: null, y: null, radius: 150 }
let animationId = null

const initParticleAnimation = () => {
  const canvas = particleCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  let width = canvas.width = window.innerWidth
  let height = canvas.height = window.innerHeight
  
  class Particle {
    constructor() {
      this.x = Math.random() * width
      this.y = Math.random() * height
      this.size = Math.random() * 3 + 1
      this.speedX = Math.random() * 1 - 0.5
      this.speedY = Math.random() * 1 - 0.5
      this.color = `rgba(255, 193, 7, ${Math.random() * 0.6 + 0.2})`
    }
    
    update() {
      if (this.x > width || this.x < 0) this.speedX = -this.speedX
      if (this.y > height || this.y < 0) this.speedY = -this.speedY
      
      let dx = mouse.x - this.x
      let dy = mouse.y - this.y
      let distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < mouse.radius) {
        if (mouse.x < this.x && this.x < width - this.size * 10) this.x += 2
        if (mouse.x > this.x && this.x > this.size * 10) this.x -= 2
        if (mouse.y < this.y && this.y < height - this.size * 10) this.y += 2
        if (mouse.y > this.y && this.y > this.size * 10) this.y -= 2
      }
      
      this.x += this.speedX
      this.y += this.speedY
    }
    
    draw() {
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.fillStyle = this.color
      ctx.fill()
    }
  }
  
  const initParticles = () => {
    particles = []
    let numberOfParticles = (width * height) / 15000
    for (let i = 0; i < numberOfParticles; i++) {
      particles.push(new Particle())
    }
  }
  
  const connect = () => {
    for (let a = 0; a < particles.length; a++) {
      for (let b = a; b < particles.length; b++) {
        let distance = ((particles[a].x - particles[b].x) * (particles[a].x - particles[b].x)) +
                       ((particles[a].y - particles[b].y) * (particles[a].y - particles[b].y))
        
        if (distance < (width / 7) * (height / 7)) {
          let opacityValue = 1 - (distance / 15000)
          ctx.strokeStyle = `rgba(255, 215, 0, ${opacityValue * 0.5})`
          ctx.lineWidth = 1
          ctx.beginPath()
          ctx.moveTo(particles[a].x, particles[a].y)
          ctx.lineTo(particles[b].x, particles[b].y)
          ctx.stroke()
        }
      }
    }
  }
  
  const animate = () => {
    animationId = requestAnimationFrame(animate)
    ctx.clearRect(0, 0, width, height)
    for (let i = 0; i < particles.length; i++) {
      particles[i].update()
      particles[i].draw()
    }
    connect()
  }
  
  const handleResize = () => {
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
    initParticles()
  }
  
  const handleMouseMove = (e) => {
    mouse.x = e.x
    mouse.y = e.y
  }
  
  const handleMouseOut = () => {
    mouse.x = undefined
    mouse.y = undefined
  }
  
  window.addEventListener('resize', handleResize)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseout', handleMouseOut)
  
  initParticles()
  animate()
  
  return () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('mousemove', handleMouseMove)
    window.removeEventListener('mouseout', handleMouseOut)
    if (animationId) {
      cancelAnimationFrame(animationId)
    }
  }
}

onMounted(() => {
  const cleanup = initParticleAnimation()
  onUnmounted(() => {
    if (cleanup) cleanup()
  })
})
</script>

<template>
  <div id="background-container">
    <div class="ambient-blobs">
      <div class="blob"></div>
      <div class="blob"></div>
      <div class="blob"></div>
    </div>
    <canvas ref="particleCanvas" id="particle-canvas"></canvas>
  </div>

  <header>
    <div class="logo">
      <img src="/有道降AI.jpg" alt="有道降AI Logo" class="logo-img">
      <span class="logo-text">有道降AI</span>
    </div>
    <nav>
      <ul>
        <li><a href="#" class="active">首页</a></li>
      </ul>
    </nav>
  </header>

  <main class="hero-section">
    <div class="main-text">
      <span class="subtitle-badge">AI率直接手降不下来？</span>
      <div class="sub-text">降AIGC率权威平台, <span class="highlight-orange">我们是您值得信赖的学术伙伴。</span></div>
      <h1>降重 · <span>降AI</span></h1>
      <div class="sub-desc">超十亿文本实测，<span class="highlight-orange">达标率超过97%</span></div>
    </div>

    <div class="upload-card">
      <div class="tab-header">
        <div :class="['tab-btn', { active: currentMode === 'text' }]" @click="switchMode('text')">粘贴文本</div>
        <div :class="['tab-btn', { active: currentMode === 'file' }]" @click="switchMode('file')">上传文档</div>
      </div>

      <!-- 文本输入模式 -->
      <div v-show="currentMode === 'text'" class="mode-container active">
        <textarea 
          v-model="textInput"
          class="text-input-area" 
          placeholder="把你的AI生成内容粘贴到这里，让它无法被发现。为了获得最佳效果，建议去除非正文内容..."
          @input="updateCount"></textarea>
        <div class="word-count">总计 <span>{{ textInput.length }}</span> 字</div>
      </div>

      <!-- 文件上传模式 -->
      <div v-show="currentMode === 'file'" class="mode-container active">
        <input 
          ref="fileInput"
          type="file" 
          id="file-input" 
          accept=".pdf,.docx,.txt,.md" 
          @change="handleFileChange"
          style="display: none;">

        <!-- 默认上传区域 -->
        <div 
          v-show="!uploadedFile"
          class="upload-area"
          :class="{ 'drag-over': isDragging }"
          @click="triggerFileInput"
          @dragenter.prevent="handleDragEnter"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop">
          <div class="file-upload-content">
            <div class="file-icon">📄</div>
            <div class="upload-title">点击或拖拽文档到此处上传</div>
            <div class="upload-tips">支持 <span class="orange-tip">.pdf, .docx, .txt, .md</span> 格式</div>
            <div class="upload-tips orange-tip">✨ 建议先删掉文档中除正文以外的内容，避免字符数冗余</div>
            <div class="upload-tips">💾 最大上传 10 MB 的文档</div>
          </div>
        </div>

        <!-- 已上传文件信息 -->
        <div v-show="uploadedFile" class="uploaded-file-info active">
          <div class="success-icon-container">
            <div class="success-tick">
              <svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
          </div>
          
          <div class="file-name-row">
            <span class="small-file-icon">📄</span>
            <span>{{ uploadedFile?.name }}</span>
          </div>

          <div class="file-meta">
            文件大小: <span>{{ formatFileSize(uploadedFile?.size) }}</span>
          </div>

          <div class="file-time">
            <span>上传时间: {{ uploadTime }}</span>
          </div>

          <button class="reupload-btn" @click="resetFileSelection">
            <span>×</span> 重新选择文件
          </button>
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="action-btn-container">
        <button class="action-btn" @click="submitJob" :disabled="isProcessing">
          {{ isProcessing ? '处理中...' : '立即降重降AI →' }}
        </button>
      </div>
    </div>
  </main>
</template>

<style scoped>
    /* --- 全局重置与变量 --- */
    :root {
        --theme-yellow: #ffc107;   /* 主题黄色 */
        --theme-yellow-light: #fff9c4; /* 更亮的浅黄色 */
        --theme-yellow-dark: #ffca28; /* 深一点的黄色 */
        /* 背景渐变改为更丰富的金色系 */
        --theme-bg-gradient: linear-gradient(135deg, #fffbe0 0%, #fff176 100%); 
        --text-dark: #333;
        --text-light: #666;
        --highlight-color: #e67e22;
        --shadow-color: rgba(255, 193, 7, 0.3);
        --danger-red: #ff4d4f;      
        --danger-bg: #fff1f0;       
        --success-green: #52c41a;   
        --success-bg: #f6ffed;      
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    /* --- 全新动态背景设计 --- */
    body {
        background: var(--theme-bg-gradient);
        color: var(--text-dark);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
        /* 移除旧的静态背景图 */
    }

    /* 背景层容器，用于放置 Canvas 和光斑 */
    #background-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -5; /* 确保在最底层 */
        overflow: hidden;
    }

    /* 1. 底层：流动的金色光斑 (CSS动画) */
    .ambient-blobs {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -2;
        filter: blur(80px); /* 极强的高斯模糊产生光晕效果 */
        opacity: 0.7;
    }

    .blob {
        position: absolute;
        background: rgba(255, 215, 0, 0.5); /* 金色 */
        border-radius: 50%;
        animation: blob-float 20s infinite ease-in-out alternate;
    }

    .blob:nth-child(1) {
        width: 500px; height: 500px;
        top: -10%; left: -10%;
        background: rgba(255, 235, 59, 0.4);
        animation-duration: 25s;
    }
    .blob:nth-child(2) {
        width: 600px; height: 600px;
        bottom: -15%; right: -15%;
        background: rgba(255, 193, 7, 0.3);
        animation-duration: 30s;
        animation-delay: -5s;
    }
    .blob:nth-child(3) {
        width: 400px; height: 400px;
        bottom: 30%; left: 20%;
        background: rgba(255, 160, 0, 0.25);
        animation-duration: 22s;
        animation-delay: -10s;
    }

    @keyframes blob-float {
        0% { transform: translate(0, 0) scale(1) rotate(0deg); }
        33% { transform: translate(100px, 50px) scale(1.1) rotate(20deg); border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;}
        66% { transform: translate(-50px, 150px) scale(0.9) rotate(-10deg); border-radius: 40% 60% 70% 30% / 50% 60% 30% 60%;}
        100% { transform: translate(50px, -50px) scale(1.05) rotate(10deg); }
    }

    /* 2. 顶层：Canvas 粒子网络 */
    #particle-canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* 在光斑之上，内容之下 */
    }

    /* --- 导航栏 --- */
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 40px;
        /* 背景色稍微调得更通透一点，配合新背景 */
        background: rgba(255, 253, 235, 0.75); 
        backdrop-filter: blur(15px); /* 增强毛玻璃效果 */
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 4px 30px rgba(255, 193, 7, 0.1); 
        border-bottom: none; 
        transition: all 0.3s;
    }

    .logo {
        display: flex;
        align-items: center;
        cursor: pointer;
    }

    .logo-img {
        width: 48px;
        height: 48px;
        margin-right: 12px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        border-radius: 8px;
    }

    .logo-text {
        font-family: "YouYuan", "Microsoft YaHei UI", "PingFang SC", sans-serif;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #5d4037; 
        text-shadow: 2px 2px 0px #ffc107, 4px 4px 0px rgba(255, 193, 7, 0.2);
        transform: skewX(-5deg);
        display: inline-block;
        transition: transform 0.3s;
    }

    .logo:hover .logo-text {
        transform: skewX(-5deg) scale(1.05);
    }

    nav ul {
        list-style: none;
        display: flex;
        gap: 30px;
        align-items: center;
    }

    nav a {
        text-decoration: none;
        color: #6d4c41;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s;
        position: relative;
    }

    nav a:hover {
        color: var(--highlight-color);
    }

    nav a::after {
        content: '';
        position: absolute;
        bottom: -6px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 3px;
        background-color: var(--highlight-color);
        transition: width 0.3s ease;
        border-radius: 2px;
    }

    nav a:hover::after {
        width: 80%;
    }

    nav a.active {
        background-color: rgba(255, 193, 7, 0.15);
        color: #bf360c;
        padding: 6px 20px;
        border-radius: 20px;
    }
    nav a.active::after { display: none; }

    /* --- 主要内容区 --- */
    .hero-section {
        text-align: center;
        padding-top: 70px;
        padding-bottom: 90px;
    }

    h1 {
        font-size: 68px;
        color: var(--text-dark);
        margin-bottom: 20px;
        letter-spacing: 3px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.08);
        position: relative;
    }

    h1 span {
        color: var(--theme-yellow);
        position: relative;
        z-index: 1;
        display: inline-block;
        animation: pulse-text 3s infinite ease-in-out;
    }

    @keyframes pulse-text {
        0%, 100% { transform: scale(1); text-shadow: 3px 3px 6px rgba(0,0,0,0.08); }
        50% { transform: scale(1.05); text-shadow: 0 0 15px rgba(255, 193, 7, 0.6); }
    }

    h1 span::after {
        content: '';
        position: absolute;
        bottom: 8px;
        left: 0;
        width: 100%;
        height: 14px;
        background-color: rgba(255, 193, 7, 0.4);
        z-index: -1;
        border-radius: 8px;
        transform: skewX(-10deg);
    }

    .subtitle-badge {
        background: linear-gradient(to right, var(--theme-yellow), #ffb300);
        color: #000;
        font-size: 14px;
        padding: 6px 14px;
        border-radius: 16px;
        vertical-align: middle;
        margin-right: 10px;
        font-weight: 800;
        box-shadow: 0 4px 12px var(--shadow-color);
        letter-spacing: 0.5px;
    }

    .sub-text {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .sub-desc {
        font-size: 16px;
        color: var(--text-light);
        margin-bottom: 50px;
        font-weight: 500;
    }

    .highlight-orange {
        color: var(--highlight-color);
        font-weight: 800;
        font-size: 1.15em;
    }

    /* --- 上传卡片区域 --- */
    .upload-card {
        background: rgba(255, 255, 255, 0.9); /* 稍微降低不透明度，让绚丽的背景透出来 */
        width: 840px;
        margin: 0 auto;
        border-radius: 20px;
        padding: 35px 45px 50px 45px;
        box-shadow: 0 20px 50px rgba(255, 193, 7, 0.25), inset 0 0 20px rgba(255, 255, 255, 0.5);
        position: relative;
        border: 2px solid rgba(255, 243, 224, 0.8);
        backdrop-filter: blur(15px); /* 增强毛玻璃效果 */
    }

    /* Tab 切换栏 */
    .tab-header {
        display: flex;
        justify-content: center;
        margin-bottom: 35px;
        background: #fffde7;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        border-radius: 35px;
        padding: 6px;
        box-shadow: inset 0 3px 8px rgba(0,0,0,0.05), 0 2px 5px rgba(255, 255, 255, 0.5);
    }

    .tab-btn {
        padding: 12px 40px;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-light);
        cursor: pointer;
        border-radius: 30px;
        transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    }

    .tab-btn.active {
        background: linear-gradient(to bottom, #ffffff, #fff9c4);
        color: var(--theme-yellow-dark);
        box-shadow: 0 6px 15px rgba(255, 193, 7, 0.25);
        transform: translateY(-2px);
    }

    /* 模式容器 */
    .mode-container {
        display: none;
    }

    .mode-container.active {
        display: block;
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0.0, 0.2, 1);
    }

    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 文本输入模式 */
    .text-input-area {
        width: 100%;
        height: 240px;
        border: 3px solid #ffe0b2;
        border-radius: 16px;
        padding: 20px;
        font-size: 16px;
        color: var(--text-dark);
        resize: none;
        background-color: rgba(255, 253, 245, 0.8);
        outline: none;
        transition: all 0.3s;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.03);
    }

    .text-input-area:focus {
        border-color: var(--theme-yellow);
        background-color: #fff;
        box-shadow: 0 0 0 4px rgba(255, 193, 7, 0.2), inset 0 1px 3px rgba(0,0,0,0.05);
    }

    .text-input-area::placeholder {
        color: #aaa;
        font-style: italic;
    }

    .word-count {
        text-align: right;
        font-size: 14px;
        color: var(--text-light);
        margin-top: 10px;
        margin-bottom: 5px;
        font-weight: 500;
    }

    /* 文件上传模式 */
    .upload-area {
        border: 3px dashed #ffe0b2;
        border-radius: 16px;
        padding: 60px 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: rgba(255, 253, 245, 0.8);
        transition: all 0.3s;
        cursor: pointer;
        min-height: 240px;
        position: relative;
        overflow: hidden;
    }

    .upload-area:hover {
        border-color: var(--theme-yellow);
        background-color: rgba(255, 248, 225, 0.9);
        transform: scale(1.01);
    }

    .upload-area.drag-over {
        border-color: var(--highlight-color);
        box-shadow: 0 0 0 4px rgba(230, 126, 34, 0.3);
        background-color: rgba(255, 248, 225, 1);
    }

    .upload-area::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at center, rgba(255, 193, 7, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .upload-area:hover::before { opacity: 1; }

    .file-icon {
        font-size: 56px;
        color: var(--theme-yellow);
        margin-bottom: 20px;
        filter: drop-shadow(0 4px 8px rgba(255, 193, 7, 0.4));
        transition: transform 0.3s;
    }
    .upload-area:hover .file-icon {
        transform: translateY(-5px) scale(1.1);
    }

    .upload-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-dark);
        margin-bottom: 15px;
        transition: all 0.3s;
    }

    .upload-tips {
        font-size: 14px;
        color: var(--text-light);
        margin-bottom: 8px;
        line-height: 1.7;
        transition: all 0.3s;
    }

    .orange-tip {
        color: var(--highlight-color);
        font-weight: 700;
    }

    #file-input { display: none; }

    /* --- 已上传文件信息展示区 --- */
    .uploaded-file-info {
        display: none; 
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 240px;
        padding: 20px;
        border: 1px solid #eee;
        border-radius: 16px;
        background-color: #fff;
    }

    .uploaded-file-info.active {
        display: flex;
    }

    .success-icon-container {
        width: 70px;
        height: 70px;
        background-color: var(--success-bg);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }

    .success-tick {
        font-size: 32px;
        color: var(--success-green);
        line-height: 1;
    }

    .file-name-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-dark);
    }

    .small-file-icon {
        color: #4A90E2; 
        font-size: 20px;
    }

    .file-meta {
        font-size: 13px;
        color: #999;
        margin-bottom: 5px;
    }

    .file-time {
        font-size: 13px;
        color: #999;
        margin-bottom: 25px;
    }

    .reupload-btn {
        background-color: var(--danger-bg); 
        color: var(--danger-red);          
        border: none;
        padding: 8px 25px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .reupload-btn:hover {
        background-color: #ffccc7;
    }

    /* --- 按钮 --- */
    .action-btn-container {
        text-align: center;
        margin-top: 30px;
    }

    .action-btn {
        background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
        color: #fff;
        border: none;
        padding: 16px 75px;
        font-size: 20px;
        border-radius: 40px;
        cursor: pointer;
        font-weight: 800;
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
        position: relative;
        overflow: hidden;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        z-index: 1;
    }

    .action-btn:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(255, 152, 0, 0.6);
        background: linear-gradient(90deg, #ffca28 0%, #f57c00 100%);
    }

    .action-btn:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 5px 15px rgba(255, 152, 0, 0.5);
    }

    .action-btn::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -60%;
        width: 250%;
        height: 250%;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
        transform: rotate(35deg);
        animation: shine-effect 4s infinite cubic-bezier(0.4, 0.0, 0.2, 1);
        z-index: -1;
    }

    @keyframes shine-effect {
        0% { left: -60%; opacity: 0; }
        50% { opacity: 1; }
        100% { left: 120%; opacity: 0; }
    }

    .btn-badge {
        position: absolute;
        top: -14px;
        right: -18px;
        background: linear-gradient(135deg, #ff5722, #d84315);
        color: #fff;
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 800;
        box-shadow: 0 3px 8px rgba(216, 67, 21, 0.4);
        z-index: 2;
        border: 2px solid #fff;
        animation: bounce 2s infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    /* --- 底部 Logo --- */
    .partners {
        margin-top: 70px;
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        max-width: 1100px;
        margin-left: auto;
        margin-right: auto;
        padding-bottom: 50px;
    }

    .partner-logo {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 12px 25px;
        display: flex;
        align-items: center;
        font-weight: 700;
        color: var(--text-light);
        font-size: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05), inset 0 1px 3px rgba(255,255,255,0.5);
        transition: all 0.3s ease;
        cursor: default;
    }

    .partner-logo:hover {
        transform: translateY(-5px);
        background: #fff;
        box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
        color: var(--text-dark);
    }
</style>
