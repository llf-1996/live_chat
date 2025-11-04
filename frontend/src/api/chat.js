import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器 - 自动添加 Token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 导出API实例和便利方法
export default Object.assign(api, {
  // 用户相关
  getUsers() {
    return api.get('/users/')
  },

  getUser(userId) {
    return api.get(`/users/${userId}`)
  },

  ensureUsers(users) {
    return api.post('/users/ensure', { users })
  },

  // 商家相关（现在是User，role=merchant）
  getMerchants() {
    return api.get('/users/', { params: { role: 'merchant' } })
  },

  getMerchant(merchantId) {
    return api.get(`/users/${merchantId}`)
  },

  // 会话相关
  getConversations(params) {
    return api.get('/conversations/', { params })
  },

  getConversation(conversationId) {
    return api.get(`/conversations/${conversationId}`)
  },

  createConversation(data) {
    return api.post('/conversations/', data)
  },

  markConversationAsRead(conversationId, userId) {
    return api.put(`/conversations/${conversationId}/read`, null, {
      params: { user_id: userId }
    })
  },

  // 消息相关
  getMessages(conversationId, params = {}) {
    // 支持分页参数
    return api.get(`/conversations/${conversationId}/messages`, { 
      params: { 
        page: params.page || 1,
        page_size: params.page_size || 50,
        order: params.order || 'desc'
      }
    })
  },

  sendMessage(data) {
    return api.post('/messages/', data)
  },

  markMessageAsRead(messageId) {
    return api.put(`/messages/${messageId}/read`)
  },

  markAllMessagesAsRead(conversationId, readerId) {
    return api.put(`/conversations/${conversationId}/messages/read-all`, null, {
      params: { reader_id: readerId }
    })
  },

  // 快捷消息相关
  getQuickReplies(userId) {
    return api.get(`/quick-replies/user/${userId}`)
  },

  createQuickReply(data) {
    return api.post('/quick-replies/', data)
  },

  updateQuickReply(quickReplyId, data) {
    return api.put(`/quick-replies/${quickReplyId}`, data)
  },

  deleteQuickReply(quickReplyId) {
    return api.delete(`/quick-replies/${quickReplyId}`)
  },

  // 文件上传
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 认证相关
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },

  getCurrentUser() {
    return api.get('/auth/me')
  }
})
