# 第十章：最佳实践与注意事项

## 10.1 性能优化

### 使用 OnPush 变更检测

```typescript
// ✅ 好的做法：使用 OnPush 变更检测
@Component({
    selector: 'tb-optimized-widget',
    changeDetection: ChangeDetectionStrategy.OnPush,
    // ...
})
export class OptimizedWidgetComponent {
    constructor(private cdr: ChangeDetectorRef) {}
    
    updateData() {
        // 数据处理...
        this.cdr.markForCheck(); // 标记需要检测
    }
}
```

### 避免频繁重绘

```javascript
// ❌ 避免：每次更新都重新创建图表
self.onDataUpdated = function() {
    $('#chart', ctx.$container).empty();
    createNewChart();  // 性能差！
};

// ✅ 正确：更新现有图表数据
self.onDataUpdated = function() {
    if (myChart) {
        myChart.data.datasets[0].data = newData;
        myChart.update('none');  // 不带动画更新
    }
};
```

### 节流处理

```javascript
// 节流函数
function throttle(func, limit) {
    var inThrottle;
    return function() {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}

// 使用节流
self.onDataUpdated = throttle(function() {
    updateChart();
}, 1000);  // 最多每秒更新一次
```

## 10.2 内存管理

### 清理订阅

```typescript
export class SafeWidgetComponent implements OnInit, OnDestroy {
    private subscriptions: Subscription[] = [];
    private intervals: any[] = [];
    private timeouts: any[] = [];
    
    ngOnInit() {
        // 记录所有订阅
        const sub = this.someObservable.subscribe();
        this.subscriptions.push(sub);
        
        // 记录定时器
        const interval = setInterval(() => {}, 1000);
        this.intervals.push(interval);
        
        // 记录延时器
        const timeout = setTimeout(() => {}, 5000);
        this.timeouts.push(timeout);
    }
    
    ngOnDestroy() {
        // 清理所有订阅
        this.subscriptions.forEach(sub => sub.unsubscribe());
        
        // 清理所有定时器
        this.intervals.forEach(interval => clearInterval(interval));
        
        // 清理所有延时器
        this.timeouts.forEach(timeout => clearTimeout(timeout));
    }
}
```

### 释放 DOM 引用

```javascript
self.onDestroy = function() {
    // 清理图表实例
    if (myChart) {
        myChart.destroy();
        myChart = null;  // 释放引用
    }
    
    // 清理 DOM 引用
    canvasElement = null;
    containerElement = null;
};
```

## 10.3 错误处理

### RPC 调用错误处理

```typescript
sendCommand(method: string, params?: any): void {
    this.ctx.controlApi.sendCommand({ method, params })
        .pipe(
            catchError(error => {
                // 显示错误提示
                this.ctx.showErrorToast(`Command failed: ${error.message}`);
                return throwError(error);
            })
        )
        .subscribe(
            response => {
                this.ctx.showSuccessToast('Command executed successfully');
            }
        );
}
```

### JavaScript 错误处理

```javascript
self.onDataUpdated = function() {
    try {
        // 数据处理
        var value = ctx.data[0].data[0][1];
        updateDisplay(value);
    } catch (error) {
        console.error('Error updating data:', error);
        showError('数据更新失败');
    }
};

function showError(message) {
    $('#error-message', ctx.$container)
        .text(message)
        .show()
        .delay(3000)
        .fadeOut();
}
```

## 10.4 代码组织

### 模块化结构

```javascript
// ============================================
// Widget 模块结构
// ============================================

// 配置
var CONFIG = {
    updateInterval: 1000,
    maxDataPoints: 100,
    defaultColor: '#1890ff'
};

// 状态
var state = {
    chart: null,
    data: [],
    isLoading: false
};

// 生命周期
self.onInit = function() {
    initChart();
    bindEvents();
};

self.onDataUpdated = function() {
    processData();
    updateChart();
};

self.onDestroy = function() {
    cleanup();
};

// 功能函数
function initChart() { }
function processData() { }
function updateChart() { }
function bindEvents() { }
function cleanup() { }
```

## 10.5 常见错误与解决

| 错误 | 原因 | 解决 |
|------|------|------|
| `ctx is undefined` | 组件未正确接收 ctx | 检查 HTML 中 `[ctx]="ctx"` |
| 数据不更新 | 未订阅数据流 | 实现 onDataUpdated 方法 |
| RPC 无响应 | 设备不在线 | 检查设备连接状态 |
| 样式不生效 | CSS 作用域问题 | 使用 ::ng-deep 或全局样式 |
| 图表不显示 | Canvas 尺寸为0 | 在 onResize 中设置尺寸 |
| 内存泄漏 | 未清理订阅/定时器 | 在 onDestroy 中清理 |

## 10.6 安全注意事项

### 避免 XSS

```javascript
// ❌ 危险：直接插入用户输入
$('#content', ctx.$container).html(userInput);

// ✅ 安全：使用 text() 或转义
$('#content', ctx.$container).text(userInput);

// 或使用转义函数
function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

### 验证 RPC 参数

```javascript
self.sendCommand = function(method, params) {
    // 验证方法名
    var allowedMethods = ['turnOn', 'turnOff', 'setTemp'];
    if (!allowedMethods.includes(method)) {
        console.error('Invalid method:', method);
        return;
    }
    
    // 验证参数
    if (params && typeof params !== 'object') {
        console.error('Invalid params:', params);
        return;
    }
    
    // 发送命令
    ctx.controlApi.sendCommand({ method, params });
};
```

## 10.7 开发 checklist

```markdown
□ 使用 console.log 验证数据流
□ 添加错误处理 try-catch
□ 在 onDestroy 中清理资源
□ 验证 DOM 元素存在后再操作
□ 使用节流避免频繁更新
□ 测试不同尺寸下的显示效果
□ 验证 RPC 命令响应
□ 检查内存使用情况
□ 添加加载状态提示
□ 测试边界条件（无数据、错误数据）
```

## 10.8 版本兼容性

### v3.4+ 重要变更

```
Starting from v3.4:
- Settings Schema JSON forms replaced with Angular components
- When creating new settings schemas, remove components from Widget Settings tab
```

### 向后兼容

```javascript
// 检测版本
var version = ctx.widgetConfig.version || '3.0';

if (version >= '3.4') {
    // 使用新 API
} else {
    // 使用旧 API
}
```
