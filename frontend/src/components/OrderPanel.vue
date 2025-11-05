<template>
  <div class="order-panel-container">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="tabs">
      <el-tab-pane label="历史订单" name="orders">
        <!-- 订单列表 -->
        <div v-if="currentConversation && mockOrders.length > 0" class="orders-list">
          <div
            v-for="order in mockOrders"
            :key="order.orderNo"
            class="order-card"
          >
            <div class="order-content">
              <!-- 左侧商品图片 -->
              <el-image
                :src="order.productImage"
                fit="cover"
                class="order-product-image"
              />
              
              <!-- 右侧订单信息 -->
              <div class="order-details">
                <div class="order-row">
                  <span class="order-label">订单编号：</span>
                  <span class="order-value">{{ order.orderNo }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">下单时间：</span>
                  <span class="order-value">{{ order.orderTime }}</span>
                </div>
                <div class="order-row">
                  <span class="order-label">订单金额：</span>
                  <span class="order-price">¥ {{ order.amount }}</span>
                </div>
              </div>
            </div>
            
            <!-- 底部操作栏 -->
            <div class="order-footer">
              <span class="product-count">{{ order.productCount }} 种商品</span>
              <el-button type="warning" size="small" plain class="send-order-btn">
                发送订单
              </el-button>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无历史订单" :image-size="120" />
      </el-tab-pane>

      <el-tab-pane label="商家信息" name="merchant">
        <div v-if="currentConversation" class="merchant-detail">
          <div class="merchant-avatar-section">
            <el-avatar :size="80" :src="currentConversation.merchant?.avatar">
              {{ currentConversation.merchant?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
          </div>

          <div class="merchant-name-section">
            {{ currentConversation.merchant?.username }}
          </div>

          <div class="merchant-desc">
            {{ currentConversation.merchant?.description || '暂无描述' }}
          </div>

          <el-divider />

          <div class="merchant-stats">
            <div class="stat-item">
              <div class="stat-value">4.8</div>
              <div class="stat-label">服务评分</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">98%</div>
              <div class="stat-label">响应率</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">2分钟</div>
              <div class="stat-label">平均响应</div>
            </div>
          </div>
        </div>

        <el-empty v-else description="请选择商户查看信息" :image-size="120" />
      </el-tab-pane>

      <!-- 快捷消息（管理员不可使用，只读权限） -->
      <el-tab-pane v-if="!isAdmin" label="快捷消息" name="quickReplies">
        <!-- 操作按钮 -->
        <div class="quick-reply-header">
          <el-button 
            type="primary" 
            size="small" 
            :disabled="quickReplies.length >= 10"
            @click="showAddDialog"
          >
            新增消息
          </el-button>
          <span class="reply-count">{{ quickReplies.length }}/10</span>
        </div>

        <!-- 快捷消息列表 -->
        <div v-if="quickReplies.length > 0" class="quick-reply-list">
          <div
            v-for="reply in quickReplies"
            :key="reply.id"
            class="quick-reply-item"
          >
            <div class="reply-main" @click="useQuickReply(reply)">
              <div class="reply-content">{{ reply.content }}</div>
            </div>
            <div class="reply-actions">
              <el-button 
                link 
                type="primary" 
                size="small"
                @click.stop="showEditDialog(reply)"
              >
                编辑
              </el-button>
              <el-button 
                link 
                type="danger" 
                size="small"
                @click.stop="handleDelete(reply)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无快捷消息，点击新增按钮创建" :image-size="120" />
      </el-tab-pane>
    </el-tabs>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" label-width="80px">
        <el-form-item label="消息内容">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="6"
            placeholder="请输入快捷消息内容"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/chat'

const emit = defineEmits(['use-quick-reply'])

const chatStore = useChatStore()
const activeTab = ref('orders')

const currentConversation = computed(() => chatStore.currentConversation)
const quickReplies = computed(() => chatStore.quickReplies)

// 检查当前用户是否是管理员（只读权限）
const isAdmin = computed(() => chatStore.currentUser.role === 'admin')

// 本地占位符图片（SVG data URI）
const placeholderImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="80"%3E%3Crect width="80" height="80" fill="%23e2e8f0"/%3E%3Ctext x="50%25" y="50%25" font-size="14" fill="%2394a3b8" text-anchor="middle" dy=".3em"%3E商品%3C/text%3E%3C/svg%3E'

// 模拟订单数据列表
const mockOrders = ref([
  {
    orderNo: '2125071660152772',
    orderTime: '2025-07-16 10:02:34',
    amount: '299.97',
    productCount: 1,
    productImage: placeholderImage
  },
  {
    orderNo: '2125071263448015',
    orderTime: '2025-07-12 18:19:31',
    amount: '138.27',
    productCount: 1,
    productImage: placeholderImage
  }
])

// 快捷消息管理
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingReply = ref(null)
const formData = ref({
  content: ''
})

function useQuickReply(reply) {
  emit('use-quick-reply', reply.content)
}

function showAddDialog() {
  if (quickReplies.value.length >= 10) {
    ElMessage.warning('最多只能创建10条快捷消息')
    return
  }
  
  dialogTitle.value = '新增快捷消息'
  editingReply.value = null
  formData.value = {
    content: ''
  }
  dialogVisible.value = true
}

function showEditDialog(reply) {
  dialogTitle.value = '编辑快捷消息'
  editingReply.value = reply
  formData.value = {
    content: reply.content
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formData.value.content) {
    ElMessage.warning('请填写消息内容')
    return
  }

  try {
    if (editingReply.value) {
      // 编辑
      await api.updateQuickReply(editingReply.value.id, formData.value)
      ElMessage.success('更新成功')
    } else {
      // 新增
      await api.createQuickReply({
        ...formData.value,
        user_id: chatStore.currentUser.id,
        sort_order: quickReplies.value.length
      })
      ElMessage.success('新增成功')
    }
    
    // 重新加载快捷消息
    await chatStore.loadQuickReplies(chatStore.currentUser.id)
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(reply) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条快捷消息吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.deleteQuickReply(reply.id)
    ElMessage.success('删除成功')
    
    // 重新加载快捷消息
    await chatStore.loadQuickReplies(chatStore.currentUser.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.order-panel-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
}

.tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 订单列表容器 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 订单卡片 */
.order-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background-color: #ffffff;
  transition: all 0.2s;
}

.order-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-color: #ff9900;
}

/* 订单内容区域 */
.order-content {
  display: flex;
  gap: 12px;
  padding: 12px;
}

/* 订单商品图片 */
.order-product-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid #e4e7ed;
}

/* 订单详情 */
.order-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: space-around;
}

/* 订单信息行 */
.order-row {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.order-label {
  color: #909399;
  white-space: nowrap;
  min-width: 70px;
}

.order-value {
  color: #303133;
  word-break: break-all;
}

.order-price {
  color: #ff6600;
  font-weight: 600;
  font-size: 15px;
}

/* 订单底部操作区 */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background-color: #f9f9f9;
  border-top: 1px solid #e4e7ed;
}

.product-count {
  font-size: 13px;
  color: #606266;
}

.send-order-btn {
  font-size: 13px;
  border-color: #ff9900;
  color: #ff9900;
}

.send-order-btn:hover {
  background-color: #ff9900;
  border-color: #ff9900;
  color: #ffffff;
}

.merchant-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.merchant-avatar-section {
  margin-bottom: 16px;
}

.merchant-name-section {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.merchant-desc {
  font-size: 14px;
  color: #909399;
  text-align: center;
  margin-bottom: 16px;
}

.merchant-stats {
  display: flex;
  gap: 24px;
  width: 100%;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

/* 快捷消息样式 */
.quick-reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  margin-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.reply-count {
  font-size: 13px;
  color: #909399;
}

.quick-reply-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-reply-item {
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  transition: all 0.2s;
}

.quick-reply-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.reply-main {
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reply-main:hover {
  background-color: #ecf5ff;
}

.reply-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  word-break: break-all;
  white-space: pre-wrap;
}

.reply-actions {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background-color: #fafafa;
  border-top: 1px solid #e4e7ed;
  justify-content: flex-end;
}

/* ==================== 响应式媒体查询 ==================== */

/* 平板端 (768px-1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .order-header {
    padding: 12px 14px;
  }
  
  .order-title {
    font-size: 15px;
  }
  
  .order-content {
    padding: 14px;
  }
  
  .merchant-name-section {
    font-size: 17px;
  }
  
  .merchant-stats {
    gap: 20px;
  }
  
  .stat-value {
    font-size: 18px;
  }
}

/* 手机端 (<768px) */
@media (max-width: 767px) {
  .order-header {
    padding: 12px 16px;
  }
  
  .order-title {
    font-size: 14px;
  }
  
  .order-content {
    padding: 16px;
  }
  
  /* 订单列表 */
  .order-item {
    padding: 12px;
  }
  
  .order-name {
    font-size: 13px;
  }
  
  .order-price {
    font-size: 13px;
  }
  
  .order-status {
    padding: 3px 8px;
    font-size: 11px;
  }
  
  .order-time {
    font-size: 11px;
  }
  
  .send-order-btn {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  /* 商家信息 */
  .merchant-name-section {
    font-size: 16px;
  }
  
  .merchant-desc {
    font-size: 13px;
  }
  
  .merchant-stats {
    gap: 16px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 11px;
  }
  
  /* 快捷消息 - 单列显示 */
  .quick-reply-list {
    gap: 10px;
  }
  
  .quick-reply-item {
    width: 100%;
  }
  
  .reply-main {
    padding: 10px;
  }
  
  .reply-content {
    font-size: 13px;
  }
  
  .reply-actions {
    padding: 6px 10px;
  }
}
</style>
