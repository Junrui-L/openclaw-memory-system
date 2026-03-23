# 第七章：调试技巧

## 7.1 使用 console.log

最简单的调试方法，在代码中输出变量值：

```javascript
self.onDataUpdated = function() {
    console.log('Data updated:', ctx.data);
    console.log('First datasource:', ctx.data[0]);
    console.log('Latest value:', ctx.data[0].data[0][1]);
};
```

### 格式化输出

```javascript
// 表格形式显示数据
console.table(ctx.data);

// 分组输出
console.group('Widget Data');
console.log('Datasources:', ctx.datasources);
console.log('Settings:', ctx.settings);
console.groupEnd();

// 带样式输出
console.log('%c Alarm triggered!', 'color: red; font-size: 20px;');
```

## 7.2 使用 debugger

在代码中设置断点，浏览器会自动暂停执行：

```javascript
self.onDataUpdated = function() {
    debugger;  // 浏览器会在这里暂停
    
    var value = ctx.data[0].data[0][1];
    // 可以查看变量、单步执行
};
```

### 使用步骤

1. 在 Widget Editor 中点击 **Run**
2. 打开浏览器开发者工具（F12）
3. 切换到 **Sources** 标签
4. 代码会在 `debugger` 处暂停
5. 使用以下按钮调试：
   - ▶️ Resume：继续执行
   - ⏭️ Step over：单步跳过
   - ⏎ Step into：单步进入
   - ⏏️ Step out：单步退出

## 7.3 查看 ctx 对象结构

```javascript
self.onInit = function() {
    // 打印完整的 ctx 对象
    console.log('Context:', ctx);
    
    // 查看特定属性
    console.log('Data structure:', JSON.stringify(ctx.data, null, 2));
    console.log('Settings:', ctx.settings);
    console.log('Width x Height:', ctx.width, 'x', ctx.height);
};
```

## 7.4 网络请求调试

### 查看 RPC 命令

```javascript
self.sendCommand = function(method, params) {
    console.log('Sending RPC:', method, params);
    
    ctx.controlApi.sendCommand({
        method: method,
        params: params
    }).subscribe(
        function(response) {
            console.log('RPC Success:', response);  // 成功响应
        },
        function(error) {
            console.error('RPC Error:', error);      // 错误信息
            console.error('Error details:', {
                message: error.message,
                status: error.status,
                data: error.data
            });
        }
    );
};
```

## 7.5 常见问题排查

### 问题1：数据不更新

```javascript
// ❌ 错误：直接访问可能不存在的数据
self.onDataUpdated = function() {
    var value = ctx.data[0].data[0][1];  // 可能报错！
};

// ✅ 正确：添加安全检查
self.onDataUpdated = function() {
    if (ctx.data && ctx.data.length > 0) {
        if (ctx.data[0].data && ctx.data[0].data.length > 0) {
            var value = ctx.data[0].data[0][1];
            console.log('Value:', value);
        } else {
            console.warn('No data points available');
        }
    } else {
        console.warn('No datasources available');
    }
};
```

### 问题2：DOM 元素找不到

```javascript
// ❌ 错误：在 onInit 时元素可能还没渲染
self.onInit = function() {
    var el = $('#my-element');  // 可能找不到
};

// ✅ 正确：使用 ctx.$container 限定范围
self.onInit = function() {
    var el = $('#my-element', ctx.$container);
    console.log('Element found:', el.length > 0);
};
```

### 问题3：图表不显示

```javascript
self.onInit = function() {
    var canvas = $('#chart', ctx.$container)[0];
    
    // 检查 canvas 是否存在
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    
    // 检查尺寸
    console.log('Canvas size:', canvas.width, 'x', canvas.height);
    
    // 初始化图表
    var chart = new Chart(canvas, {...});
};
```

### 问题4：样式不生效

```javascript
// 检查样式是否正确应用
self.onInit = function() {
    var el = $('#my-element', ctx.$container);
    
    // 查看计算样式
    console.log('Computed styles:', {
        width: el.css('width'),
        height: el.css('height'),
        display: el.css('display'),
        visibility: el.css('visibility')
    });
    
    // 查看元素类名
    console.log('Classes:', el.attr('class'));
};
```

## 7.6 性能调试

```javascript
// 测量执行时间
self.onDataUpdated = function() {
    console.time('dataUpdate');
    
    // 数据处理逻辑
    processData();
    
    console.timeEnd('dataUpdate');  // 输出: dataUpdate: 2.5ms
};

// 内存使用检查
self.onInit = function() {
    if (performance && performance.memory) {
        console.log('Memory used:', 
            (performance.memory.usedJSHeapSize / 1048576).toFixed(2), 
            'MB'
        );
    }
};
```

## 7.7 浏览器开发者工具技巧

### Elements 面板
- 实时查看和修改 HTML/CSS
- 检查元素尺寸和位置
- 查看应用的 CSS 规则

### Console 面板
- 执行 JavaScript 代码
- 查看日志输出
- 使用 `$0` 引用当前选中的元素

### Network 面板
- 查看 RPC 请求和响应
- 检查外部资源加载
- 查看请求耗时

### Sources 面板
- 设置断点
- 单步调试
- 查看调用栈

## 7.8 调试清单

```markdown
□ 使用 console.log 输出关键变量
□ 使用 debugger 设置断点
□ 检查 ctx.data 结构
□ 验证 DOM 元素存在
□ 确认事件绑定成功
□ 检查 RPC 请求响应
□ 查看浏览器控制台错误
□ 验证样式是否正确应用
```
