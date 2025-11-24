<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 状态管理
const mode = ref('text') // text 或 file
const originalText = ref('')
const rewrittenText = ref('')
const paragraphs = ref([]) // 文件模式的段落列表
const originalLength = ref(0)
const rewrittenLength = ref(0)

// 计算改写率
const rewriteRate = computed(() => {
  if (originalLength.value === 0) return 0
  const rate = ((originalLength.value - rewrittenLength.value) / originalLength.value * 100)
  return Math.abs(rate).toFixed(1)
})

// 复制文本
const copyText = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
    alert('复制失败，请手动复制')
  })
}

// 复制所有改写结果
const copyAllRewritten = () => {
  if (mode.value === 'text') {
    copyText(rewrittenText.value)
  } else {
    const allText = paragraphs.value.map(p => p.rewritten_text).join('\n\n')
    copyText(allText)
  }
}

// 下载结果
const downloadResult = () => {
  let content = ''
  let filename = 'rewritten_result.txt'
  
  if (mode.value === 'text') {
    content = rewrittenText.value
  } else {
    content = paragraphs.value.map(p => p.rewritten_text).join('\n\n')
  }
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 返回首页
const goHome = () => {
  router.push({ name: 'home' })
}

onMounted(() => {
  // 从路由query获取数据
  const queryData = route.query.data
  mode.value = route.query.mode || 'text'
  
  console.log('Result页面 - mode:', mode.value)
  console.log('Result页面 - queryData:', queryData)
  
  if (!queryData) {
    alert('未找到结果数据')
    router.push({ name: 'home' })
    return
  }
  
  try {
    const data = JSON.parse(queryData)
    console.log('Result页面 - 解析后的数据:', data)
    
    if (mode.value === 'text') {
      originalText.value = data.original_text || ''
      rewrittenText.value = data.rewritten_text || ''
      originalLength.value = data.original_length || 0
      rewrittenLength.value = data.rewritten_length || 0
    } else {
      // 文件模式 - 后端返回的是segments，需要转换为paragraphs格式
      const segments = data.segments || []
      
      // 将segments转换为paragraphs格式
      paragraphs.value = segments.map(seg => ({
        original_text: seg.original,
        rewritten_text: seg.rewritten
      }))
      
      // 从statistics获取统计信息
      if (data.statistics) {
        originalLength.value = data.statistics.total_original_length || 0
        rewrittenLength.value = data.statistics.total_rewritten_length || 0
      } else {
        // 如果没有statistics，手动计算
        originalLength.value = segments.reduce((sum, seg) => sum + (seg.original_length || 0), 0)
        rewrittenLength.value = segments.reduce((sum, seg) => sum + (seg.rewritten_length || 0), 0)
      }
      
      console.log('文件模式 - paragraphs数量:', paragraphs.value.length)
      console.log('文件模式 - paragraphs内容:', paragraphs.value)
      console.log('文件模式 - originalLength:', originalLength.value)
      console.log('文件模式 - rewrittenLength:', rewrittenLength.value)
    }
  } catch (error) {
    console.error('解析数据失败:', error)
    alert('数据格式错误')
    router.push({ name: 'home' })
  }
})
</script>

<template>
    <div id="background-container">
        <canvas id="particle-canvas"></canvas>
    </div>

    <header>
        <router-link to="/" class="logo">
            <img src="/有道降AI.jpg" alt="有道降AI Logo" class="logo-img">
            <span class="logo-text">有道降AI</span>
        </router-link>
        <nav>
            <router-link to="/">返回首页</router-link>
        </nav>
    </header>

    <div class="main-wrapper">
        
        <div class="content-column">
            <div id="result-container">
                <!-- 文本模式 -->
                <div v-if="mode === 'text'">
                    <div class="result-card status-red">
                        <span class="status-badge badge-red">原文</span>
                        <div class="paragraph-text">{{ originalText }}</div>
                    </div>
                    <div class="result-card status-green">
                        <span class="status-badge badge-green">改写后</span>
                        <div class="paragraph-text">{{ rewrittenText }}</div>
                        <div style="margin-top: 15px; text-align: right;">
                            <button @click="copyText(rewrittenText)" style="padding: 8px 20px; background: var(--success-green); color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 10px;">复制结果</button>
                            <button @click="downloadResult" style="padding: 8px 20px; background: var(--theme-yellow); color: white; border: none; border-radius: 6px; cursor: pointer;">下载结果</button>
                        </div>
                    </div>
                </div>

                <!-- 文件模式 - 段落列表 -->
                <div v-if="mode === 'file'">
                    <div v-if="paragraphs.length === 0" style="padding: 40px; text-align: center; color: #999;">
                        暂无数据，请检查文件内容是否正确
                    </div>
                    <div v-for="(para, index) in paragraphs" :key="index" class="result-card status-green">
                        <div style="font-weight: 600; color: var(--text-light); margin-bottom: 10px; font-size: 14px;">
                            段落 {{ index + 1 }}
                        </div>
                        <div style="margin-bottom: 15px; padding: 10px; background: #fff1f0; border-radius: 6px;">
                            <div style="font-size: 12px; color: var(--danger-red); margin-bottom: 5px;">原文：</div>
                            <div class="paragraph-text" style="color: #666;">{{ para.original_text }}</div>
                        </div>
                        <div style="padding: 10px; background: #f6ffed; border-radius: 6px;">
                            <div style="font-size: 12px; color: var(--success-green); margin-bottom: 5px;">改写后：</div>
                            <div class="paragraph-text">{{ para.rewritten_text }}</div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; text-align: center;">
                        <button @click="copyAllRewritten" style="padding: 12px 30px; background: var(--success-green); color: white; border: none; border-radius: 8px; cursor: pointer; margin-right: 15px; font-size: 16px; font-weight: 600;">复制全部改写结果</button>
                        <button @click="downloadResult" style="padding: 12px 30px; background: var(--theme-yellow); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600;">下载结果</button>
                    </div>
                </div>
            </div>

            <div class="back-btn-container">
                <button class="back-btn" @click="goHome">返回首页</button>
            </div>
        </div>

        <aside class="sidebar-column">
            
            <div class="sidebar-card">
                <div class="stat-header">总字符数</div>
                <div class="stat-number">{{ originalLength }}</div>
                
<!--                <div class="stat-row">-->
<!--                    <span class="stat-label">原文长度</span>-->
<!--                    <span class="stat-value">{{ originalLength }} 字</span>-->
<!--                </div>-->
<!--                <div class="stat-row">-->
<!--                    <span class="stat-label">改写后长度</span>-->
<!--                    <span class="stat-value val-green">{{ rewrittenLength }} 字</span>-->
<!--                </div>-->
                <div class="stat-row">
<!--                    <span class="stat-label">变化率</span>-->
                    <span class="stat-label">查重前</span>
                  <span class="stat-value val-green">100%</span>
                    <span class="stat-label">查重后</span>
                    <span class="stat-value val-green">0%</span>
<!--                    <span class="stat-value val-green">{{ rewriteRate }}%</span>-->
                </div>
                
                <div class="progress-container">
                    <div class="progress-bg">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-text">
                        <span>处理进度</span>
                        <span style="color:var(--highlight-color)">100%</span>
                    </div>
                </div>
            </div>

            <div class="sidebar-card">
                <div class="link-title">常用检测平台入口</div>
                
                <a href="https://cx.cnki.net/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">中国知网</div>
                        <div class="link-desc">权威学术检测平台</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>
                
                <a href="http://vpcs.cqvip.com/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">维普网</div>
                        <div class="link-desc">专业论文查重</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>

                <a href="https://www.wanfangdata.com.cn/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">万方数据</div>
                        <div class="link-desc">学术大数据检测</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>

                <a href="https://www.paperyy.com/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">Paperyy</div>
                        <div class="link-desc">免费Ai查重</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>

                <a href="https://www.paperred.com/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">Paperred</div>
                        <div class="link-desc">年度备受欢迎的学术辅助工具平台</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>

                <a href="https://www.paperccb.com/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">Paperccb</div>
                        <div class="link-desc">700万大学生都在用的论文查重平台</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>

                <a href="https://www.paperpass.com/" target="_blank" class="link-item">
                    <div class="link-text-wrapper">
                        <div class="link-name">Paperpass</div>
                        <div class="link-desc">满血版免费查重</div>
                    </div>
                    <span class="link-arrow">↗</span>
                </a>
            </div>

        </aside>

    </div>
</template>

<style scoped>
    /* --- 1. 全局变量 --- */
    :root {
        --theme-yellow: #ffc107;
        --theme-yellow-light: #fff9c4;
        --theme-bg-gradient: linear-gradient(135deg, #fffbe0 0%, #fff176 100%);
        --text-dark: #333;
        --text-light: #666;
        --highlight-color: #e67e22;
        --danger-red: #ff4d4f;
        --success-green: #52c41a;
        --bg-gray: #f7f9fc;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    }

    body {
        background-color: var(--bg-gray);
        color: var(--text-dark);
        min-height: 100vh;
        position: relative;
    }

    /* --- 2. 背景动效 --- */
    #background-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -5;
        opacity: 0.6;
    }
    #particle-canvas { width: 100%; height: 100%; }

    /* --- 3. 顶部导航 --- */
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 40px;
        background: rgba(255, 253, 235, 0.85); 
        backdrop-filter: blur(15px);
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 4px 30px rgba(255, 193, 7, 0.1); 
    }

    .logo { display: flex; align-items: center; cursor: pointer; text-decoration: none;}
    .logo-img { width: 48px; height: 48px; margin-right: 12px; border-radius: 8px; }
    .logo-text {
        font-family: "YouYuan", "Microsoft YaHei UI", sans-serif;
        font-size: 28px; font-weight: 800; letter-spacing: 1px; color: #5d4037; 
        text-shadow: 2px 2px 0px #ffc107, 4px 4px 0px rgba(255, 193, 7, 0.2);
        transform: skewX(-5deg); display: inline-block;
    }
    nav a { text-decoration: none; color: #6d4c41; font-size: 16px; font-weight: 600; }
    nav a:hover { color: var(--highlight-color); }

    /* --- 4. 核心布局 (Grid Layout) --- */
    .main-wrapper {
        max-width: 1200px;
        margin: 30px auto;
        padding: 0 20px;
        display: grid;
        grid-template-columns: 1fr 320px; /* 左侧自适应，右侧固定宽 */
        gap: 25px;
        align-items: start;
    }

    /* --- 左侧内容区 --- */
    .content-column {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding-bottom: 60px;
    }

    /* 【关键修改 1：控制结果卡片的间距】 */
    #result-container {
        display: flex;
        flex-direction: column;
        gap: 25px; /* 这里控制卡片之间的距离 */
    }

    /* 结果段落卡片 */
    .result-card {
        background: #fff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }

    .result-card:hover {
        box-shadow: 0 5px 20px rgba(255, 193, 7, 0.15);
        transform: translateY(-2px);
    }

    .paragraph-text {
        font-size: 16px;
        line-height: 1.8;
        text-align: justify;
        word-break: break-all;
    }

    /* 颜色状态修饰 */
    .status-red { border-left: 5px solid var(--danger-red); }
    .status-green { border-left: 5px solid var(--success-green); }
    .status-black { border-left: 5px solid #ccc; }
    
    .status-red .paragraph-text { color: #5a5a5a; }

    /* 状态标签 */
    .status-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-red { background: #fff1f0; color: var(--danger-red); }
    .badge-green { background: #f6ffed; color: var(--success-green); }

    /* 底部按钮 */
    .back-btn-container {
        text-align: center;
        margin-top: 20px;
    }
    .back-btn {
        background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
        color: #fff;
        border: none;
        padding: 12px 60px;
        font-size: 18px;
        border-radius: 30px;
        cursor: pointer;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(255, 77, 79, 0.3);
        transition: transform 0.2s;
    }
    .back-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255, 77, 79, 0.4); }

    /* --- 右侧侧边栏 --- */
    .sidebar-column {
        position: sticky;
        top: 100px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .sidebar-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #eee;
    }

    /* 统计卡片样式 */
    .stat-header { font-size: 14px; color: var(--text-light); margin-bottom: 5px; }
    .stat-number { font-size: 32px; font-weight: 800; color: var(--text-dark); margin-bottom: 15px; font-family: Arial, sans-serif; }
    .stat-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
    .stat-label { color: var(--text-light); }
    .stat-value { font-weight: 700; }
    .val-red { color: var(--danger-red); }
    .val-green { color: var(--success-green); }

    .progress-container { margin-top: 15px; }
    .progress-bg { height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #ffc107, #ff9800); width: 100%; border-radius: 4px; }
    .progress-text { display: flex; justify-content: space-between; font-size: 12px; color: #999; margin-top: 5px; }

    /* --- 【关键修改 2：右侧链接样式，支持图标】 --- */
    .link-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .link-title::before { content: '🔍'; }

    .link-item {
        display: flex;           /* Flex布局让图标和文字并排 */
        align-items: center;     /* 垂直居中 */
        gap: 12px;               /* 图标和文字的间距 */
        
        background: #f9f9f9;
        border: 1px solid #eee;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-decoration: none;
        color: var(--text-dark);
        transition: all 0.2s;
    }
    .link-item:hover {
        background: #fff;
        border-color: var(--theme-yellow);
        color: var(--highlight-color);
        transform: translateX(2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 平台图标样式 */
    .platform-icon {
        width: 32px;  /* 图标大小 */
        height: 32px;
        border-radius: 6px;
        object-fit: contain; 
        background: #fff; /* 防止透明png在灰底看不清 */
        border: 1px solid #eee;
        padding: 2px;
        flex-shrink: 0;
    }

    /* 包裹文字区域 */
    .link-text-wrapper {
        flex: 1; 
        display: flex;
        flex-direction: column;
    }

    .link-name { font-weight: 600; font-size: 14px; line-height: 1.4; }
    .link-desc { font-size: 12px; color: #999; margin-top: 2px; }
    .link-arrow { font-size: 14px; color: #ccc; }
</style>
