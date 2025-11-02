"""
生成默认头像
使用 PIL/Pillow 生成彩色背景 + 文字的头像
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

# 创建头像目录（同时创建到 static/avatars 和 media/avatars）
STATIC_AVATAR_DIR = Path("static/avatars")
MEDIA_AVATAR_DIR = Path("media/avatars")

STATIC_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# 头像配置
AVATAR_SIZE = 200  # 头像尺寸
FONT_SIZE = 80     # 字体大小

# 预设颜色方案（背景色）
COLORS = [
    "#FF6B6B",  # 红色
    "#4ECDC4",  # 青色
    "#45B7D1",  # 蓝色
    "#FFA07A",  # 橙色
    "#98D8C8",  # 薄荷绿
    "#F7DC6F",  # 黄色
    "#BB8FCE",  # 紫色
    "#85C1E2",  # 天蓝色
    "#F8B739",  # 金色
    "#52B788",  # 绿色
]

# 预设头像列表
AVATARS = [
    {"filename": "admin.png", "text": "管", "color": "#4A90E2"},  # 管理员
    {"filename": "service.png", "text": "客", "color": "#50C878"},  # 客服
    {"filename": "merchant1.png", "text": "商", "color": "#FF6B6B"},  # 商户
    {"filename": "merchant2.png", "text": "店", "color": "#FFA07A"},  # 商户
    {"filename": "buyer1.png", "text": "买", "color": "#45B7D1"},  # 买家
    {"filename": "buyer2.png", "text": "用", "color": "#4ECDC4"},  # 买家
    {"filename": "user1.png", "text": "A", "color": "#BB8FCE"},  # 通用用户
    {"filename": "user2.png", "text": "B", "color": "#98D8C8"},
    {"filename": "user3.png", "text": "C", "color": "#F7DC6F"},
    {"filename": "user4.png", "text": "D", "color": "#85C1E2"},
]


def hex_to_rgb(hex_color):
    """将十六进制颜色转换为 RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_avatar(text, color, filename):
    """
    生成头像
    
    Args:
        text: 头像上显示的文字
        color: 背景颜色（十六进制）
        filename: 保存的文件名
    """
    # 创建图像
    img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), hex_to_rgb(color))
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        # Windows 系统字体
        font = ImageFont.truetype("msyh.ttc", FONT_SIZE)  # 微软雅黑
    except:
        try:
            # Linux/Mac 系统字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", FONT_SIZE)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = (
        (AVATAR_SIZE - text_width) // 2,
        (AVATAR_SIZE - text_height) // 2 - 5  # 稍微向上调整
    )
    
    # 绘制文字（白色）
    draw.text(position, text, fill=(255, 255, 255), font=font)
    
    # 添加圆角效果（可选）
    # 创建圆角遮罩
    mask = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
    
    # 创建圆形头像
    output = Image.new('RGBA', (AVATAR_SIZE, AVATAR_SIZE), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    # 保存图像（保存到两个目录）
    static_path = STATIC_AVATAR_DIR / filename
    media_path = MEDIA_AVATAR_DIR / filename
    
    output.save(static_path, 'PNG')
    output.save(media_path, 'PNG')
    
    print(f"✅ 生成头像: {static_path} 和 {media_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("生成默认头像")
    print("=" * 60)
    print()
    
    # 生成预设头像
    for avatar in AVATARS:
        generate_avatar(
            text=avatar["text"],
            color=avatar["color"],
            filename=avatar["filename"]
        )
    
    print()
    print(f"✅ 成功生成 {len(AVATARS)} 个头像")
    print(f"保存位置:")
    print(f"  - {STATIC_AVATAR_DIR.absolute()} （源文件，提交到 Git）")
    print(f"  - {MEDIA_AVATAR_DIR.absolute()} （运行时使用）")
    print()
    print("头像文件列表:")
    for avatar in AVATARS:
        print(f"  - {avatar['filename']} ({avatar['text']})")
    print()
    print("💡 提示: 部署时可以只复制 static/avatars/ 到 media/avatars/")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print()
        print("请确保已安装 Pillow 库:")
        print("  pip install Pillow")

