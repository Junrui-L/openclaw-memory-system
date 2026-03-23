# 第四章：Context (ctx) 对象详解

## 4.1 什么是 ctx？

`ctx`（Context）是 Widget 与 ThingsBoard 平台交互的**核心对象**，包含了所有数据、配置和方法。

```javascript
// 访问方式
self.ctx  // 全局上下文对象
```

## 4.2 ctx 核心属性速查表

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `ctx.data` | Array | 当前数据数组 | `ctx.data[0].data[0][1]` |
| `ctx.datasources` | Array | 数据源配置 | `ctx.datasources[0].entityId` |
| `ctx.defaultSubscription` | Object | 默认订阅对象 | `ctx.defaultSubscription.data` |
| `ctx.timeWindow` | Object | 时间窗口 | `ctx.timeWindow.minTime` |
| `ctx.width` | Number | Widget 宽度 | `ctx.width` |
| `ctx.height` | Number | Widget 高度 | `ctx.height` |
| `ctx.$container` | jQuery | Widget DOM 容器 | `$('#my-id', ctx.$container)` |
| `ctx.$scope` | Angular Scope | Angular 作用域 | `ctx.$scope.myComponent` |
| `ctx.settings` | Object | Widget 设置 | `ctx.settings.cardTitle` |

## 4.3 ctx.data 数据结构

### Latest Values 格式

```javascript
ctx.data = [
    {
        dataKey: {
            name: "temperature",      // 数据键名称
            label: "温度",            // 显示标签
            color: "#ff0000",         // 颜色
            units: "°C",              // 单位
            decimals: 2,              // 小数位数
            // ... 其他配置
        },
        data: [
            [1647840000000, 25.5]     // [时间戳, 值] - 只有一条（最新）
        ]
    },
    {
        dataKey: { name: "humidity", label: "湿度", ... },
        data: [[1647840000000, 60]]
    }
]
```

### Time Series 格式

```javascript
ctx.data = [
    {
        dataKey: { name: "temperature", label: "温度", ... },
        data: [
            [1647836400000, 24.0],     // 历史数据点1
            [1647837000000, 24.5],     // 历史数据点2
            [1647837600000, 25.0],     // 历史数据点3
            // ... 多个数据点
        ]
    }
]
```

## 4.4 数据获取实战

### 获取最新值

```javascript
self.onDataUpdated = function() {
    // 方式1: 安全获取（推荐）
    if (ctx.data && ctx.data.length > 0) {
        var dataItem = ctx.data[0];
        
        if (dataItem.data && dataItem.data.length > 0) {
            var latest = dataItem.data[dataItem.data.length - 1];
            var timestamp = latest[0];    // 时间戳 (ms)
            var value = latest[1];         // 数值
            
            console.log('Value:', value);
            console.log('Time:', new Date(timestamp));
        }
    }
    
    // 方式2: 通过 defaultSubscription
    if (ctx.defaultSubscription && 
        ctx.defaultSubscription.data && 
        ctx.defaultSubscription.data.length > 0) {
        
        var value = ctx.defaultSubscription.data[0].data[0][1];
    }
};
```

### 遍历多个数据源

```javascript
self.onDataUpdated = function() {
    // 遍历所有数据源
    for (var i = 0; i < ctx.data.length; i++) {
        var dataItem = ctx.data[i];
        var dataKey = dataItem.dataKey;      // 数据键配置
        var dataSet = dataItem.data;          // 数据数组
        
        console.log('Data key:', dataKey.name);
        console.log('Label:', dataKey.label);
        console.log('Color:', dataKey.color);
        
        // 遍历数据点
        for (var d = 0; d < dataSet.length; d++) {
            var point = dataSet[d];
            var ts = point[0];    // 时间戳
            var val = point[1];   // 值
            
            console.log('  [' + new Date(ts) + '] = ' + val);
        }
    }
};
```

### Time Series 数据处理

```javascript
self.onDataUpdated = function() {
    // 准备图表数据
    var chartData = [];
    
    for (var i = 0; i < ctx.data.length; i++) {
        var dataItem = ctx.data[i];
        var series = {
            label: dataItem.dataKey.label,
            color: dataItem.dataKey.color,
            data: []
        };
        
        // 转换数据格式
        for (var d = 0; d < dataItem.data.length; d++) {
            var point = dataItem.data[d];
            series.data.push({
                x: point[0],      // 时间戳
                y: point[1]       // 值
            });
        }
        
        chartData.push(series);
    }
    
    // 更新图表
    updateChart(chartData);
};
```

## 4.5 ctx.datasources 数据源信息

```javascript
// 获取数据源配置
var datasource = ctx.datasources[0];

console.log(datasource.entityId);      // 实体ID
console.log(datasource.entityType);    // 实体类型 (DEVICE, ASSET, etc.)
console.log(datasource.entityName);    // 实体名称
console.log(datasource.name);          // 数据源名称

// 数据键列表
var dataKeys = datasource.dataKeys;
for (var i = 0; i < dataKeys.length; i++) {
    console.log(dataKeys[i].name);     // 数据键名称
    console.log(dataKeys[i].label);    // 显示标签
    console.log(dataKeys[i].type);     // 类型 (timeseries, attribute)
}
```

## 4.6 ctx.timeWindow 时间窗口

```javascript
// 时间窗口信息
var timeWindow = ctx.timeWindow;

console.log(timeWindow.minTime);    // 开始时间戳 (ms)
console.log(timeWindow.maxTime);    // 结束时间戳 (ms)
console.log(timeWindow.interval);   // 时间间隔 (ms)

// 用于限制图表显示范围
chart.options.scales.x.min = timeWindow.minTime;
chart.options.scales.x.max = timeWindow.maxTime;
```

## 4.7 ctx.settings 设置值

```javascript
// 在 Settings Schema 中定义
{
    "schema": {
        "properties": {
            "cardTitle": { "type": "string", "default": "Title" },
            "maxValue": { "type": "number", "default": 100 },
            "showIcon": { "type": "boolean", "default": true }
        }
    }
}

// 在 JavaScript 中使用
self.onInit = function() {
    var title = ctx.settings.cardTitle;      // "Title"
    var max = ctx.settings.maxValue;          // 100
    var show = ctx.settings.showIcon;         // true
    
    // 应用设置
    $('#title', ctx.$container).text(title);
};
```

## 4.8 ctx.$container DOM 操作

```javascript
// 在 Widget 容器内查找元素
var element = $('#my-element', ctx.$container);

// 修改内容
element.text('New value');
element.html('<span>HTML content</span>');

// 修改样式
element.css('color', 'red');
element.css({
    'background-color': '#f0f0f0',
    'padding': '10px'
});

// 绑定事件
element.on('click', function() {
    console.log('Clicked!');
});

// 获取容器尺寸
var width = ctx.$container.width();
var height = ctx.$container.height();
```

## 4.9 ctx.controlApi RPC 控制

```javascript
// 发送 RPC 命令到设备
self.sendCommand = function(method, params) {
    var rpcRequest = {
        method: method,
        params: params || {}
    };
    
    ctx.controlApi.sendCommand(rpcRequest).subscribe(
        function(response) {
            console.log('Success:', response);
        },
        function(error) {
            console.error('Error:', error);
        }
    );
};

// 使用示例
$('#on-button', ctx.$container).on('click', function() {
    self.sendCommand('turnOn');
});

$('#set-temp', ctx.$container).on('click', function() {
    self.sendCommand('setTemperature', { value: 25 });
});
```

## 4.10 完整数据获取示例

```javascript
self.onDataUpdated = function() {
    // 安全获取数据
    if (!ctx.data || ctx.data.length === 0) {
        console.warn('No data available');
        return;
    }
    
    // 获取第一个数据源
    var dataItem = ctx.data[0];
    var dataKey = dataItem.dataKey;
    var dataSet = dataItem.data;
    
    // 获取设置
    var settings = ctx.settings || {};
    var maxValue = settings.maxValue || 100;
    var units = dataKey.units || '';
    
    // 处理数据
    if (dataSet.length > 0) {
        var latest = dataSet[dataSet.length - 1];
        var value = latest[1];
        var timestamp = latest[0];
        
        // 更新显示
        updateUI({
            value: value,
            units: units,
            timestamp: timestamp,
            label: dataKey.label,
            maxValue: maxValue
        });
    }
};

function updateUI(data) {
    $('#value', ctx.$container).text(data.value.toFixed(2));
    $('#units', ctx.$container).text(data.units);
    $('#label', ctx.$container).text(data.label);
    $('#time', ctx.$container).text(new Date(data.timestamp).toLocaleString());
}
```

