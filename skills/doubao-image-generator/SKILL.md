---
name: doubao-image-generator
description: "Generate images on Doubao (豆包) website and capture screenshots. Use when: user wants to generate AI images with specific prompts, needs screenshots of generated images, or wants to automate Doubao image generation workflow."
homepage: https://www.doubao.com
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins: ["browser"]
---

# 生成豆包图片 (Doubao Image Generator)

在豆包网站生成 AI 图片并截图返回。

## When to Use

✅ **使用场景：**

- 用户提供了详细的图片生成提示词
- 需要在豆包网站生成图片
- 需要截图返回生成的图片
- 需要点击特定图片（如第四张）并截图

❌ **不使用场景：**

- 浏览器工具不可用
- 豆包网站无法访问
- 用户没有提供提示词

## Workflow

### 完整流程

```
1. 打开豆包网站 (https://www.doubao.com)
2. 等待页面加载完成
3. 输入用户提供的提示词
4. 点击生成按钮
5. 等待图片生成完成
6. 点击第四张大图
7. 截图并返回给用户
```

## Commands

### 打开豆包网站

```bash
# 使用 browser 工具打开豆包
browser open https://www.doubao.com
```

### 输入提示词

```bash
# 在输入框中输入提示词
browser type --selector "textarea" --text "提示词内容"
```

### 点击生成

```bash
# 点击生成按钮
browser click --selector "button[type='submit']"
```

### 等待生成完成

```bash
# 等待图片加载
browser wait --time 30000
```

### 点击第四张图片

```bash
# 点击第四张大图
browser click --selector ".image-grid > div:nth-child(4)"
```

### 截图

```bash
# 截图当前页面
browser screenshot --full-page
```

## Example Prompts

### 人物花海场景（用户提供的完整设定）

```
人物设定：
· 服装：吊带、收腰、白色长裙。材质建议选择雪纺或丝绸，以增强飘逸感和光影通透感。
· 发型：过肩中长发，发尾微卷。发色建议为自然的棕色或黑色，发尾的卷度要柔和，体现慵懒感。
· 姿态：可站立或漫步花丛中。建议侧身或背影，增加意境；若为正面，表情应宁静、微闭双眼，感受微风。
· 环境设定：
  · 花海：种类建议选择薰衣草（紫色）、虞美人（红/橙）、小雏菊（白/黄） 或 混搭野花。注意色彩层次和景深。
  · 天空：晴朗少云，意味着光线充足。建议光线方向为侧逆光，这样能勾勒出人物的发丝和裙摆轮廓。
· 动态细节：
  · 微风：裙摆和头发的飘动方向要一致。
  · 花瓣：画面中景处要有3-5片飘落的花瓣，增加灵动感。

配色方案（方案A - 浪漫紫色调）：
· 花海：薰衣草紫、鼠尾草蓝
· 点缀：白色小雏菊
· 氛围：梦幻、治愈、优雅

构图参考：
· 三分法构图：将人物放在画面的左侧或右侧三分之一处，天空留白多一些，更有电影感和呼吸感。
```

## Optimized Prompt (English - Better Quality)

```
A young Asian woman, wearing a white spaghetti-strap cinched-waist long flowing dress made of chiffon fabric with light-transmitting quality, shoulder-length natural brown hair with soft loose curls at the ends, standing sideways in a dreamy lavender purple flower field with white daisies scattered, peaceful expression with eyes gently closed feeling the breeze, side backlighting creating rim light on hair and dress silhouette, dress and hair flowing in the same direction with the wind, 3-5 petals falling in mid-ground, clear blue sky with soft white clouds, shallow depth of field, romantic purple color palette, cinematic composition, ethereal and elegant atmosphere, 9:16 aspect ratio, photorealistic, soft natural lighting
```

## Error Handling

### 浏览器工具不可用

```
错误：timed out. Restart the OpenClaw gateway
解决：执行 openclaw gateway restart 重启网关
```

### 豆包网站加载失败

```
错误：无法访问 www.doubao.com
解决：检查网络连接，或尝试使用 VPN
```

### 图片生成超时

```
错误：等待图片生成超时
解决：增加等待时间，或检查网络状况
```

## Notes

- 豆包网站可能需要登录，建议提前准备好账号
- 图片生成时间通常为 10-30 秒
- 截图可能需要处理飞书的图片发送限制
- 如果无法直接发送图片，可以提供图片下载链接

## Related

- 豆包官网: https://www.doubao.com
- 浏览器工具: agent-browser skill
- 图像生成技能: ai-image-generation skill
