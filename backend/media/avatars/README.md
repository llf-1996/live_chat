# 默认头像目录

此目录包含系统默认头像图片。

## 头像列表

| 文件名 | 用途 | 说明 |
|--------|------|------|
| `admin.png` | 管理员 | 蓝色背景 + "管" 字 |
| `service.png` | 客服 | 绿色背景 + "客" 字 |
| `merchant1.png` | 商户1 | 红色背景 + "商" 字 |
| `merchant2.png` | 商户2 | 橙色背景 + "店" 字 |
| `buyer1.png` | 买家1 | 蓝色背景 + "买" 字 |
| `buyer2.png` | 买家2 | 青色背景 + "用" 字 |
| `user1.png` | 通用用户 | 紫色背景 + "A" |
| `user2.png` | 通用用户 | 绿色背景 + "B" |
| `user3.png` | 通用用户 | 黄色背景 + "C" |
| `user4.png` | 通用用户 | 天蓝色背景 + "D" |

## 重新生成头像

如果需要重新生成这些默认头像，请运行：

```bash
cd backend
python generate_avatars.py
```

## 使用方法

在代码中使用相对路径引用：

```python
# 后端 API 返回
avatar_url = "/api/media/avatars/admin.png"
```

```javascript
// 前端使用
<img :src="user.avatar || '/api/media/avatars/admin.png'" />
```

## 注意事项

- 所有头像尺寸为 200x200 像素
- 格式为 PNG，支持透明背景（圆形）
- 文件大小约 10-20 KB

