# ThingsBoard 自定义组件开发指南

> 文档创建时间: 2026-03-22
> 来源: ThingsBoard 官方文档
> 用途: 跌倒报警组件开发参考

---

## 📋 学习计划

### 阶段一：基础概念（已完成 ✅）
- [x] 了解 Widget 类型和分类
- [x] 理解 Widget Editor 结构
- [x] 掌握 Settings Schema 基础

### 阶段二：核心开发（进行中 🔄）
- [ ] Widget API 详解
- [ ] 数据绑定与生命周期
- [ ] 模板系统与 is 调用
- [ ] 最佳实践总结

### 阶段三：实战应用（待开始 ⏳）
- [ ] 跌倒报警组件设计
- [ ] 组件实现与测试
- [ ] 文档归档

---

## 一、Widget 基础概念

### 1.1 Widget 类型

ThingsBoard 有 **5 种核心 Widget 类型**：

| 类型 | 用途 | 数据源 | 典型场景 |
|------|------|--------|----------|
| **Latest values** | 显示最新值 | 实体属性/时序数据 | 仪表盘、数值显示 |
| **Time series** | 显示历史数据 | 时序数据 | 折线图、趋势图 |
| **Control widget** | 发送 RPC 命令 | 目标设备 | 开关控制、GPIO |
| **Alarm widget** | 显示报警信息 | 报警源 | 报警列表、报警统计 |
| **Static** | 静态 HTML | 无 | 说明文字、自定义卡片 |

### 1.2 Widget Bundle（组件包）

组件按功能分组到 **Widget Bundles**：

- **Air quality** - 空气质量
- **Alarm widgets** - 报警相关
- **Charts** - 图表
- **Control widgets** - 控制组件
- **Maps** - 地图
- **SCADA symbols** - 工业符号
- **Tables** - 表格
- ... 等 30+ 个分类

---

## 二、Widget Editor 详解

### 2.1 编辑器结构

Widget Editor 是一个迷你 IDE，包含 4 个主要区域：

```
┌─────────────────────────────────────────┐
│  Toolbar (标题、类型、运行、保存)          │
├──────────┬──────────┬───────────────────┤
│          │          │                   │
│ Resources│ JavaScript│  Settings Schema  │
│   HTML   │          │                   │
│   CSS    │          │  Widget Preview   │
│          │          │    (实时预览)      │
│          │          │                   │
└──────────┴──────────┴───────────────────┘
```

### 2.2 Toolbar 功能

| 按钮 | 功能 |
|------|------|
| **Widget Title** | 设置组件标题 |
| **Widget Type** | 选择组件类型 |
| **Run** | 运行代码，预览效果 |
| **Undo** | 恢复到上次保存状态 |
| **Save** | 保存组件定义 |
| **Save as** | 另存为新组件 |

### 2.3 Resources/HTML/CSS 区域

#### Resources Tab
引入外部资源：
```javascript
// 外部 JS/CSS 资源
https://cdn.jsdelivr.net/npm/chart.js
https://unpkg.com/leaflet@1.7.1/dist/leaflet.css
```

#### HTML Tab
组件的 HTML 结构：
```html
<div class="my-widget">
  <h3>{{title}}</h3>
  <div class="value">{{value}}</div>
</div>
```

#### CSS Tab
组件样式：
```css
.my-widget {
  padding: 10px;
  background: #f5f5f5;
}
.my-widget .value {
  font-size: 24px;
  color: #333;
}
```

---

## 三、JavaScript 核心 API

### 3.1 Widget 生命周期

```javascript
// 1. 初始化 - 组件首次加载时调用
self.onInit = function() {
  // 初始化变量、创建 DOM 元素
  console.log('Widget initialized');
};

// 2. 数据更新 - 数据变化时调用
self.onDataUpdated = function() {
  // 处理新数据，更新 UI
  var data = self.ctx.data;
  updateUI(data);
};

// 3. 调整大小 - 组件尺寸变化时调用
self.onResize = function() {
  // 重新计算布局
  var width = self.ctx.width;
  var height = self.ctx.height;
};

// 4. 编辑模式切换
self.onEditModeChanged = function(isEditMode) {
  // 进入/退出编辑模式
};

// 5. 销毁 - 组件移除时调用
self.onDestroy = function() {
  // 清理资源、取消订阅
};
```

### 3.2 核心上下文对象 (self.ctx)

```javascript
// 数据相关
self.ctx.data          // 组件数据数组
self.ctx.datasources   // 数据源配置
self.ctx.dataKeys      // 数据键配置
self.ctx.timeWindow    // 时间窗口配置

// 设置相关
self.ctx.settings      // 用户设置对象
self.ctx.widgetConfig  // 组件配置

// 实体相关
self.ctx.entityId      // 当前实体 ID
self.ctx.entityName    // 当前实体名称
self.ctx.entityLabel   // 当前实体标签

// 工具函数
self.ctx.utils         // 工具函数集
self.ctx.$scope        // Angular scope
self.ctx.$container    // jQuery 容器对象

// 尺寸
self.ctx.width         // 组件宽度
self.ctx.height        // 组件高度
```

### 3.3 数据访问 API

```javascript
// 获取最新值
self.onDataUpdated = function() {
  var data = self.ctx.data;
  
  // 遍历所有数据源
  for (var i = 0; i < data.length; i++) {
    var datasource = data[i];
    var dataKey = datasource.dataKey;
    var value = datasource.data[0];  // 最新值
    
    console.log('Key:', dataKey.name);
    console.log('Value:', value[0]);  // 数值
    console.log('Time:', value[1]);   // 时间戳
  }
};

// 获取特定数据键的值
function getValue(keyName) {
  var data = self.ctx.data;
  for (var i = 0; i < data.length; i++) {
    if (data[i].dataKey.name === keyName) {
      return data[i].data[0][0];  // 返回最新值
    }
  }
  return null;
}
```

### 3.4 设置访问

```javascript
// 访问组件设置
self.onInit = function() {
  var settings = self.ctx.settings;
  
  // 获取设置值（带默认值）
  var title = settings.title || 'Default Title';
  var threshold = settings.threshold || 100;
  var showIcon = settings.showIcon !== false;  // 默认 true
  
  // 应用到 UI
  updateTitle(title);
};
```

---

## 四、Settings Schema 详解

### 4.1 基础 Schema 结构

```json
{
  "schema": {
    "type": "object",
    "title": "Settings",
    "properties": {
      "title": {
        "title": "Widget Title",
        "type": "string",
        "default": "My Widget"
      },
      "threshold": {
        "title": "Alert Threshold",
        "type": "number",
        "default": 100
      }
    },
    "required": ["title"]
  },
  "form": [
    "title",
    "threshold"
  ]
}
```

### 4.2 支持的字段类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `string` | 文本输入 | 标题、描述 |
| `number` | 数值输入 | 阈值、最大值 |
| `boolean` | 复选框 | 显示/隐藏 |
| `object` | 嵌套对象 | 分组设置 |
| `array` | 数组 | 列表、多选 |

### 4.3 Form 字段类型

```json
{
  "form": [
    {
      "key": "title",
      "type": "text"  // 文本输入
    },
    {
      "key": "color",
      "type": "color"  // 颜色选择器
    },
    {
      "key": "image",
      "type": "image"  // 图片选择
    },
    {
      "key": "code",
      "type": "javascript"  // JS 代码编辑器
    },
    {
      "key": "html",
      "type": "html"  // HTML 编辑器
    },
    {
      "key": "style",
      "type": "css"  // CSS 编辑器
    },
    {
      "key": "level",
      "type": "rc-select",  // 下拉选择
      "items": [
        {"value": "low", "label": "Low"},
        {"value": "high", "label": "High"}
      ]
    }
  ]
}
```

### 4.4 条件显示

```json
{
  "schema": {
    "properties": {
      "useCustomColor": {
        "type": "boolean",
        "default": false
      },
      "customColor": {
        "type": "string"
      }
    }
  },
  "form": [
    "useCustomColor",
    {
      "key": "customColor",
      "type": "color",
      "condition": "model.useCustomColor === true"  // 条件显示
    }
  ]
}
```

### 4.5 分组设置

```json
{
  "schema": {
    "properties": {
      "appearance": {
        "title": "Appearance",
        "type": "object",
        "properties": {
          "backgroundColor": {"type": "string"},
          "textColor": {"type": "string"}
        }
      },
      "behavior": {
        "title": "Behavior",
        "type": "object",
        "properties": {
          "autoRefresh": {"type": "boolean"},
          "refreshInterval": {"type": "number"}
        }
      }
    }
  },
  "form": [
    {
      "key": "appearance",
      "items": [
        {"key": "appearance.backgroundColor", "type": "color"},
        {"key": "appearance.textColor", "type": "color"}
      ]
    },
    {
      "key": "behavior",
      "items": [
        "behavior.autoRefresh",
        "behavior.refreshInterval"
      ]
    }
  ],
  "groupInfoes": [
    {"formIndex": 0, "GroupTitle": "Appearance Settings"},
    {"formIndex": 1, "GroupTitle": "Behavior Settings"}
  ]
}
```

---

## 五、模板系统详解

### 5.1 HTML 模板语法

ThingsBoard 使用 **AngularJS 模板语法**（在 Widget 中）：

```html
<!-- 数据绑定 -->
<div>{{value}}</div>

<!-- 表达式 -->
<div>{{value * 100}}%</div>

<!-- 过滤器 -->
<div>{{timestamp | date:'yyyy-MM-dd HH:mm'}}</div>
<div>{{value | number:2}}</div>

<!-- 条件渲染 -->
<div ng-if="isAlarm">⚠️ Alarm!</div>
<div ng-show="isVisible">Content</div>

<!-- 循环 -->
<ul>
  <li ng-repeat="item in items">{{item.name}}</li>
</ul>

<!-- 样式绑定 -->
<div ng-style="{color: color, 'font-size': size + 'px'}">Styled</div>
<div ng-class="{'alarm': isAlarm, 'normal': !isAlarm}">Status</div>
```

### 5.2 JavaScript 模板字符串

在 JS 中动态生成 HTML：

```javascript
self.onDataUpdated = function() {
  var value = getValue('temperature');
  var html = `
    <div class="sensor-value ${value > threshold ? 'alarm' : 'normal'}">
      <span class="value">${value.toFixed(1)}</span>
      <span class="unit">°C</span>
    </div>
  `;
  self.ctx.$container.html(html);
};
```

### 5.3 模板与 is 调用

```javascript
// 使用 is 函数进行条件判断
self.onDataUpdated = function() {
  var value = getValue('status');
  
  // is 函数检查
  if (is(value, 'CRITICAL')) {
    showCriticalAlert();
  } else if (is(value, 'WARNING')) {
    showWarningAlert();
  }
};

// 或者使用三元表达式
var statusClass = is(alarmLevel, 'HIGH') ? 'high-priority' : 'low-priority';
```

---

## 六、调试技巧

### 6.1 Console 调试

```javascript
// 简单日志
console.log('Data updated:', self.ctx.data);

// 查看数据源
console.table(self.ctx.datasources);

// 查看设置
console.log('Settings:', JSON.stringify(self.ctx.settings, null, 2));
```

### 6.2 断点调试

```javascript
// 在代码中插入 debugger 语句
self.onDataUpdated = function() {
  debugger;  // 浏览器会在此处暂停
  var data = self.ctx.data;
  // ...
};
```

**步骤：**
1. 在代码中插入 `debugger;`
2. 点击 **Run** 按钮
3. 打开浏览器开发者工具 (F12)
4. 代码会在 `debugger` 处暂停
5. 使用调试工具单步执行、查看变量

### 6.3 预览调试

- Widget Preview 区域支持 **Function** 数据源
- 可以编写模拟数据函数进行测试

```javascript
// 模拟数据函数
function generateData() {
  return {
    temperature: 20 + Math.random() * 10,
    humidity: 40 + Math.random() * 20
  };
}
```

---

## 七、最佳实践

### 7.1 代码组织

```javascript
// 使用立即执行函数避免全局污染
(function() {
  var self = this;
  
  // 私有变量
  var privateVar = 0;
  
  // 初始化
  self.onInit = function() {
    initUI();
    bindEvents();
  };
  
  // 私有函数
  function initUI() {
    // UI 初始化
  }
  
  function bindEvents() {
    // 事件绑定
  }
  
  // 公开方法
  self.onDataUpdated = function() {
    updateData();
  };
  
  function updateData() {
    // 数据处理
  }
})();
```

### 7.2 性能优化

```javascript
// 1. 使用防抖避免频繁更新
var debounceTimer;
self.onDataUpdated = function() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(function() {
    doUpdate();
  }, 100);  // 100ms 防抖
};

// 2. 避免重复 DOM 操作
var $container = self.ctx.$container;
var $value = $container.find('.value');

self.onDataUpdated = function() {
  // 只更新内容，不重建 DOM
  $value.text(newValue);
};

// 3. 及时清理资源
self.onDestroy = function() {
  clearInterval(timer);
  $container.off('click');  // 解绑事件
};
```

### 7.3 错误处理

```javascript
self.onDataUpdated = function() {
  try {
    var data = self.ctx.data;
    if (!data || data.length === 0) {
      console.warn('No data available');
      showNoDataMessage();
      return;
    }
    
    processData(data);
  } catch (e) {
    console.error('Widget error:', e);
    showErrorMessage(e.message);
  }
};

function showNoDataMessage() {
  self.ctx.$container.html('<div class="no-data">No data available</div>');
}

function showErrorMessage(msg) {
  self.ctx.$container.html('<div class="error">Error: ' + msg + '</div>');
}
```

### 7.4 样式隔离

```css
/* 使用组件类名前缀避免样式冲突 */
.my-fall-detection-widget {
  /* 组件样式 */
}

.my-fall-detection-widget .alarm-indicator {
  /* 子元素样式 */
}

/* 避免使用全局选择器 */
/* ❌ 不推荐 */
.alarm { color: red; }

/* ✅ 推荐 */
.my-fall-detection-widget .alarm { color: red; }
```

---

## 八、注意事项

### 8.1 版本兼容性

| 版本 | 注意事项 |
|------|----------|
| v3.4+ | Settings Schema 改为 Angular 组件，创建新组件时需移除 Widget Settings tab 的组件 |
| v3.0+ | 支持 react-schema-form |
| v2.x | 使用旧版设置系统 |

### 8.2 安全限制

- Widget 运行在沙箱环境中
- 无法访问全局 `window` 对象
- 无法使用 `eval()` 或 `new Function()`
- 外部资源需通过 Resources tab 引入

### 8.3 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `self is not defined` | 忘记 `var self = this;` | 在开头添加 |
| `ctx is undefined` | 在 onInit 外访问 ctx | 确保在生命周期函数内 |
| 样式不生效 | CSS 选择器冲突 | 使用组件前缀类名 |
| 数据不更新 | 未实现 onDataUpdated | 添加回调函数 |
| 设置不生效 | Schema 格式错误 | 检查 JSON 语法 |

---

## 九、资源与参考

### 官方文档
- [Widget Development Guide](https://thingsboard.io/docs/user-guide/contribution/widgets-development/)
- [Widget Library](https://thingsboard.io/docs/user-guide/ui/widget-library/)

### 社区资源
- [ThingsBoard GitHub](https://github.com/thingsboard/thingsboard)
- [react-schema-form](http://networknt.github.io/react-schema-form/)

### 相关技能
- AngularJS 模板语法
- JavaScript ES6+
- CSS3 / SCSS

---

*文档状态: 阶段二进行中*  
*最后更新: 2026-03-22*