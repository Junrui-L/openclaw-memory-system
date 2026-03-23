# 第七章：标题与元标签

## 7.1 标题标签 (Title Tag)

### 标题标签重要性

```
标题标签的作用:
├── 搜索结果中显示为蓝色链接
├── 浏览器标签页显示
├── 社交分享时默认标题
└── 重要的排名因素

显示位置:
┌─────────────────────────────────────────┐
│ Google 搜索结果                         │
│                                         │
│ SEO 写作完全指南: 10 个技巧提升排名     │ ← 标题标签 │
│ https://example.com/seo-guide           │
│ 学习 SEO 写作技巧，提升文章搜索排名...  │
│                                         │
└─────────────────────────────────────────┘
```

### 标题标签公式

```
公式1: 主关键词 + 分隔符 + 价值承诺
├── "SEO 写作指南 | 提升排名的 10 个技巧"
├── "关键词研究方法 - 2024 完整教程"
└── "搜索意图分析: SEO 成功的关键"

公式2: 数字 + 主关键词 + 利益点
├── "10 个 SEO 写作技巧，让你的文章排名飙升"
├── "5 步学会关键词研究，新手也能上手"
└── "7 种内容类型，满足所有搜索意图"

公式3: 问题 + 解决方案
├── "为什么文章不排名? SEO 结构优化指南"
├── "如何写出高排名文章? 10 个实用技巧"
└── "SEO 新手必看: 文章结构优化全攻略"
```

### 标题标签最佳实践

```
长度: 50-60 字符 (最多 70)
├── 太短: 浪费空间
├── 太长: 被截断
└── 示例: "SEO 写作完全指南: 10 个技巧提升排名" (28字符)

结构: 主关键词前置
├── 好: "SEO 写作 | 完整指南"
├── 差: "完整指南 | SEO 写作"

独特性: 每个页面唯一
├── 避免重复标题
├── 反映页面内容

吸引力: 提高点击率
├── 使用数字
├── 使用强力词
├── 制造好奇
```

---

## 7.2 元描述 (Meta Description)

### 元描述作用

```
功能:
├── 搜索结果中显示为页面摘要
├── 影响点击率 (CTR)
├── 不直接影响排名，但间接影响

显示位置:
┌─────────────────────────────────────────┐
│ Google 搜索结果                         │
│                                         │
│ SEO 写作完全指南...                     │
│ https://example.com/seo-guide           │
│ 学习 SEO 写作技巧，提升文章搜索排名。   │ ← 元描述  │
│ 包含 10 个实用技巧，适合新手入门...     │
│                                         │
└─────────────────────────────────────────┘
```

### 元描述公式

```
公式: 问题/痛点 + 解决方案 + CTA

示例1:
" struggling with low search rankings? 
Learn 10 proven SEO writing techniques 
to boost your content visibility. 
Start optimizing today!"

示例2:
"想提升文章搜索排名？
这份 SEO 写作指南分享 10 个经过验证的技巧，
帮助你创作高排名内容。
立即阅读，开始优化！"

关键元素:
├── 包含主关键词 (Google 会加粗显示)
├── 长度 150-160 字符
├── 明确的 CTA
├── 独特的卖点
└── 匹配搜索意图
```

---

## 7.3 其他元标签

### Open Graph 标签 (社交分享)

```html
<!-- Facebook/Open Graph -->
<meta property="og:title" content="SEO 写作完全指南">
<meta property="og:description" content="学习 10 个 SEO 写作技巧...">
<meta property="og:image" content="https://example.com/image.jpg">
<meta property="og:url" content="https://example.com/seo-guide">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="SEO 写作完全指南">
<meta name="twitter:description" content="学习 10 个 SEO 写作技巧...">
<meta name="twitter:image" content="https://example.com/image.jpg">
```

### 结构化数据 (Schema Markup)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "SEO 写作完全指南",
  "description": "学习 10 个 SEO 写作技巧...",
  "author": {
    "@type": "Person",
    "name": "作者名"
  },
  "datePublished": "2024-03-21",
  "image": "https://example.com/image.jpg"
}
```

---

## 7.4 标题与元标签检查清单

```
□ 标题长度 50-60 字符
□ 标题包含主关键词
□ 标题独特且有吸引力
□ 元描述长度 150-160 字符
□ 元描述包含主关键词
□ 元描述有明确的 CTA
□ Open Graph 标签完整
□ 结构化数据正确
□ 社交分享预览正常
```

---

## 下一步

继续学习 [第八章：内容质量与用户体验](./08-content-quality.md)
