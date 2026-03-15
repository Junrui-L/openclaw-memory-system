# Happy-birthDay 🎂

一个精美的、可配置的生日祝福页面，使用 HTML5 Canvas 粒子动画效果。

![效果预览](images/preview.png)

## ✨ 特性

- 🎨 **高度可配置** - 通过 `config.js` 自定义所有内容
- 📱 **响应式设计** - 完美适配手机、平板和桌面
- 🎵 **背景音乐** - 支持自动播放和手动控制
- ✨ **粒子动画** - 文字、形状、烟花等多种效果
- ⌨️ **键盘快捷键** - 空格播放/暂停音乐，方向键切换内容
- 🖱️ **交互效果** - 点击画布触发烟花
- 🎯 **倒计时** - 自动计算并显示时间差

## 🚀 快速开始

1. 克隆或下载本项目
2. 替换 `images/avatar.jpg` 为你的头像
3. 编辑 `js/config.js` 配置信息
4. 打开 `index.html` 即可查看效果

## ⚙️ 配置说明

编辑 `js/config.js` 文件：

```javascript
const CONFIG = {
    // 目标人物信息
    person: {
        name: "亲爱的",                    // 显示的名字
        birthday: "1992-09-21",           // 生日日期
        avatar: "images/avatar.jpg",      // 头像路径
    },

    // 显示文字序列
    messages: [
        "亲爱的",
        "生日快乐哟",
        "#heart",              // 爱心形状
        "#countdown 3",        // 倒计时3秒
        "#time"                // 显示当前时间
    ],

    // 主题配色
    theme: {
        backgroundType: "gradient",       // gradient 或 solid
        gradient: {
            start: "rgb(203, 235, 219)",
            end: "rgb(55, 148, 192)"
        },
        textColor: "#ed3073",
    },

    // 音效配置
    audio: {
        enabled: false,                   // 是否启用音乐
        music: "audio/birthday.mp3",      // 音乐文件路径
        autoplay: false,                  // 自动播放
    }
};
```

## 🎮 特殊指令

在 `messages` 数组中可以使用以下特殊指令：

| 指令 | 说明 | 示例 |
|------|------|------|
| `#countdown N` | 倒计时 N 秒 | `#countdown 3` |
| `#rectangle WxH` | 绘制矩形 | `#rectangle 15x15` |
| `#circle R` | 绘制圆形 | `#circle 12` |
| `#heart` | 爱心形状 | `#heart` |
| `#star` | 星星形状 | `#star` |
| `#time` | 当前时间 | `#time` |
| `#firework` | 烟花效果 | `#firework` |

## ⌨️ 快捷键

- `空格` - 播放/暂停音乐
- `←` / `→` - 切换上一条/下一条消息
- `R` - 重置动画序列

## 📱 触摸手势

- **左滑** - 下一条消息
- **右滑** - 上一条消息
- **点击画布** - 触发烟花效果

## 📂 文件结构

```
Happy-birthDay-improved/
├── index.html          # 主页面
├── css/
│   └── style.css       # 样式文件
├── js/
│   ├── config.js       # 配置文件 ⭐
│   ├── color.js        # 颜色工具
│   ├── canvas.js       # 画布管理
│   ├── particles.js    # 粒子系统
│   ├── countdown.js    # 倒计时计算
│   ├── audio.js        # 音频控制
│   └── main.js         # 主程序
├── images/
│   └── avatar.jpg      # 头像图片 ⭐
├── audio/
│   └── birthday.mp3    # 背景音乐（可选）
└── README.md           # 本文件
```

## 🌐 浏览器支持

- Chrome / Edge 90+
- Firefox 88+
- Safari 14+
- iOS Safari 14+
- Chrome Android 90+

## 📄 许可证

MIT License - 自由使用和修改

---

Made with ❤️ for special moments