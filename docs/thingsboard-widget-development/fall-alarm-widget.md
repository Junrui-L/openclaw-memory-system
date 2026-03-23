# 跌倒告警卡片 Widget - Fall Alarm Card

> 基于锐哥提供的设计图开发
> 开发日期: 2026-03-21

---

## 设计预览

```
┌─────────────────────────────────────────┐
│  ⚠️ Fall Alarm                    MINOR │
│                                         │
│  客厅检测到跌倒，需要立即关注            │
│                                         │
│  📅 2026-03-21 11:59:55                 │
│  📍 客厅                               │
│  👤 Johe ha                            │
│                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 呼叫急救 │ │联系家人 │ │  误报   │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
```

---

## Widget 代码

### 1. Resources/HTML

```html
<div class="fall-alarm-card" id="alarm-card">
    <div class="alarm-header">
        <div class="alarm-title">
            <span class="alarm-icon">⚠️</span>
            <span class="alarm-type">Fall Alarm</span>
        </div>
        <div class="alarm-severity" id="severity-badge">MINOR</div>
    </div>
    
    <div class="alarm-body">
        <div class="alarm-message" id="alarm-message">
            客厅检测到跌倒，需要立即关注
        </div>
        
        <div class="alarm-details">
            <div class="detail-item">
                <span class="detail-icon">📅</span>
                <span class="detail-text" id="alarm-time">2026-03-21 11:59:55</span>
            </div>
            <div class="detail-item">
                <span class="detail-icon">📍</span>
                <span class="detail-text" id="alarm-location">客厅</span>
            </div>
            <div class="detail-item">
                <span class="detail-icon">👤</span>
                <span class="detail-text" id="resident-name">Johe ha</span>
            </div>
        </div>
    </div>
    
    <div class="alarm-actions">
        <button class="action-btn btn-emergency" id="btn-emergency">
            <span class="btn-icon">🚨</span>
            <span class="btn-text">呼叫急救服务</span>
        </button>
        <button class="action-btn btn-family" id="btn-family">
            <span class="btn-icon">📞</span>
            <span class="btn-text">联系家人</span>
        </button>
        <button class="action-btn btn-false" id="btn-false">
            <span class="btn-icon">✓</span>
            <span class="btn-text">标记为误报</span>
        </button>
    </div>
</div>
```

### 2. Resources/CSS

```css
/* 告警卡片容器 */
.fall-alarm-card {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
    border-radius: 16px;
    border: 2px solid #ffccc7;
    padding: 20px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    box-shadow: 0 4px 20px rgba(255, 77, 79, 0.15);
}

/* 头部 */
.alarm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ffccc7;
}

.alarm-title {
    display: flex;
    align-items: center;
    gap: 8px;
}

.alarm-icon {
    font-size: 24px;
}

.alarm-type {
    font-size: 18px;
    font-weight: 700;
    color: #cf1322;
}

/* 告警级别徽章 */
.alarm-severity {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.alarm-severity.CRITICAL {
    background: #ff4d4f;
    color: white;
}

.alarm-severity.MAJOR {
    background: #faad14;
    color: white;
}

.alarm-severity.MINOR {
    background: #ffa940;
    color: white;
}

.alarm-severity.WARNING {
    background: #73d13d;
    color: white;
}

.alarm-severity.INDETERMINATE {
    background: #8c8c8c;
    color: white;
}

/* 告警内容 */
.alarm-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.alarm-message {
    font-size: 16px;
    color: #262626;
    line-height: 1.5;
    padding: 12px;
    background: rgba(255, 77, 79, 0.05);
    border-radius: 8px;
    border-left: 3px solid #ff4d4f;
}

/* 详情列表 */
.alarm-details {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: #595959;
}

.detail-icon {
    font-size: 16px;
    width: 24px;
    text-align: center;
}

.detail-text {
    font-weight: 500;
}

/* 操作按钮区 */
.alarm-actions {
    display: flex;
    gap: 10px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #ffccc7;
}

.action-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 12px 8px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: inherit;
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
    transform: translateY(0);
}

.btn-icon {
    font-size: 20px;
}

.btn-text {
    font-size: 12px;
    font-weight: 600;
}

/* 急救按钮 */
.btn-emergency {
    background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
    color: white;
}

.btn-emergency:hover {
    background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%);
}

/* 联系家人按钮 */
.btn-family {
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    color: white;
}

.btn-family:hover {
    background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
}

/* 误报按钮 */
.btn-false {
    background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
    color: white;
}

.btn-false:hover {
    background: linear-gradient(135deg, #73d13d 0%, #52c41a 100%);
}

/* 已处理状态 */
.fall-alarm-card.resolved {
    opacity: 0.7;
    border-color: #52c41a;
    background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
}

.fall-alarm-card.resolved .alarm-message {
    border-left-color: #52c41a;
}

/* 响应式 */
@media (max-width: 400px) {
    .alarm-actions {
        flex-direction: column;
    }
    
    .action-btn {
        flex-direction: row;
        justify-content: center;
        padding: 10px;
    }
}
```

### 3. JavaScript

```javascript
// ============================================
// 跌倒告警卡片 Widget
// ============================================

var alarmData = null;
var isResolved = false;

// 初始化
self.onInit = function() {
    console.log('Fall Alarm Widget initialized');
    
    // 绑定按钮事件
    bindButtonEvents();
    
    // 初始化显示
    updateDisplay();
};

// 数据更新
self.onDataUpdated = function() {
    console.log('Alarm data updated:', ctx.data);
    
    if (ctx.data && ctx.data.length > 0) {
        // 解析告警数据
        parseAlarmData();
        // 更新显示
        updateDisplay();
    }
};

// 尺寸变化
self.onResize = function() {
    // 响应式调整（如果需要）
    var width = ctx.width;
    var card = $('#alarm-card', ctx.$container);
    
    if (width < 400) {
        card.addClass('compact');
    } else {
        card.removeClass('compact');
    }
};

// 销毁清理
self.onDestroy = function() {
    console.log('Fall Alarm Widget destroyed');
    // 清理事件绑定
    $('#btn-emergency', ctx.$container).off('click');
    $('#btn-family', ctx.$container).off('click');
    $('#btn-false', ctx.$container).off('click');
};

// Widget 行为配置
self.typeParameters = function() {
    return {
        maxDatasources: 1,
        singleEntity: true,
        previewWidth: '380px',
        previewHeight: '320px',
        embedTitlePanel: true
    };
};

// ============================================
// 辅助函数
// ============================================

// 解析告警数据
function parseAlarmData() {
    var dataItem = ctx.data[0];
    
    if (dataItem && dataItem.data.length > 0) {
        var latest = dataItem.data[dataItem.data.length - 1];
        var alarmJson = latest[1];
        
        // 如果数据是字符串，解析 JSON
        if (typeof alarmJson === 'string') {
            try {
                alarmData = JSON.parse(alarmJson);
            } catch (e) {
                console.error('Failed to parse alarm data:', e);
                alarmData = null;
            }
        } else {
            alarmData = alarmJson;
        }
    }
}

// 更新显示
function updateDisplay() {
    if (!alarmData) return;
    
    // 更新告警级别
    var severity = alarmData.severity || 'MINOR';
    $('#severity-badge', ctx.$container)
        .text(severity)
        .attr('class', 'alarm-severity ' + severity);
    
    // 更新告警消息
    var message = alarmData.message || '检测到跌倒，需要立即关注';
    $('#alarm-message', ctx.$container).text(message);
    
    // 更新时间
    var time = alarmData.time || formatTime(new Date());
    $('#alarm-time', ctx.$container).text(time);
    
    // 更新位置
    var location = alarmData.location || '未知位置';
    $('#alarm-location', ctx.$container).text(location);
    
    // 更新居民姓名
    var resident = alarmData.resident || '未知居民';
    $('#resident-name', ctx.$container).text(resident);
    
    // 更新处理状态
    if (alarmData.resolved || isResolved) {
        $('#alarm-card', ctx.$container).addClass('resolved');
    } else {
        $('#alarm-card', ctx.$container).removeClass('resolved');
    }
}

// 绑定按钮事件
function bindButtonEvents() {
    var container = ctx.$container;
    
    // 呼叫急救
    $('#btn-emergency', container).on('click', function() {
        console.log('Emergency call triggered');
        
        // 发送 RPC 命令
        sendCommand('callEmergency', {
            alarmId: alarmData ? alarmData.id : null,
            location: alarmData ? alarmData.location : null,
            resident: alarmData ? alarmData.resident : null
        });
        
        // 显示确认
        showToast('正在呼叫急救服务...', 'info');
    });
    
    // 联系家人
    $('#btn-family', container).on('click', function() {
        console.log('Contact family triggered');
        
        sendCommand('notifyFamily', {
            alarmId: alarmData ? alarmData.id : null,
            message: alarmData ? alarmData.message : 'Fall detected'
        });
        
        showToast('已通知家人', 'info');
    });
    
    // 标记为误报
    $('#btn-false', container).on('click', function() {
        console.log('Mark as false alarm');
        
        isResolved = true;
        $('#alarm-card', container).addClass('resolved');
        
        sendCommand('markAsFalseAlarm', {
            alarmId: alarmData ? alarmData.id : null
        });
        
        showToast('已标记为误报', 'success');
    });
}

// 发送 RPC 命令
function sendCommand(method, params) {
    var rpcRequest = {
        method: method,
        params: params || {}
    };
    
    if (ctx.controlApi) {
        ctx.controlApi.sendCommand(rpcRequest).subscribe(
            function(response) {
                console.log('Command success:', response);
            },
            function(error) {
                console.error('Command error:', error);
                showToast('操作失败: ' + error.message, 'error');
            }
        );
    } else {
        console.warn('Control API not available');
    }
}

// 显示提示
function showToast(message, type) {
    // 创建临时提示元素
    var toast = $('<div class="alarm-toast ' + type + '">' + message + '</div>');
    toast.css({
        'position': 'fixed',
        'top': '20px',
        'right': '20px',
        'padding': '12px 20px',
        'border-radius': '8px',
        'color': 'white',
        'font-weight': '500',
        'z-index': '9999',
        'opacity': '0',
        'transition': 'opacity 0.3s'
    });
    
    if (type === 'success') {
        toast.css('background', '#52c41a');
    } else if (type === 'error') {
        toast.css('background', '#ff4d4f');
    } else {
        toast.css('background', '#1890ff');
    }
    
    $('body').append(toast);
    
    // 显示动画
    setTimeout(function() {
        toast.css('opacity', '1');
    }, 10);
    
    // 自动隐藏
    setTimeout(function() {
        toast.css('opacity', '0');
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

// 格式化时间
function formatTime(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    var hours = String(date.getHours()).padStart(2, '0');
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var seconds = String(date.getSeconds()).padStart(2, '0');
    
    return year + '-' + month + '-' + day + ' ' + hours + ':' + minutes + ':' + seconds;
}
```

### 4. Settings Schema

```json
{
    "schema": {
        "type": "object",
        "title": "Alarm Card Settings",
        "properties": {
            "emergencyNumber": {
                "title": "Emergency Contact Number",
                "type": "string",
                "default": "120"
            },
            "familyContact": {
                "title": "Family Contact",
                "type": "string",
                "default": ""
            },
            "autoNotify": {
                "title": "Auto Notify Family",
                "type": "boolean",
                "default": true
            },
            "cardTitle": {
                "title": "Card Title",
                "type": "string",
                "default": "Fall Alarm"
            }
        }
    },
    "form": [
        "cardTitle",
        "emergencyNumber",
        "familyContact",
        "autoNotify"
    ]
}
```

---

## 数据结构

### 输入数据格式

```json
{
    "id": "alarm-001",
    "severity": "MINOR",
    "message": "客厅检测到跌倒，需要立即关注",
    "time": "2026-03-21 11:59:55",
    "location": "客厅",
    "resident": "Johe ha",
    "resolved": false
}
```

### 告警级别

| 级别 | 颜色 | 说明 |
|------|------|------|
| CRITICAL | 🔴 红色 | 危急，需立即处理 |
| MAJOR | 🟠 橙色 | 严重，需尽快处理 |
| MINOR | 🟡 黄色 | 次要，需关注 |
| WARNING | 🟢 绿色 | 警告，需注意 |
| INDETERMINATE | ⚪ 灰色 | 未确定 |

---

## RPC 命令

| 命令 | 参数 | 说明 |
|------|------|------|
| `callEmergency` | `{alarmId, location, resident}` | 呼叫急救服务 |
| `notifyFamily` | `{alarmId, message}` | 通知家人 |
| `markAsFalseAlarm` | `{alarmId}` | 标记为误报 |

---

## 使用说明

1. 创建 **Latest values** 类型的 Widget
2. 选择 **Alarm source** 作为数据源
3. 配置告警类型筛选（如 `Fall Alarm`）
4. 复制上述 HTML/CSS/JavaScript 到对应区域
5. 点击 **Run** 预览效果
6. 保存 Widget

---

## 截图

![Fall Alarm Card Design](fall-alarm-card-design.png)
