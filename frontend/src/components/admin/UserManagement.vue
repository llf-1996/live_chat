<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名或ID"
        :prefix-icon="Search"
        clearable
        style="width: 300px"
        @input="loadUsers"
      />
      <el-select
        v-model="filterRole"
        placeholder="角色筛选"
        clearable
        style="width: 150px; margin-left: 16px"
        @change="loadUsers"
      >
        <el-option label="全部角色" value="" />
        <el-option label="买家" value="buyer" />
        <el-option label="商户" value="merchant" />
        <el-option label="管理员" value="admin" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="状态筛选"
        clearable
        style="width: 150px; margin-left: 16px"
        @change="loadUsers"
      >
        <el-option label="全部状态" value="" />
        <el-option label="激活" value="active" />
        <el-option label="禁用" value="inactive" />
      </el-select>
    </div>

    <!-- 用户列表表格 -->
    <el-table :data="users" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="用户ID" width="120" />
      <el-table-column label="用户信息" min-width="200">
        <template #default="{ row }">
          <div style="display: flex; align-items: center;">
            <el-avatar :size="36" :src="row.avatar" style="margin-right: 12px">
              {{ row.username?.charAt(0) }}
            </el-avatar>
            <span>{{ row.username }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="getRoleTagType(row.role)" size="small">
            {{ getRoleLabel(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '激活' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="showDetailDrawer(row)">
            详情
          </el-button>
          <el-button link type="primary" size="small" @click="showEditDialog(row)">
            编辑
          </el-button>
          <el-button 
            link 
            :type="row.status === 'active' ? 'warning' : 'success'" 
            size="small"
            @click="toggleUserStatus(row)"
          >
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
          <el-button link type="danger" size="small" @click="deleteUser(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="用户ID" v-if="!isEdit">
          <el-input v-model="formData.id" placeholder="请输入用户ID（如b1, m1）" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="头像URL">
          <el-input v-model="formData.avatar" placeholder="请输入头像URL" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="formData.role" placeholder="请选择角色">
            <el-option label="买家" value="buyer" />
            <el-option label="商户" value="merchant" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述信息"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 用户详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="用户详情"
      size="50%"
    >
      <div v-if="currentUser" class="user-detail">
        <div class="detail-section">
          <div class="section-title">基本信息</div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
            <el-descriptions-item label="头像">
              <el-avatar :size="60" :src="currentUser.avatar">
                {{ currentUser.username?.charAt(0) }}
              </el-avatar>
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="getRoleTagType(currentUser.role)">
                {{ getRoleLabel(currentUser.role) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="描述">
              {{ currentUser.description || '无' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentUser.status === 'active' ? 'success' : 'danger'">
                {{ currentUser.status === 'active' ? '激活' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatTime(currentUser.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/api/chat'

const users = ref([])
const totalUsers = ref(0)
const loading = ref(false)
const searchKeyword = ref('')
const filterRole = ref('')
const filterStatus = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const formData = ref({
  id: '',
  username: '',
  avatar: '',
  role: 'buyer',
  description: '',
  status: 'active'
})

const drawerVisible = ref(false)
const currentUser = ref(null)

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  loading.value = true
  try {
    const params = {}
    if (filterRole.value) params.role = filterRole.value
    const response = await api.get('/users/', { params })
    users.value = response.results
    totalUsers.value = response.count

    // 客户端过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      users.value = users.value.filter(user =>
        user.id.toLowerCase().includes(keyword) ||
        user.username.toLowerCase().includes(keyword)
      )
    }
    if (filterStatus.value) {
      users.value = users.value.filter(user => user.status === filterStatus.value)
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  dialogTitle.value = '新增用户'
  isEdit.value = false
  formData.value = {
    id: '',
    username: '',
    avatar: '',
    role: 'buyer',
    description: '',
    status: 'active'
  }
  dialogVisible.value = true
}

function showEditDialog(user) {
  dialogTitle.value = '编辑用户'
  isEdit.value = true
  formData.value = {
    id: user.id,
    username: user.username,
    avatar: user.avatar,
    role: user.role,
    description: user.description || '',
    status: user.status
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (isEdit.value) {
      // 更新用户
      await api.put(`/users/${formData.value.id}`, {
        username: formData.value.username,
        avatar: formData.value.avatar,
        role: formData.value.role,
        description: formData.value.description,
        status: formData.value.status
      })
      ElMessage.success('更新成功')
    } else {
      // 新增用户
      await api.post('/users/', formData.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

async function toggleUserStatus(user) {
  const newStatus = user.status === 'active' ? 'inactive' : 'active'
  const action = newStatus === 'inactive' ? '禁用' : '启用'

  try {
    await ElMessageBox.confirm(
      `确定要${action}用户"${user.username}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.patch(`/api/users/${user.id}/status?status=${newStatus}`)
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

async function deleteUser(user) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${user.username}"吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await api.delete(`/users/${user.id}`)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function showDetailDrawer(user) {
  currentUser.value = user
  drawerVisible.value = true
}

function getRoleLabel(role) {
  const roleMap = {
    buyer: '买家',
    merchant: '商户',
    admin: '管理员'
  }
  return roleMap[role] || role
}

function getRoleTagType(role) {
  const typeMap = {
    buyer: 'primary',
    merchant: 'warning',
    admin: 'danger'
  }
  return typeMap[role] || 'info'
}

function formatTime(timestamp) {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-management {
  background-color: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.filter-bar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.user-detail {
  padding: 16px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}
</style>

