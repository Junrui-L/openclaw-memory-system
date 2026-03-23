# 第九章：实战项目 - 智能温控面板

## 9.1 项目需求

开发一个完整的智能温控面板 Widget：

| 功能 | 说明 |
|------|------|
| 显示当前温度 | 实时显示 |
| 显示目标温度 | 可调整 |
| 显示湿度 | 辅助信息 |
| 温度趋势图表 | 24小时历史 |
| 模式切换 | 制冷/制热/自动 |
| 开关控制 | 电源开关 |

## 9.2 数据模型

```typescript
// 设备遥测数据
interface TemperatureData {
    currentTemp: number;      // 当前温度
    targetTemp: number;       // 目标温度
    humidity: number;         // 湿度
    mode: 'cool' | 'heat' | 'auto';  // 模式
    power: boolean;           // 开关状态
}
```

## 9.3 Extension 组件完整代码

### TypeScript

```typescript
// temperature-panel.component.ts

import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { WidgetContext, Datasource } from '@shared/public-api';
import { Subscription } from 'rxjs';

@Component({
    selector: 'tb-temperature-panel',
    templateUrl: './temperature-panel.component.html',
    styleUrls: ['./temperature-panel.component.scss']
})
export class TemperaturePanelComponent implements OnInit, OnDestroy {
    
    @Input() ctx: WidgetContext;
    
    // 数据
    public currentTemp: number = 0;
    public targetTemp: number = 24;
    public humidity: number = 0;
    public mode: string = 'auto';
    public power: boolean = false;
    
    // 图表数据
    public chartData: any[] = [];
    
    // 订阅
    private subscription: Subscription;
    
    ngOnInit(): void {
        this.initializeData();
        this.subscribeToData();
    }
    
    ngOnDestroy(): void {
        if (this.subscription) {
            this.subscription.unsubscribe();
        }
    }
    
    // Widget 调用：数据更新
    public onDataUpdated(): void {
        this.updateFromContext();
    }
    
    private initializeData(): void {
        this.updateFromContext();
    }
    
    private updateFromContext(): void {
        if (!this.ctx.data) return;
        
        this.ctx.data.forEach(item => {
            const key = item.dataKey.name;
            const latestValue = item.data[item.data.length - 1]?.[1];
            
            switch(key) {
                case 'currentTemp':
                    this.currentTemp = latestValue;
                    break;
                case 'targetTemp':
                    this.targetTemp = latestValue;
                    break;
                case 'humidity':
                    this.humidity = latestValue;
                    break;
                case 'mode':
                    this.mode = latestValue;
                    break;
                case 'power':
                    this.power = latestValue;
                    break;
            }
        });
        
        // 更新图表数据
        this.updateChartData();
    }
    
    private updateChartData(): void {
        const tempData = this.ctx.data.find(d => d.dataKey.name === 'currentTemp');
        if (tempData) {
            this.chartData = tempData.data.map(([ts, val]) => ({
                time: new Date(ts),
                value: val
            }));
        }
    }
    
    private subscribeToData(): void {
        if (this.ctx.defaultSubscription) {
            this.subscription = this.ctx.defaultSubscription.data$.subscribe(() => {
                this.updateFromContext();
            });
        }
    }
    
    // 用户操作：调整目标温度
    public adjustTargetTemp(delta: number): void {
        this.targetTemp += delta;
        this.sendCommand('setTargetTemp', { value: this.targetTemp });
    }
    
    // 用户操作：切换模式
    public setMode(mode: string): void {
        this.mode = mode;
        this.sendCommand('setMode', { mode: mode });
    }
    
    // 用户操作：开关
    public togglePower(): void {
        this.power = !this.power;
        this.sendCommand(this.power ? 'turnOn' : 'turnOff');
    }
    
    // 发送 RPC 命令
    private sendCommand(method: string, params?: any): void {
        const request = {
            method: method,
            params: params || {}
        };
        
        this.ctx.controlApi.sendCommand(request).subscribe({
            next: (response) => console.log('Command success:', response),
            error: (err) => console.error('Command failed:', err)
        });
    }
}
```

### HTML 模板

```html
<!-- temperature-panel.component.html -->

<div class="temp-panel" [class.power-off]="!power">
    <!-- 头部：设备名称和开关 -->
    <div class="panel-header">
        <span class="device-name">{{ ctx.datasources[0]?.name }}</span>
        <button class="power-btn" [class.active]="power" (click)="togglePower()">
            <i class="icon-power"></i>
        </button>
    </div>
    
    <!-- 主显示区 -->
    <div class="panel-main">
        <div class="temp-display">
            <span class="current-temp">{{ currentTemp | number:'1.1-1' }}</span>
            <span class="temp-unit">°C</span>
        </div>
        <div class="temp-info">
            <span>目标: {{ targetTemp }}°C</span>
            <span>湿度: {{ humidity }}%</span>
        </div>
    </div>
    
    <!-- 温度调节 -->
    <div class="temp-control" *ngIf="power">
        <button (click)="adjustTargetTemp(-1)">-</button>
        <span>{{ targetTemp }}°C</span>
        <button (click)="adjustTargetTemp(1)">+</button>
    </div>
    
    <!-- 模式选择 -->
    <div class="mode-selector" *ngIf="power">
        <button [class.active]="mode === 'cool'" (click)="setMode('cool')">
            ❄️ 制冷
        </button>
        <button [class.active]="mode === 'heat'" (click)="setMode('heat')">
            🔥 制热
        </button>
        <button [class.active]="mode === 'auto'" (click)="setMode('auto')">
            🔄 自动
        </button>
    </div>
    
    <!-- 趋势图表 -->
    <div class="chart-container" *ngIf="power && chartData.length > 0">
        <div class="mini-chart">
            <div *ngFor="let point of chartData.slice(-20)" 
                 class="chart-bar"
                 [style.height.%]="(point.value / 40) * 100">
            </div>
        </div>
    </div>
</div>
```

### SCSS 样式

```scss
// temperature-panel.component.scss

.temp-panel {
    width: 100%;
    height: 100%;
    padding: 20px;
    box-sizing: border-box;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
    display: flex;
    flex-direction: column;
    
    &.power-off {
        background: #2c3e50;
        opacity: 0.8;
    }
    
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .device-name {
            font-size: 18px;
            font-weight: 500;
        }
        
        .power-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            background: rgba(255,255,255,0.2);
            cursor: pointer;
            transition: all 0.3s;
            
            &.active {
                background: #52c41a;
                box-shadow: 0 0 20px rgba(82, 196, 26, 0.5);
            }
        }
    }
    
    .panel-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        
        .temp-display {
            .current-temp {
                font-size: 72px;
                font-weight: bold;
            }
            .temp-unit {
                font-size: 24px;
            }
        }
        
        .temp-info {
            margin-top: 12px;
            display: flex;
            gap: 20px;
            opacity: 0.8;
        }
    }
    
    .temp-control {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 16px 0;
        
        button {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 20px;
            cursor: pointer;
            
            &:hover {
                background: rgba(255,255,255,0.3);
            }
        }
        
        span {
            font-size: 20px;
            font-weight: 500;
            min-width: 60px;
            text-align: center;
        }
    }
    
    .mode-selector {
        display: flex;
        gap: 12px;
        justify-content: center;
        
        button {
            padding: 8px 16px;
            border-radius: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            background: transparent;
            color: white;
            cursor: pointer;
            transition: all 0.3s;
            
            &.active {
                background: white;
                color: #667eea;
                border-color: white;
            }
        }
    }
    
    .chart-container {
        height: 60px;
        margin-top: 16px;
        
        .mini-chart {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            height: 100%;
            
            .chart-bar {
                flex: 1;
                margin: 0 2px;
                background: rgba(255,255,255,0.5);
                border-radius: 2px 2px 0 0;
                min-height: 5px;
            }
        }
    }
}
```

### Widget 中使用

**HTML:**
```html
<tb-temperature-panel [ctx]="ctx"></tb-temperature-panel>
```

**JavaScript:**
```javascript
self.onInit = function() {
    // 初始化完成
};

self.onDataUpdated = function() {
    if (self.ctx.$scope.temperaturePanelComponent) {
        self.ctx.$scope.temperaturePanelComponent.onDataUpdated();
    }
};

self.onResize = function() {
    // 处理尺寸变化
};

self.typeParameters = function() {
    return {
        maxDatasources: 1,
        singleEntity: true,
        previewWidth: '300px',
        previewHeight: '400px',
        embedTitlePanel: true
    };
};
```

---

## 下一步

继续学习 [第十章：最佳实践](./10-best-practices.md)