# ThingsBoard 跌倒报警组件案例

> 案例文档: 跌倒检测报警 Widget  
> 创建时间: 2026-03-22  
> 用途: 项目最佳实践参考

---

## 📋 组件概述

### 功能描述
实时监测老人/患者的跌倒状态，当检测到跌倒时触发视觉和声音报警。

### 适用场景
- 智慧养老监护
- 医院病房监控
- 独居老人安全

### 数据源
- `fall_detected` (Boolean) - 跌倒检测状态
- `location` (String) - 位置信息
- `battery_level` (Number) - 设备电量
- `timestamp` (Number) - 时间戳

---

## 🎨 组件设计

### Widget 类型选择
**Alarm Widget** - 专门用于显示报警信息

### 界面布局

```
┌─────────────────────────────────────┐
│  🔴 跌倒报警 - 紧急                  │  ← 标题栏
├─────────────────────────────────────┤
│                                     │
│     ⚠️                              │  ← 大图标
│                                     │
│    检测到跌倒！                      │  ← 报警信息
│                                     │
│  📍 位置: 卧室                       │  ← 详情
│  🔋 电量: 85%                        │
│  ⏰ 时间: 14:32:15                   │
│                                     │
├─────────────────────────────────────┤
│  [确认] [呼叫] [查看位置]            │  ← 操作按钮
└─────────────────────────────────────┘
```

---

## 💻 完整代码实现

### 1. HTML Tab

```html
<div class="fall-detection-widget" ng-class="{'alarm-active': isAlarm}">
  <!-- 标题栏 -->
  <div class="widget-header">
    <span class="status-icon" ng-class="alarmLevel">{{statusIcon}}</span>
    <span class="title">{{widgetTitle}}</span>
  </div>
  
  <!-- 主内容区 -->
  <div class="widget-body">
    <!-- 大图标 -->
    <div class="main-icon" ng-class="{'pulse': isAlarm}">
      {{mainIcon}}
    </div>
    
    <!-- 报警信息 -->
    <div class="alarm-message" ng-if="isAlarm">
      <h2>{{alarmMessage}}</h2>
      <p class="sub-message">{{subMessage}}</p>
    </div>
    
    <!-- 正常状态 -->
    <div class="normal-message" ng-if="!isAlarm">
      <h3>{{normalMessage}}</h3>
    </div>
    
    <!-- 详情信息 -->
    <div class="details" ng-if="showDetails">
      <div class="detail-item" ng-if="location">
        <span class="icon">📍</span>
        <span class="label">位置:</span>
        <span class="value">{{location}}</span>
      </div>
      <div class="detail-item" ng-if="batteryLevel !== null">
        <span class="icon">🔋</span>
        <span class="label">电量:</span>
        <span class="value" ng-class="{'low-battery': batteryLevel < 20}">
          {{batteryLevel}}%
        </span>
      </div>
      <div class="detail-item" ng-if="lastUpdate">
        <span class="icon">⏰</span>
        <span class="label">时间:</span>
        <span class="value">{{lastUpdate | date:'HH:mm:ss'}}</span>
      </div>
    </div>
  </div>
  
  <!-- 操作按钮 -->
  <div class="widget-actions" ng-if="isAlarm && showActions">
    <button class="btn btn-confirm" ng-click="confirmAlarm()">
      {{confirmButtonText}}
    </button>
    <button class="btn btn-call" ng-click="callEmergency()" ng-if="enableCall">
      {{callButtonText}}
    </button>
    <button class="btn btn-location" ng-click="viewLocation()" ng-if="enableLocation">
      {{locationButtonText}}
    </button>
  </div>
</div>
```

### 2. CSS Tab

```css
/* ========== 基础样式 ========== */
.fall-detection-widget {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: white;
  transition: all 0.3s ease;
}

/* 报警状态 - 红色渐变 */
.fall-detection-widget.alarm-active {
  background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
  animation: alarm-pulse 1s ease-in-out infinite;
}

@keyframes alarm-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 65, 108, 0.5); }
  50% { box-shadow: 0 0 40px rgba(255, 65, 108, 0.8); }
}

/* ========== 标题栏 ========== */
.widget-header {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.status-icon {
  font-size: 18px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.status-icon.normal {
  background: #4CAF50;
}

.status-icon.warning {
  background: #FF9800;
}

.status-icon.critical {
  background: #f44336;
  animation: blink 0.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.title {
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

/* ========== 主内容区 ========== */
.widget-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
}

.main-icon {
  font-size: 64px;
  margin-bottom: 16px;
  transition: transform 0.3s ease;
}

.main-icon.pulse {
  animation: icon-pulse 0.8s ease-in-out infinite;
}

@keyframes icon-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* ========== 报警信息 ========== */
.alarm-message h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.sub-message {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.normal-message h3 {
  font-size: 20px;
  font-weight: 500;
  opacity: 0.9;
}

/* ========== 详情信息 ========== */
.details {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  min-width: 200px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item .icon {
  font-size: 16px;
}

.detail-item .label {
  opacity: 0.7;
  min-width: 50px;
}

.detail-item .value {
  font-weight: 500;
}

.detail-item .value.low-battery {
  color: #ffeb3b;
  font-weight: 700;
}

/* ========== 操作按钮 ========== */
.widget-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.btn:active {
  transform: translateY(0);
}

.btn-confirm {
  background: #4CAF50;
  color: white;
}

.btn-call {
  background: #2196F3;
  color: white;
}

.btn-location {
  background: #9C27B0;
  color: white;
}

/* ========== 响应式 ========== */
@media (max-width: 300px) {
  .main-icon {
    font-size: 48px;
  }
  
  .alarm-message h2 {
    font-size: 20px;
  }
  
  .widget-actions {
    flex-direction: column;
  }
}
```

### 3. JavaScript Tab

```javascript
(function() {
  var self = this;
  
  // ========== 配置变量 ==========
  var config = {
    dataKeys: {
      fallDetected: 'fall_detected',
      location: 'location',
      batteryLevel: 'battery_level'
    }
  };
  
  // ========== 初始化 ==========
  self.onInit = function() {
    initScope();
    initUI();
    console.log('Fall Detection Widget initialized');
  };
  
  function initScope() {
    var scope = self.ctx.$scope;
    var settings = self.ctx.settings;
    
    // 从设置读取配置
    scope.widgetTitle = settings.title || '跌倒监测';
    scope.showDetails = settings.showDetails !== false;
    scope.showActions = settings.showActions !== false;
    scope.enableCall = settings.enableCall === true;
    scope.enableLocation = settings.enableLocation !== false;
    
    // 按钮文本
    scope.confirmButtonText = settings.confirmButtonText || '确认';
    scope.callButtonText = settings.callButtonText || '呼叫';
    scope.locationButtonText = settings.locationButtonText || '查看位置';
    
    // 消息文本
    scope.alarmMessage = settings.alarmMessage || '检测到跌倒！';
    scope.subMessage = settings.subMessage || '请立即处理';
    scope.normalMessage = settings.normalMessage || '状态正常';
    
    // 初始化状态
    scope.isAlarm = false;
    scope.alarmLevel = 'normal';
    scope.statusIcon = '✓';
    scope.mainIcon = '👤';
    scope.location = null;
    scope.batteryLevel = null;
    scope.lastUpdate = null;
    
    // 绑定方法
    scope.confirmAlarm = confirmAlarm;
    scope.callEmergency = callEmergency;
    scope.viewLocation = viewLocation;
  }
  
  function initUI() {
    // 初始化 UI 状态
    updateUI();
  }
  
  // ========== 数据更新 ==========
  self.onDataUpdated = function() {
    try {
      var data = self.ctx.data;
      var scope = self.ctx.$scope;
      
      if (!data || data.length === 0) {
        console.warn('No data available');
        setNormalState();
        return;
      }
      
      // 解析数据
      var fallDetected = getBooleanValue(data, config.dataKeys.fallDetected);
      var location = getStringValue(data, config.dataKeys.location);
      var batteryLevel = getNumberValue(data, config.dataKeys.batteryLevel);
      
      // 更新 scope
      scope.location = location;
      scope.batteryLevel = batteryLevel;
      scope.lastUpdate = new Date();
      
      // 更新状态
      if (fallDetected) {
        setAlarmState();
      } else {
        setNormalState();
      }
      
      // 更新 UI
      updateUI();
      
    } catch (e) {
      console.error('Error in onDataUpdated:', e);
    }
  };
  
  // ========== 状态管理 ==========
  function setAlarmState() {
    var scope = self.ctx.$scope;
    scope.isAlarm = true;
    scope.alarmLevel = 'critical';
    scope.statusIcon = '⚠️';
    scope.mainIcon = '🆘';
    
    // 触发声音报警（如果启用）
    playAlarmSound();
  }
  
  function setNormalState() {
    var scope = self.ctx.$scope;
    scope.isAlarm = false;
    scope.alarmLevel = 'normal';
    scope.statusIcon = '✓';
    scope.mainIcon = '👤';
  }
  
  function updateUI() {
    // Angular 会自动更新 UI
    var scope = self.ctx.$scope;
    if (scope.$apply && !scope.$$phase) {
      scope.$apply();
    }
  }
  
  // ========== 数据获取辅助函数 ==========
  function getBooleanValue(data, keyName) {
    var value = getValue(data, keyName);
    if (value === null || value === undefined) return false;
    return value === true || value === 'true' || value === 1 || value === '1';
  }
  
  function getStringValue(data, keyName) {
    var value = getValue(data, keyName);
    return value !== null && value !== undefined ? String(value) : null;
  }
  
  function getNumberValue(data, keyName) {
    var value = getValue(data, keyName);
    if (value === null || value === undefined) return null;
    var num = Number(value);
    return isNaN(num) ? null : num;
  }
  
  function getValue(data, keyName) {
    if (!data || !keyName) return null;
    
    for (var i = 0; i < data.length; i++) {
      var item = data[i];
      if (item.dataKey && item.dataKey.name === keyName) {
        if (item.data && item.data.length > 0) {
          return item.data[0][0];  // 返回最新值
        }
      }
    }
    return null;
  }
  
  // ========== 操作处理 ==========
  function confirmAlarm() {
    console.log('Alarm confirmed');
    var scope = self.ctx.$scope;
    scope.isAlarm = false;
    updateUI();
    
    // 可以发送确认到服务器
    sendAction('CONFIRM_ALARM');
  }
  
  function callEmergency() {
    console.log('Calling emergency...');
    // 触发规则链动作
    sendAction('CALL_EMERGENCY');
  }
  
  function viewLocation() {
    console.log('Viewing location...');
    var scope = self.ctx.$scope;
    if (scope.location) {
      // 可以打开地图或发送事件
      sendAction('VIEW_LOCATION', { location: scope.location });
    }
  }
  
  function sendAction(actionType, params) {
    // 通过 ThingsBoard API 发送动作
    var $injector = self.ctx.$injector;
    var attributeService = $injector.get('attributeService');
    
    var entityId = self.ctx.entityId;
    if (entityId && entityId.id) {
      var attributes = [{
        key: 'lastAction',
        value: actionType
      }];
      
      attributeService.saveEntityAttributes(
        entityId,
        'SERVER_SCOPE',
        attributes
      ).subscribe(
        function() {
          console.log('Action sent:', actionType);
        },
        function(err) {
          console.error('Failed to send action:', err);
        }
      );
    }
  }
  
  function playAlarmSound() {
    // 检查是否启用声音
    var settings = self.ctx.settings;
    if (settings.enableSound === false) return;
    
    try {
      // 创建音频上下文播放提示音
      var AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      
      var ctx = new AudioContext();
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      osc.frequency.value = 800;
      osc.type = 'sine';
      
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
      
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
      console.warn('Could not play alarm sound:', e);
    }
  }
  
  // ========== 生命周期 ==========
  self.onResize = function() {
    // 响应尺寸变化
    var width = self.ctx.width;
    var height = self.ctx.height;
    
    // 可以在这里调整布局
    console.log('Widget resized:', width, 'x', height);
  };
  
  self.onDestroy = function() {
    // 清理资源
    console.log('Fall Detection Widget destroyed');
  };
  
})();
```

### 4. Settings Schema

```json
{
  "schema": {
    "type": "object",
    "title": "Settings",
    "properties": {
      "title": {
        "title": "Widget Title",
        "type": "string",
        "default": "跌倒监测"
      },
      "showDetails": {
        "title": "Show Details",
        "type": "boolean",
        "default": true
      },
      "showActions": {
        "title": "Show Action Buttons",
        "type": "boolean",
        "default": true
      },
      "enableCall": {
        "title": "Enable Call Button",
        "type": "boolean",
        "default": false
      },
      "enableLocation": {
        "title": "Enable Location Button",
        "type": "boolean",
        "default": true
      },
      "enableSound": {
        "title": "Enable Alarm Sound",
        "type": "boolean",
        "default": true
      },
      "alarmMessage": {
        "title": "Alarm Message",
        "type": "string",
        "default": "检测到跌倒！"
      },
      "subMessage": {
        "title": "Sub Message",
        "type": "string",
        "default": "请立即处理"
      },
      "normalMessage": {
        "title": "Normal Message",
        "type": "string",
        "default": "状态正常"
      },
      "confirmButtonText": {
        "title": "Confirm Button Text",
        "type": "string",
        "default": "确认"
      },
      "callButtonText": {
        "title": "Call Button Text",
        "type": "string",
        "default": "呼叫"
      },
      "locationButtonText": {
        "title": "Location Button Text",
        "type": "string",
        "default": "查看位置"
      },
      "appearance": {
        "title": "Appearance",
        "type": "object",
        "properties": {
          "normalColor": {
            "title": "Normal State Color",
            "type": "string",
            "default": "#667eea"
          },
          "alarmColor": {
            "title": "Alarm State Color",
            "type": "string",
            "default": "#ff416c"
          }
        }
      }
    },
    "required": ["title"]
  },
  "form": [
    "title",
    {
      "key": "appearance",
      "items": [
        {"key": "appearance.normalColor", "type": "color"},
        {"key": "appearance.alarmColor", "type": "color"}
      ]
    },
    [
      "showDetails",
      "showActions",
      "enableCall",
      "enableLocation",
      "enableSound"
    ],
    [
      "alarmMessage",
      "subMessage",
      "normalMessage"
    ],
    [
      "confirmButtonText",
      "callButtonText",
      "locationButtonText"
    ]
  ],
  "groupInfoes": [
    {"formIndex": 0, "GroupTitle": "Appearance"},
    {"formIndex": 1, "GroupTitle": "Features"},
    {"formIndex": 2, "GroupTitle": "Messages"},
    {"formIndex": 3, "GroupTitle": "Button Texts"}
  ]
}
```

---

## 🔧 使用说明

### 数据源配置

1. 在 Dashboard 中添加 Widget
2. 选择 **Alarm Widget** 类型
3. 配置数据源：
   - **Key**: `fall_detected` (Boolean)
   - **Key**: `location` (String)
   - **Key**: `battery_level` (Number)

### 设备遥测数据格式

```json
{
  "fall_detected": true,
  "location": "卧室",
  "battery_level": 85,
  "ts": 1711098735000
}
```

### 规则链集成

**创建规则链处理跌倒报警：**

```
[Message Type Switch]
    ↓ (POST_TELEMETRY)
[Script Filter: msg.fall_detected === true]
    ↓
[Create Alarm]
    ↓
[Send Notification]
```

**Script Filter:**
```javascript
return msg.fall_detected === true;
```

---

## ✅ 最佳实践总结

### 1. 组件设计原则

| 原则 | 说明 | 本案例应用 |
|------|------|-----------|
| **清晰的状态区分** | 正常/报警状态视觉差异明显 | 颜色渐变 + 动画 |
| **信息层级** | 重要信息突出显示 | 大图标 + 醒目标题 |
| **可操作性** | 报警时提供处理按钮 | 确认/呼叫/查看位置 |
| **容错性** | 无数据时优雅降级 | 显示"无数据"提示 |

### 2. 代码组织

- ✅ 使用 IIFE 避免全局污染
- ✅ 配置与逻辑分离
- ✅ 数据解析函数独立
- ✅ 错误处理完善

### 3. 性能优化

- ✅ 防抖处理频繁更新
- ✅ 避免重复 DOM 操作
- ✅ 资源及时清理

### 4. 用户体验

- ✅ 动画反馈增强感知
- ✅ 声音提示重要报警
- ✅ 响应式布局适配
- ✅ 可配置的外观和行为

---

## 📚 相关文档

- [ThingsBoard Widget 开发指南](./thingsboard-widget-development-guide.md)
- [ThingsBoard 官方文档](https://thingsboard.io/docs/)
- [AngularJS 模板语法](https://docs.angularjs.org/guide/templates)

---

*文档状态: 已完成 ✅*  
*最后更新: 2026-03-22*
