# 第三章：Widget 生命周期与核心 API

## 3.1 生命周期概述

Widget 有四个核心生命周期方法，按以下顺序执行：

```
用户添加 Widget 到 Dashboard
        ↓
   [onInit]  ← 初始化（仅一次）
        ↓
   [onDataUpdated] ← 首次数据加载
        ↓
   [onResize] ← 初始尺寸设置
        ↓
   ┌─────────────────┐
   │  运行中...       │
   │  数据更新 → onDataUpdated │
   │  尺寸变化 → onResize     │
   └─────────────────┘
        ↓
   [onDestroy] ← Widget 被移除
```

## 3.2 生命周期方法详解

### onInit - 初始化

```javascript
self.onInit = function() {
    // Widget 创建时调用（仅一次）
    // 用途：
    // - 初始化 DOM 元素
    // - 创建图表实例
    // - 设置初始状态
    // - 绑定事件监听器
    
    // 示例：初始化图表
    canvasElement = $('#my-chart', self.ctx.$container)[0];
    chart = new Chart(canvasElement, {
        type: 'line',
        data: { datasets: [] }
    });
};
```

### onDataUpdated - 数据更新

```javascript
self.onDataUpdated = function() {
    // 收到新数据时调用
    // 用途：
    // - 获取最新数据
    // - 更新图表/显示
    // - 触发 UI 刷新
    
    // 示例：更新图表数据
    var value = ctx.data[0].data[0][1];
    chart.data.datasets[0].data.push(value);
    chart.update();
};
```

### onResize - 尺寸变化

```javascript
self.onResize = function() {
    // Widget 大小改变时调用
    // 用途：
    // - 重新计算尺寸
    // - 调整图表大小
    // - 响应式布局调整
    
    // 示例：调整图表尺寸
    canvasElement.width = self.ctx.width;
    canvasElement.height = self.ctx.height;
    chart.resize();
};
```

### onDestroy - 销毁清理

```javascript
self.onDestroy = function() {
    // Widget 被移除时调用
    // 用途：
    // - 清除定时器
    // - 销毁图表实例
    // - 解绑事件监听器
    // - 释放内存
    
    // 示例：清理资源
    if (chart) {
        chart.destroy();
        chart = null;
    }
    clearInterval(updateTimer);
};
```

## 3.3 typeParameters - Widget 行为配置

```javascript
self.typeParameters = function() {
    return {
        // 最大数据源数量
        maxDatasources: 1,
        
        // 是否只允许单个实体
        singleEntity: true,
        
        // 预览默认尺寸
        previewWidth: '300px',
        previewHeight: '200px',
        
        // 是否隐藏标题面板
        embedTitlePanel: true,
        
        // 其他配置...
    };
};
```

### 配置参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `maxDatasources` | Number | 最大数据源数量限制 |
| `singleEntity` | Boolean | 是否只允许选择单个实体 |
| `previewWidth` | String | Widget 预览默认宽度 |
| `previewHeight` | String | Widget 预览默认高度 |
| `embedTitlePanel` | Boolean | 是否隐藏标题面板 |
| `hasDataPageLink` | Boolean | 是否有数据页面链接 |
| `datasourcesOptional` | Boolean | 数据源是否可选 |

## 3.4 完整代码模板

```javascript
// ============================================
// ThingsBoard Widget 完整模板
// ============================================

// 全局变量（组件状态）
var myChart;
var updateTimer;

// 1. 初始化
self.onInit = function() {
    console.log('Widget initialized');
    
    // 获取 DOM 元素
    var container = self.ctx.$container;
    var canvas = $('#my-canvas', container)[0];
    
    // 初始化组件
    initChart(canvas);
    
    // 设置定时器（如果需要）
    updateTimer = setInterval(function() {
        // 定时任务
    }, 5000);
};

// 2. 数据更新
self.onDataUpdated = function() {
    console.log('Data updated:', ctx.data);
    
    // 检查数据是否存在
    if (ctx.data && ctx.data.length > 0) {
        var dataItem = ctx.data[0];
        
        if (dataItem.data.length > 0) {
            // 获取最新值 [timestamp, value]
            var latest = dataItem.data[dataItem.data.length - 1];
            var timestamp = latest[0];
            var value = latest[1];
            
            // 更新显示
            updateDisplay(value, timestamp);
        }
    }
};

// 3. 尺寸变化
self.onResize = function() {
    console.log('Resized:', ctx.width, 'x', ctx.height);
    
    // 调整组件尺寸
    if (myChart) {
        myChart.resize();
    }
};

// 4. 销毁清理
self.onDestroy = function() {
    console.log('Widget destroyed');
    
    // 清理定时器
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
    
    // 销毁组件
    if (myChart) {
        myChart.destroy();
        myChart = null;
    }
};

// Widget 行为配置
self.typeParameters = function() {
    return {
        maxDatasources: 1,
        singleEntity: true,
        previewWidth: '300px',
        previewHeight: '200px',
        embedTitlePanel: true
    };
};

// 辅助函数
function initChart(canvas) {
    // 初始化图表逻辑
}

function updateDisplay(value, timestamp) {
    // 更新显示逻辑
}
```

## 3.5 生命周期最佳实践

### ✅ 好的做法

```javascript
// 1. 检查数据存在性
self.onDataUpdated = function() {
    if (ctx.data && ctx.data.length > 0 && ctx.data[0].data.length > 0) {
        var value = ctx.data[0].data[0][1];
        // 处理数据...
    }
};

// 2. 安全销毁
self.onDestroy = function() {
    if (myComponent) {
        myComponent.destroy();
        myComponent = null;  // 释放引用
    }
};

// 3. 使用局部变量避免全局污染
self.onInit = function() {
    var localVar = 'value';  // 不是全局变量
    // ...
};
```

### ❌ 避免的做法

```javascript
// 1. 不检查数据直接访问
self.onDataUpdated = function() {
    var value = ctx.data[0].data[0][1];  // 可能报错！
};

// 2. 不清理资源
self.onDestroy = function() {
    // 什么都没做，内存泄漏！
};

// 3. 创建全局变量
myGlobalVar = 'value';  // 污染全局命名空间
```

## 3.6 执行顺序验证

```javascript
self.onInit = function() {
    console.log('1. onInit - Widget 初始化');
};

self.onDataUpdated = function() {
    console.log('2. onDataUpdated - 数据更新');
};

self.onResize = function() {
    console.log('3. onResize - 尺寸变化');
};

// 预期控制台输出：
// 1. onInit - Widget 初始化
// 2. onDataUpdated - 数据更新
// 3. onResize - 尺寸变化
// 2. onDataUpdated - 数据更新（后续数据更新）
// 3. onResize - 尺寸变化（窗口调整）
```

---

## 下一步

继续学习 [第四章：Context (ctx) 对象详解](./04-context-object.md)
