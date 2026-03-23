# 第二章：Widget Editor 界面详解

## 2.1 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  Widget Title: [________]  Type: [Latest values ▼]          │
│  [Run] [Undo] [Save] [Save as...]                          │
├───────────────────┬─────────────────────────────────────────┤
│                   │                                         │
│  📦 RESOURCES     │    📜 JAVASCRIPT                        │
│  ├─ Resources     │                                         │
│  │  (外部JS/CSS)  │    self.onInit = function() {           │
│  ├─ HTML          │        // 初始化代码                    │
│  │  (HTML模板)    │    }                                    │
│  └─ CSS           │                                         │
│    (样式定义)      │    self.onDataUpdated = function() {    │
│                   │        // 数据更新处理                  │
│  ⚙️ SETTINGS      │    }                                    │
│  ├─ Settings      │                                         │
│  │  schema        │    self.onResize = function() {         │
│  ├─ Data key      │        // 尺寸变化处理                  │
│  │  settings      │    }                                    │
│  └─ Latest data   │                                         │
│    key settings   │    self.onDestroy = function() {        │
│                   │        // 清理资源                      │
│                   │    }                                    │
│                   │                                         │
├───────────────────┴─────────────────────────────────────────┤
│  👁️ WIDGET PREVIEW (实时预览区域)                          │
│  [可以调试，查看效果]                                        │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 Toolbar（工具栏）

| 按钮 | 功能 |
|------|------|
| **Widget Title** | 设置 Widget 定义标题 |
| **Widget Type** | 选择 Widget 类型（5种类型） |
| **Run** | 运行 Widget 代码，在 Preview 区域查看结果 |
| **Undo** | 撤销所有更改，恢复到最新保存状态 |
| **Save** | 保存 Widget 定义 |
| **Save as** | 另存为新 Widget，可指定新名称和目标 Bundle |

## 2.3 Resources/HTML/CSS 区域

包含三个标签页：

### Resources 标签
- 指定 Widget 使用的外部 JavaScript/CSS 资源
- 可以添加 CDN 链接或本地资源
- 示例：
  ```
  https://bernii.github.io/gauge.js/dist/gauge.min.js
  https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js
  ```

### HTML 标签
- 包含 Widget 的 HTML 代码
- 注意：有些 Widget 动态创建 HTML，初始内容可以为空
- 使用 `ctx.$container` 作为容器上下文

### CSS 标签
- Widget 特定的 CSS 样式定义
- 使用 `#my-widget-id` 限定作用域

## 2.4 JavaScript 区域

包含所有 Widget 相关的 JavaScript 代码，遵循 **Widget API** 规范。

核心结构：
```javascript
// 生命周期方法
self.onInit = function() { };
self.onDataUpdated = function() { };
self.onResize = function() { };
self.onDestroy = function() { };

// Widget 行为配置
self.typeParameters = function() {
    return {
        maxDatasources: 1,
        singleEntity: true,
        // ...
    };
};
```

## 2.5 Settings Schema 区域

包含两个/三个标签页：

### Settings Schema 标签
- 指定 Widget 设置的 JSON schema
- 使用 react-schema-form builder 自动生成 UI 表单
- 生成的表单显示在 Widget 设置的 Appearance 标签（Advanced 模式）
- Settings Object 可从 Widget JavaScript 代码访问

**⚠️ 重要变更（v3.4+）**：
- 自动生成的 JSON 表单已被 **Angular components** 替代
- 创建自定义 Widget 时，需要从 Widget Settings 标签移除组件

### Data Key Settings Schema 标签
- 指定数据键设置的 JSON schema
- 生成的表单显示在 Data key 配置对话框的 Advanced 标签
- 用于为每个数据键存储特定设置

### Latest Data Key Settings Schema 标签
- 仅适用于 **Time series** Widgets
- 用于 Latest keys 的数据键配置

## 2.6 Widget Preview 区域

- 用于预览和测试 Widget 定义
- 以迷你 Dashboard 形式展示，包含一个从当前 Widget 定义实例化的 Widget
- 具有典型 ThingsBoard Dashboard 的大部分功能（有限制）
- **Function** 只能作为数据源类型用于调试

## 2.7 创建新 Widget 流程

1. 导航到 **Widget Library**
2. 打开现有 **Widgets Bundle** 或创建新 Bundle
3. 点击右上角 **"+"** 按钮
4. 点击 **"Create new widget"**
5. 选择 **Widget Type**（5种类型之一）
6. Widget Editor 打开，显示预填充的模板代码

## 2.8 重要注意事项

### v3.4+ 版本变更
```
Starting from v3.4, auto-generated advanced widget settings JSON forms 
are replaced with Angular components.

When creating new settings schemas for custom widgets, don't forget to 
remove components from Widget Settings tab.
```

### 调试数据源
在 Preview 区域：
- 只能选择 **Function** 作为数据源类型
- 用于模拟设备数据进行调试

---

## 下一步

继续学习 [第三章：Widget 生命周期与核心 API](./03-lifecycle-api.md)
