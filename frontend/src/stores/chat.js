import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  // 从 URL 参数获取用户ID和目标用户ID
  const urlParams = new URLSearchParams(window.location.search)
  const userIdParam = urlParams.get('user_id')
  const userId = ref(userIdParam || null)  // 当前用户ID（必填，无默认值）- 字符串类型
  const targetUserId = urlParams.get('target') || null  // 目标用户ID（非必填）- 字符串类型
  
  // 状态
  const currentUser = ref({
    id: userId.value,
    username: userId.value ? '加载中...' : '',
    role: 'buyer',
    description: ''
  })

  const merchants = ref([])
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const quickReplies = ref([])
  const ws = ref(null)
  const isConnected = ref(false)
  
  // 在线用户状态
  const onlineUsers = ref(new Set())  // 在线用户ID集合
  
  // 消息分页状态
  const currentPage = ref(1)           // 当前页码
  const pageSize = ref(50)             // 每页条数
  const totalMessages = ref(0)         // 消息总数
  const isLoadingMessages = ref(false) // 加载中状态
  
  // 计算属性：是否还有更多消息
  const hasMoreMessages = computed(() => messages.value.length < totalMessages.value)

  // 计算属性
  const totalUnreadCount = computed(() => {
    // 根据角色返回对应的未读数总和
    if (currentUser.value.role === 'buyer') {
      return conversations.value.reduce((sum, conv) => sum + (conv.customer_unread_count || 0), 0)
    } else {
      return conversations.value.reduce((sum, conv) => sum + (conv.merchant_unread_count || 0), 0)
    }
  })

  // 方法
  async function loadCurrentUser() {
    if (!userId.value) {
      console.warn('访问受限：缺少用户ID')
      return
    }
    
    try {
      const user = await api.getUser(userId.value)
      currentUser.value = {
        id: user.id,
        username: user.username,
        avatar: user.avatar,
        role: user.role,
        description: user.description || ''
      }
      console.log('当前用户:', currentUser.value)
    } catch (error) {
      console.error('加载用户信息失败:', error)
      // 如果用户不存在或验证失败，清空 userId，触发访问受限提示
      if (error.response && error.response.status === 404) {
        console.warn('访问受限：用户不存在（ID: ' + userId.value + '）')
      } else {
        console.warn('访问受限：无法验证用户身份')
      }
      // 清空 userId，让页面显示访问受限
      userId.value = null
      currentUser.value = {
        id: null,
        username: '',
        role: '',
        description: ''
      }
    }
  }

  async function loadMerchants() {
    try {
      merchants.value = await api.getMerchants()
    } catch (error) {
      console.error('加载商户失败:', error)
    }
  }

  async function loadConversations() {
    if (!userId.value) {
      return
    }
    
    try {
      const params = {}
      
      // 根据角色加载不同的会话
      if (currentUser.value.role === 'buyer') {
        // 买家：加载自己的会话
        params.customer_id = currentUser.value.id
      } else if (currentUser.value.role === 'merchant') {
        // 商家：加载该商家的所有会话
        params.merchant_id = currentUser.value.id
      }
      // 管理员：加载所有会话（不传参数）
      
      const response = await api.getConversations(params)
      conversations.value = response.results || []
    } catch (error) {
      console.error('加载会话失败:', error)
    }
  }

  async function selectConversation(conversation) {
    currentConversation.value = conversation
    currentPage.value = 1 // 重置页码
    totalMessages.value = 0 // 重置总数
    
    // 先加载消息
    await loadMessages(conversation.id, 1)
    
    // 管理员查看会话时不标记为已读（只读监控）
    if (currentUser.value?.role !== 'admin') {
      // 立即标记为已读（会更新数据库和本地状态）
      await markAsRead(conversation.id)
    }
    
    // 不需要重新加载会话列表，因为 markAsRead 已经更新了本地的未读计数
  }

  async function loadMessages(conversationId, page = 1) {
    if (isLoadingMessages.value) return
    
    try {
      isLoadingMessages.value = true
      const response = await api.getMessages(conversationId, { 
        page, 
        page_size: pageSize.value,
        order: 'desc' // 降序获取（最新在前）
      })
      
      totalMessages.value = response.count
      
      if (page === 1) {
        // 首次加载，直接设置并反转
        messages.value = response.results.reverse()
        currentPage.value = 1
      } else {
        // 加载更多，在头部插入旧消息
        const oldMessages = response.results.reverse()
        messages.value = [...oldMessages, ...messages.value]
        currentPage.value = page
      }
    } catch (error) {
      console.error('加载消息失败:', error)
    } finally {
      isLoadingMessages.value = false
    }
  }
  
  async function loadMoreMessages() {
    if (!currentConversation.value || !hasMoreMessages.value || isLoadingMessages.value) {
      return
    }
    
    const nextPage = currentPage.value + 1
    await loadMessages(currentConversation.value.id, nextPage)
  }

  async function sendMessage(content, messageType = 'text') {
    if (!currentConversation.value) return

    try {
      const messageData = {
        conversation_id: currentConversation.value.id,
        sender_id: currentUser.value.id,
        content,
        message_type: messageType
      }

      const newMessage = await api.sendMessage(messageData)
      messages.value.push(newMessage)

      // 通过WebSocket发送
      if (ws.value && isConnected.value) {
        ws.value.send(JSON.stringify({
          type: 'message',
          conversation_id: currentConversation.value.id,
          sender_id: currentUser.value.id,
          content,
          message_type: messageType
        }))
      }

      // 更新会话列表
      await loadConversations()
    } catch (error) {
      console.error('发送消息失败:', error)
    }
  }

  async function markAsRead(conversationId) {
    try {
      // ✅ 先立即更新本地状态（UI 即时响应，避免等待网络请求）
      messages.value.forEach(msg => {
        if (msg.sender_id !== currentUser.value.id) {
          msg.is_read = true  // Vue 3 Proxy 响应式，直接修改即可
        }
      })
      
      // ✅ 立即更新本地会话列表的未读计数
      const conv = conversations.value.find(c => c.id === conversationId)
      if (conv) {
        // 根据角色清零对应的未读数
        if (currentUser.value.role === 'buyer') {
          conv.customer_unread_count = 0
        } else {
          conv.merchant_unread_count = 0
        }
      }
      
      // 然后异步更新后端数据库（不阻塞 UI）
      await api.markAllMessagesAsRead(conversationId, currentUser.value.id)
      await api.markConversationAsRead(conversationId, currentUser.value.id)
      
      console.log('✓ 消息已标记为已读，会话未读数已清零')
    } catch (error) {
      console.error('标记已读失败:', error)
      // 如果后端更新失败，可以考虑回滚本地状态（可选）
    }
  }

  async function createConversation(merchantId) {
    try {
      const conversation = await api.createConversation({
        customer_id: currentUser.value.id,
        merchant_id: merchantId
      })
      await loadConversations()
      await selectConversation(conversation)
    } catch (error) {
      console.error('创建会话失败:', error)
    }
  }

  async function openConversationWithUser(targetId) {
    try {
      console.log(`尝试打开与用户${targetId}的会话`)
      
      // 根据当前用户角色，确定会话的customer_id和merchant_id
      let conversationData
      if (currentUser.value.role === 'buyer') {
        // 买家：target是merchant_id
        conversationData = {
          customer_id: currentUser.value.id,
          merchant_id: targetId
        }
      } else if (currentUser.value.role === 'merchant') {
        // 商家：target是customer_id
        conversationData = {
          customer_id: targetId,
          merchant_id: currentUser.value.id
        }
      } else {
        // 管理员：暂不支持自动打开
        console.log('管理员角色暂不支持自动打开对话')
        return
      }
      
      // 创建或获取会话
      console.log('正在创建/获取会话...', conversationData)
      const conversation = await api.createConversation(conversationData)
      console.log('会话创建/获取成功:', conversation)
      
      // 重新加载会话列表（确保新创建的会话出现在列表中）
      await loadConversations()
      console.log('会话列表已重新加载，当前会话数:', conversations.value.length)
      
      // 从重新加载的会话列表中找到对应的会话
      // 这样确保使用的是列表中的对象，避免引用不一致的问题
      const foundConversation = conversations.value.find(c => c.id === conversation.id)
      if (foundConversation) {
        console.log('从会话列表中找到目标会话，准备选中')
        await selectConversation(foundConversation)
      } else {
        console.warn('未在会话列表中找到目标会话，使用API返回的对象')
        await selectConversation(conversation)
      }
      
      console.log('已成功打开会话:', conversation.id)
    } catch (error) {
      console.error('打开会话失败:', error)
      throw error  // 抛出错误以便上层处理
    }
  }

  async function loadQuickReplies(merchantId) {
    try {
      quickReplies.value = await api.getQuickReplies(merchantId)
    } catch (error) {
      console.error('加载快捷回复失败:', error)
    }
  }

  function connectWebSocket() {
    // 从环境变量获取 WebSocket 地址
    const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    const wsUrl = `${wsBaseUrl}/ws/${currentUser.value.id}`
    
    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      console.log('WebSocket 连接成功')
      isConnected.value = true
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }

    ws.value.onclose = () => {
      console.log('WebSocket 连接关闭')
      isConnected.value = false
      // 5秒后重连
      setTimeout(connectWebSocket, 5000)
    }
  }

  async function handleWebSocketMessage(data) {
    switch (data.type) {
      case 'online_users':
        // 连接时收到当前所有在线用户列表
        if (data.users && Array.isArray(data.users)) {
          data.users.forEach(userId => {
            onlineUsers.value.add(userId)
          })
          // 触发响应式更新
          onlineUsers.value = new Set(onlineUsers.value)
          console.log('✓ 收到在线用户列表:', data.users)
        }
        break

      case 'message':
        // 接收到新消息
        const isCurrentConversation = currentConversation.value && data.conversation_id === currentConversation.value.id
        const isSentByOthers = data.sender_id !== currentUser.value.id
        
        if (isCurrentConversation) {
          // ✅ 管理员查看会话时不标记为已读（只读监控）
          // 买家/商户查看会话时，收到别人的消息，直接标记为已读
          const isAdmin = currentUser.value?.role === 'admin'
          const shouldMarkAsRead = isSentByOthers && !isAdmin
          
          // 添加消息到当前会话
          messages.value.push({
            id: Date.now(),
            conversation_id: data.conversation_id,
            sender_id: data.sender_id,
            content: data.content,
            message_type: data.message_type,
            created_at: data.timestamp,
            is_read: shouldMarkAsRead // 如果正在查看且是别人发的且不是管理员，标记为已读
          })
          
          // 如果需要标记为已读，先调用 API 更新数据库，再更新会话列表
          if (shouldMarkAsRead) {
            // 等待标记已读完成（会同步更新本地会话列表的未读数）
            await markAsRead(data.conversation_id).catch(err => {
              console.error('标记已读失败:', err)
            })
          }
          
          // 更新会话列表（更新最后一条消息和时间）
          // 如果已标记为已读，此时会话的未读数应该是0
          await loadConversations()
        } else {
          // 不是当前会话，只需更新会话列表
          await loadConversations()
        }
        break

      case 'read':
        // 收到已读通知：对方已查看消息
        if (currentConversation.value && data.conversation_id === currentConversation.value.id) {
          // 将当前会话中自己发送的所有消息标记为已读
          messages.value.forEach(msg => {
            if (msg.sender_id === currentUser.value.id) {
              msg.is_read = true  // Vue 3 Proxy 响应式，直接修改
            }
          })
          console.log('✓ 对方已查看消息')
        }
        break

      case 'unread':
        // 更新未读消息数（当前通过重新加载会话列表来更新，此处保留以防将来使用）
        // const conv = conversations.value.find(c => c.id === data.conversation_id)
        // if (conv) {
        //   根据角色更新对应的未读数
        // }
        break

      case 'status':
        // 用户在线状态更新
        console.log('用户状态更新:', data)
        if (data.status === 'online') {
          onlineUsers.value.add(data.user_id)
          console.log(`✓ 用户 ${data.user_id} 上线`)
        } else if (data.status === 'offline') {
          onlineUsers.value.delete(data.user_id)
          console.log(`✓ 用户 ${data.user_id} 离线`)
        }
        // 触发响应式更新
        onlineUsers.value = new Set(onlineUsers.value)
        break
    }
  }

  function disconnectWebSocket() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      isConnected.value = false
    }
  }

  // 检查用户是否在线
  function isUserOnline(userId) {
    return onlineUsers.value.has(userId)
  }

  return {
    userId,  // 导出用户ID（用于检查是否存在）
    currentUser,
    merchants,
    conversations,
    currentConversation,
    messages,
    quickReplies,
    isConnected,
    onlineUsers,  // 在线用户集合
    isUserOnline,  // 检查用户是否在线
    totalUnreadCount,
    targetUserId,  // 导出目标用户ID
    loadCurrentUser,  // 导出加载当前用户方法
    loadMerchants,
    loadConversations,
    selectConversation,
    loadMessages,
    sendMessage,
    markAsRead,
    createConversation,
    openConversationWithUser,  // 导出自动打开对话方法
    loadQuickReplies,
    connectWebSocket,
    disconnectWebSocket,
    // 消息分页相关
    loadMoreMessages,
    hasMoreMessages,
    isLoadingMessages
  }
})
