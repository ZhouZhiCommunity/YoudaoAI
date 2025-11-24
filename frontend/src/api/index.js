import axios from 'axios'

const API_BASE = 'http://localhost:5000'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 文本改写API
export const rewriteText = async (text, temperature = 0.5, useKnowledgeBase = true) => {
  const response = await api.post('/api/rewrite', {
    text,
    temperature,
    use_knowledge_base: useKnowledgeBase
  })
  return response.data
}

// 文件改写API
export const rewriteFile = async (file, temperature = 0.5, useKnowledgeBase = true) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('temperature', String(temperature))
  formData.append('use_knowledge_base', String(useKnowledgeBase))
  
  const response = await axios.post(`${API_BASE}/api/rewrite-file`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 300000
  })
  return response.data
}

// 健康检查API
export const healthCheck = async () => {
  const response = await api.get('/api/health')
  return response.data
}

export default api
