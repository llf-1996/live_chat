# 界面截图说明

本目录存放项目的界面截图，用于 README.md 展示。

## 📋 需要的截图

### 1. 管理员登录 (login.png)
- **页面**：http://localhost:5173/login
- **尺寸建议**：1600×900 或 1920×1080
- **要点**：
  - 展示优化后的蓝色渐变背景
  - 显示聊天图标 Logo
  - 展示现代化的登录表单

### 2. 桌面端聊天界面 (chat-desktop.png)
- **页面**：http://localhost:5173/chat?user_id=b1&target=m1
- **尺寸建议**：1600×900 或 1920×1080
- **要点**：
  - 三栏布局：会话列表 + 聊天窗口 + 更多面板
  - 显示在线状态（绿点）
  - 显示消息气泡
  - 展示快捷消息或历史订单

### 3. 移动端会话列表 (chat-mobile-list.png)
- **页面**：http://localhost:5173/chat?user_id=b1（手机模式）
- **尺寸建议**：375×812 或 390×844（iPhone 尺寸）
- **要点**：
  - 单栏布局显示会话列表
  - 底部导航栏（会话、聊天）
  - 显示未读消息红点
  - 显示在线状态

### 4. 移动端聊天窗口 (chat-mobile-chat.png)
- **页面**：http://localhost:5173/chat?user_id=b1&target=m1（手机模式）
- **尺寸建议**：375×812 或 390×844
- **要点**：
  - 聊天消息界面
  - 顶部显示对方信息和在线状态
  - 消息气泡
  - 底部输入框和工具栏
  - 展示"更多"按钮

### 5. 移动端更多菜单 (chat-mobile-more.png)
- **页面**：http://localhost:5173/chat?user_id=m1（点击更多按钮）
- **尺寸建议**：375×812 或 390×844
- **要点**：
  - 半屏弹窗（从底部向上）
  - 显示快捷消息列表
  - 显示商家信息（如果是商户角色）

### 6. 客服后台管理 (admin-dashboard.png)
- **页面**：http://localhost:5173/admin?user_id=a1
- **尺寸建议**：1600×900 或 1920×1080
- **要点**：
  - 左侧导航菜单
  - 实时监控界面
  - 会话列表
  - 消息管理
  - 用户管理

## 🎨 截图规范

### 准备工作
1. 确保后端服务运行正常
2. 创建测试数据（用户、会话、消息）
3. 浏览器开发者工具设置移动端视口

### 截图工具推荐
- **Windows**：Snipping Tool / ShareX
- **macOS**：Command + Shift + 4
- **浏览器**：F12 开发者工具 → 设备模拟器 → 截图

### 质量要求
- **格式**：PNG（推荐）或 JPG
- **分辨率**：高清，至少 1x
- **内容**：真实数据，避免空白状态
- **隐私**：不包含敏感信息

### 文件命名
严格按照上面的文件名命名：
- `login.png`
- `chat-desktop.png`
- `chat-mobile-list.png`
- `chat-mobile-chat.png`
- `chat-mobile-more.png`
- `admin-dashboard.png`

## 📝 注意事项

1. **移动端截图**：
   - 在浏览器中按 F12 打开开发者工具
   - 点击设备模拟器图标（或按 Ctrl+Shift+M）
   - 选择设备：iPhone 12 Pro / iPhone 13 Pro
   - 刷新页面确保响应式生效
   - 截图保存

2. **桌面端截图**：
   - 使用完整屏幕截图或浏览器窗口截图
   - 确保窗口足够大（至少 1400px 宽度）

3. **内容要求**：
   - 至少包含 3-5 条消息
   - 展示不同类型消息（文字、图片）
   - 显示在线/离线状态
   - 显示未读消息提示

4. **美观度**：
   - 截图整洁，无杂乱元素
   - 色彩自然，不过曝或过暗
   - 布局完整，不被截断

## 🚀 快速开始

```bash
# 1. 启动后端服务
cd backend && python main.py

# 2. 启动前端服务
cd frontend && pnpm dev

# 3. 创建测试数据（如果没有）
# 打开 http://localhost:5173/chat?user_id=b1&target=m1
# 发送几条测试消息

# 4. 开始截图
```

## 📖 参考示例

如需参考其他项目的截图风格：
- [Chatwoot](https://github.com/chatwoot/chatwoot)
- [Rocket.Chat](https://github.com/RocketChat/Rocket.Chat)
- [Zulip](https://github.com/zulip/zulip)

