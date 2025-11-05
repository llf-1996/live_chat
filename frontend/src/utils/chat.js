import axios from 'axios'

const CHAT_BASE_URL = 'https://chat.yaokongxiao.com'

const api = axios.create({
  timeout: 10000
})

// 请求拦截器 - 自动添加 Token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
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
  ensureUsers(users) {
    return api.post('/api/users/ensure', { users })
  }
})

/**
 * 打开聊天页面
 * @param {Array} usersToCreate - 需要创建的用户列表
 * @param {string} user_id - 当前用户ID
 * @param {string} target_user_id - 聊天对象ID
 * @returns {Promise<string>} - 聊天页面URL
 */
export async function openChatPage(usersToCreate, user_id, target_user_id) {
  /*
  usersToCreate:
    [
      {
        id: 'b1',
        role: 'buyer',
        username: '',
        avatar: '',
        description: ''
      },
      {
        id: 'm2',
        role: 'merchant',
        username: '',
        avatar: '',
        description: ''
      }
    ]
  */
  if (!user_id) {
    return Promise.reject(new Error('用户ID不能为空'))
  }
  if (!(Array.isArray(usersToCreate) && usersToCreate.length > 0)) {
    return Promise.reject(new Error('用户信息不能为空'))
  }
  // 调用接口创建用户
  const createdUsers = await api.ensureUsers(usersToCreate)
  console.log('用户创建成功:', createdUsers)
  
  // 验证跳转所需的用户是否都创建成功
  const userIds = createdUsers.map(u => u.id)
  if (!userIds.includes(user_id)) {
    return Promise.reject(new Error(`用户初始化失败，请重试`))
  }
  if (!userIds.includes(target_user_id)) {
    return Promise.reject(new Error(`聊天初始化失败，请重试`))
  }
  // 构造完整的 URL
  let chatUrl = `${CHAT_BASE_URL}/chat?user_id=${user_id}`
  if (target_user_id) {
    chatUrl += `&target_user_id=${target_user_id}`
  }
  return Promise.resolve(chatUrl)
}

