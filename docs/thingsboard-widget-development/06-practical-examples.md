# 第六章：完整实战示例

## 6.1 Latest Values 仪表盘 Widget

### 使用 gauge.js 库

**Resources/HTML:**
```html
<canvas id="my-gauge"></canvas>
```

**Resources/CSS:**
```css
#my-gauge {
    width: 100%;
    height: 100%;
}
```

**Resources（外部库）:**
```
https://bernii.github.io/gauge.js/dist/gauge.min.js
```

**JavaScript:**
```javascript
var canvasElement;
var gauge;

self.onInit = function() {
    canvasElement = $('#my-gauge', self.ctx.$container)[0];
    gauge = new Gauge(canvasElement);
    gauge.minValue = -1000;
    gauge.maxValue = 1000;
    gauge.animationSpeed = 16;
    self.onResize();
};

self.onResize = function() {
    canvasElement.width = self.ctx.width;
    canvasElement.height = self.ctx.height;
    gauge.update(true);
    gauge.render();
};

self.onDataUpdated = function() {
    if (self.ctx.defaultSubscription.data[0].data.length) {
        var value = self.ctx.defaultSubscription.data[0].data[0][1];
        gauge.set(value);
    }
};

self.onDestroy = function() {
    gauge = null;
};
```

## 6.2 Time Series 折线图 Widget

### 使用 Chart.js 库

**Resources/HTML:**
```html
<canvas id="myChart"></canvas>
```

**Resources（外部库）:**
```
https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js
```

**JavaScript:**
```javascript
var myChart;

self.onInit = function() {
    var chartData = {
        datasets: []
    };

    for (var i=0; i < self.ctx.data.length; i++) {
        var dataKey = self.ctx.data[i].dataKey;
        var dataset = {
            label: dataKey.label,
            data: [],
            borderColor: dataKey.color,
            fill: false
        };
        chartData.datasets.push(dataset);
    }

    var options = {
        maintainAspectRatio: false,
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                type: 'time',
                ticks: {
                    maxRotation: 0,
                    autoSkipPadding: 30
                }
            }]
        }
    };

    var canvasElement = $('#myChart', self.ctx.$container)[0];
    var canvasCtx = canvasElement.getContext('2d');
    myChart = new Chart(canvasCtx, {
        type: 'line',
        data: chartData,
        options: options
    });
    self.onResize();
};

self.onResize = function() {
    myChart.resize();
};

self.onDataUpdated = function() {
    for (var i = 0; i < self.ctx.data.length; i++) {
        var datasourceData = self.ctx.data[i];
        var dataSet = datasourceData.data;
        myChart.data.datasets[i].data.length = 0;
        var data = myChart.data.datasets[i].data;
        for (var d = 0; d < dataSet.length; d++) {
            var tsValuePair = dataSet[d];
            var ts = tsValuePair[0];
            var value = tsValuePair[1];
            data.push({t: ts, y: value});
        }
    }
    myChart.options.scales.xAxes[0].ticks.min = self.ctx.timeWindow.minTime;
    myChart.options.scales.xAxes[0].ticks.max = self.ctx.timeWindow.maxTime;
    myChart.update();
};
```

## 6.3 Control Widget - 开关控制

**Resources/HTML:**
```html
<div class="switch-container">
    <label class="switch">
        <input type="checkbox" id="power-switch">
        <span class="slider"></span>
    </label>
    <span id="status-text">OFF</span>
</div>
```

**Resources/CSS:**
```css
.switch-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 20px;
}

.switch {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 34px;
}

.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 34px;
}

.slider:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

input:checked + .slider {
    background-color: #2196F3;
}

input:checked + .slider:before {
    transform: translateX(26px);
}

#status-text {
    font-size: 24px;
    font-weight: bold;
}
```

**JavaScript:**
```javascript
self.onInit = function() {
    var switchEl = $('#power-switch', self.ctx.$container);
    var statusEl = $('#status-text', self.ctx.$container);
    
    switchEl.on('change', function() {
        var isOn = $(this).is(':checked');
        statusEl.text(isOn ? 'ON' : 'OFF');
        
        // 发送 RPC 命令
        var rpcRequest = {
            method: isOn ? 'turnOn' : 'turnOff',
            params: {}
        };
        
        self.ctx.controlApi.sendCommand(rpcRequest).subscribe(
            function(response) {
                console.log('Command success:', response);
            },
            function(error) {
                console.error('Command error:', error);
                // 回滚开关状态
                switchEl.prop('checked', !isOn);
                statusEl.text(!isOn ? 'ON' : 'OFF');
            }
        );
    });
};

self.onDataUpdated = function() {
    // 从设备状态更新开关
    if (self.ctx.data && self.ctx.data.length > 0) {
        var powerData = self.ctx.data.find(function(d) {
            return d.dataKey.name === 'power';
        });
        
        if (powerData && powerData.data.length > 0) {
            var isOn = powerData.data[powerData.data.length - 1][1];
            $('#power-switch', self.ctx.$container).prop('checked', isOn);
            $('#status-text', self.ctx.$container).text(isOn ? 'ON' : 'OFF');
        }
    }
};
```

## 6.4 Static Widget - HTML 卡片

**Resources/HTML:**
```html
<div class="info-card">
    <h2>设备状态</h2>
    <div class="status-item">
        <span class="label">在线设备:</span>
        <span class="value" id="online-count">--</span>
    </div>
    <div class="status-item">
        <span class="label">离线设备:</span>
        <span class="value" id="offline-count">--</span>
    </div>
</div>
```

**Resources/CSS:**
```css
.info-card {
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
}

.info-card h2 {
    margin: 0 0 16px 0;
    font-size: 20px;
}

.status-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.2);
}

.status-item:last-child {
    border-bottom: none;
}

.label {
    opacity: 0.8;
}

.value {
    font-weight: bold;
    font-size: 18px;
}
```

**Settings Schema:**
```json
{
    "schema": {
        "type": "object",
        "properties": {
            "cardTitle": {
                "title": "Card title",
                "type": "string",
                "default": "设备状态"
            },
            "bgColor": {
                "title": "Background color",
                "type": "string",
                "default": "#667eea"
            }
        }
    },
    "form": [
        "cardTitle",
        {
            "key": "bgColor",
            "type": "color"
        }
    ]
}
```

## 6.5 Alarm Widget - 告警列表

**Resources/HTML:**
```html
<div class="alarm-list">
    <div id="alarms-container"></div>
</div>
```

**Resources/CSS:**
```css
.alarm-list {
    padding: 10px;
    height: 100%;
    overflow-y: auto;
}

.alarm-item {
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border-left: 4px solid;
}

.alarm-item.CRITICAL {
    background: #fff2f0;
    border-left-color: #ff4d4f;
}

.alarm-item.MAJOR {
    background: #fff7e6;
    border-left-color: #faad14;
}

.alarm-item.MINOR {
    background: #e6f7ff;
    border-left-color: #1890ff;
}

.alarm-item.WARNING {
    background: #f6ffed;
    border-left-color: #52c41a;
}

.alarm-severity {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.alarm-severity.CRITICAL { background: #ff4d4f; color: white; }
.alarm-severity.MAJOR { background: #faad14; color: white; }
.alarm-severity.MINOR { background: #1890ff; color: white; }
.alarm-severity.WARNING { background: #52c41a; color: white; }

.alarm-title {
    font-weight: bold;
    margin-bottom: 4px;
}

.alarm-time {
    font-size: 12px;
    color: #666;
}
```

## 6.5 Alarm Widget - 完整代码

**Resources/HTML:**
```html
<div class="alarm-list" id="alarm-list"></div>
```

**Resources/CSS:**
```css
.alarm-list {
    padding: 10px;
    height: 100%;
    overflow-y: auto;
}

.alarm-item {
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border-left: 4px solid;
    cursor: pointer;
    transition: all 0.3s;
}

.alarm-item:hover {
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.alarm-item.CRITICAL {
    background: #fff2f0;
    border-left-color: #ff4d4f;
}

.alarm-item.MAJOR {
    background: #fff7e6;
    border-left-color: #faad14;
}

.alarm-item.MINOR {
    background: #e6f7ff;
    border-left-color: #1890ff;
}

.alarm-item.WARNING {
    background: #f6ffed;
    border-left-color: #52c41a;
}

.alarm-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.alarm-type {
    font-weight: bold;
    font-size: 14px;
}

.alarm-severity-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: bold;
    color: white;
}

.alarm-message {
    font-size: 13px;
    color: #333;
    margin-bottom: 4px;
}

.alarm-meta {
    font-size: 12px;
    color: #999;
}
```

**JavaScript:**
```javascript
self.onInit = function() {
    renderAlarmList();
};

self.onDataUpdated = function() {
    renderAlarmList();
};

function renderAlarmList() {
    var container = $('#alarm-list', ctx.$container);
    container.empty();
    
    if (!ctx.data || ctx.data.length === 0) {
        container.html('<div class="no-alarms">暂无告警</div>');
        return;
    }
    
    // 获取告警数据
    var alarms = ctx.data[0].data;
    
    // 按时间倒序排列
    alarms.sort(function(a, b) {
        return b[0] - a[0];
    });
    
    // 渲染每个告警
    alarms.forEach(function(alarm) {
        var alarmData = alarm[1];
        if (typeof alarmData === 'string') {
            alarmData = JSON.parse(alarmData);
        }
        
        var item = $('<div class="alarm-item"></div>');
        item.addClass(alarmData.severity || 'WARNING');
        
        item.html(
            '<div class="alarm-header">' +
                '<span class="alarm-type">' + (alarmData.type || '告警') + '</span>' +
                '<span class="alarm-severity-badge" style="background:' + getSeverityColor(alarmData.severity) + '">' +
                    (alarmData.severity || 'WARNING') +
                '</span>' +
            '</div>' +
            '<div class="alarm-message">' + (alarmData.message || '') + '</div>' +
            '<div class="alarm-meta">' +
                formatTime(alarm[0]) + ' | ' + (alarmData.device || '未知设备') +
            '</div>'
        );
        
        // 点击处理
        item.on('click', function() {
            handleAlarmClick(alarmData);
        });
        
        container.append(item);
    });
}

function getSeverityColor(severity) {
    var colors = {
        'CRITICAL': '#ff4d4f',
        'MAJOR': '#faad14',
        'MINOR': '#1890ff',
        'WARNING': '#52c41a'
    };
    return colors[severity] || '#999';
}

function formatTime(timestamp) {
    var date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

function handleAlarmClick(alarmData) {
    console.log('Alarm clicked:', alarmData);
    // 可以打开详情弹窗或执行其他操作
}
```

## 6.6 数据格式示例

### Latest Values 数据
```json
{
    "dataKey": {
        "name": "temperature",
        "label": "温度",
        "color": "#ff0000",
        "units": "°C"
    },
    "data": [
        [1647840000000, 25.5]
    ]
}
```

### Time Series 数据
```json
{
    "dataKey": { "name": "temperature", "label": "温度" },
    "data": [
        [1647836400000, 24.0],
        [1647837000000, 24.5],
        [1647837600000, 25.0]
    ]
}
```

### Alarm 数据
```json
{
    "id": "alarm-001",
    "severity": "CRITICAL",
    "type": "高温告警",
    "message": "设备温度超过阈值",
    "device": "Device-A",
    "time": 1647840000000
}
```

---

## 下一步

继续学习 [第七章：调试技巧](./07-debugging.md)
