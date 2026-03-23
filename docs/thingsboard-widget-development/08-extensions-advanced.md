# 第八章：ThingsBoard Extensions 高级开发

## 8.1 Extensions 架构原理

```
┌─────────────────────────────────────────────────────────────┐
│                  ThingsBoard UI (Angular)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Widget Container                        │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │         Your Extension Component             │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │   │
│  │  │  │  TS逻辑  │  │ Angular │  │  第三方  │     │   │   │
│  │  │  │  代码   │  │ 模板    │  │  库     │     │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘     │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↑
                    通过 Widget API 通信
                              ↑
┌─────────────────────────────────────────────────────────────┐
│              ThingsBoard Extension Project                  │
│         (Angular + TypeScript + Webpack 打包)               │
└─────────────────────────────────────────────────────────────┘
```

## 8.2 开发环境搭建

### 系统要求
- Node.js >= 20.20.0
- Yarn >= 1.22.22 (Yarn Classic)

### 初始化步骤

```bash
# 1. 克隆仓库
git clone https://github.com/thingsboard/thingsboard-extensions.git
cd thingsboard-extensions

# 2. 安装依赖
yarn install

# 3. 启动开发服务器
yarn start
# 服务运行在 http://localhost:5000
```

## 8.3 项目结构

```
thingsboard-extensions/
├── src/
│   ├── app/
│   │   ├── components/           # 自定义组件
│   │   │   └── example-table/
│   │   │       ├── example-table.component.ts
│   │   │       ├── example-table.component.html
│   │   │       └── example-table.component.scss
│   │   └── app.module.ts         # Angular 模块配置
│   └── index.ts                  # 入口文件
├── examples/                     # 官方示例
│   ├── example-table/
│   ├── example-chart/
│   ├── example-table-with-custom-settings/
│   └── ...
├── package.json
├── tsconfig.json
└── webpack.config.js
```

## 8.4 核心依赖导入

ThingsBoard 提供了模块映射，可以导入核心功能：

```typescript
// 从 ThingsBoard 核心模块导入
import { 
    WidgetConfig,           // Widget 配置
    Datasource,             // 数据源
    DataKey,                // 数据键
    EntityId                // 实体ID
} from '@shared/public-api';

import { 
    UtilsService,           // 工具服务
    DatePipe               // 日期管道
} from '@core/public-api';

// 完整可导入模块列表：
// @app/*, @core/*, @shared/*, @modules/*, @home/*
```

## 8.5 创建一个完整的 Extension 组件

### 步骤 1：创建组件文件

```typescript
// src/app/components/my-widget/my-widget.component.ts

import { Component, Input, OnInit } from '@angular/core';
import { WidgetContext } from '@shared/public-api';

@Component({
    selector: 'tb-my-widget',
    templateUrl: './my-widget.component.html',
    styleUrls: ['./my-widget.component.scss']
})
export class MyWidgetComponent implements OnInit {
    
    // 接收 Widget 上下文
    @Input() ctx: WidgetContext;
    
    // 组件内部数据
    public currentValue: number = 0;
    public deviceName: string = '';
    
    ngOnInit(): void {
        // 初始化
        this.deviceName = this.ctx.datasources[0]?.name || 'Unknown';
        this.updateData();
    }
    
    // 数据更新方法（Widget 会调用）
    public onDataUpdated(): void {
        this.updateData();
    }
    
    private updateData(): void {
        // 从 ctx 获取最新数据
        if (this.ctx.data && this.ctx.data.length > 0) {
            const data = this.ctx.data[0].data;
            if (data.length > 0) {
                // 获取最新值 [timestamp, value]
                this.currentValue = data[data.length - 1][1];
            }
        }
    }
    
    // 发送 RPC 命令（控制设备）
    public sendCommand(command: string, params?: any): void {
        const rpcRequest = {
            method: command,
            params: params || {}
        };
        
        this.ctx.controlApi.sendCommand(rpcRequest).subscribe(
            (response) => {
                console.log('RPC success:', response);
            },
            (error) => {
                console.error('RPC error:', error);
            }
        );
    }
}
```

### 步骤 2：创建模板

```html
<!-- src/app/components/my-widget/my-widget.component.html -->

<div class="my-widget-container">
    <!-- 标题 -->
    <div class="widget-header">
        <h3>{{ deviceName }}</h3>
    </div>
    
    <!-- 数据显示 -->
    <div class="widget-content">
        <div class="value-display">
            <span class="value">{{ currentValue | number:'1.2-2' }}</span>
            <span class="unit">{{ ctx.data[0]?.dataKey?.units || '' }}</span>
        </div>
    </div>
    
    <!-- 控制按钮 -->
    <div class="widget-controls">
        <button (click)="sendCommand('turnOn')">开启</button>
        <button (click)="sendCommand('turnOff')">关闭</button>
    </div>
</div>
```

### 步骤 3：添加样式

```scss
/* src/app/components/my-widget/my-widget.component.scss */

.my-widget-container {
    width: 100%;
    height: 100%;
    padding: 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    
    .widget-header {
        h3 {
            margin: 0 0 12px 0;
            font-size: 16px;
            color: #333;
        }
    }
    
    .widget-content {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .value-display {
            text-align: center;
            
            .value {
                font-size: 48px;
                font-weight: bold;
                color: #1890ff;
            }
            
            .unit {
                font-size: 24px;
                color: #666;
                margin-left: 8px;
            }
        }
    }
    
    .widget-controls {
        display: flex;
        gap: 12px;
        justify-content: center;
        
        button {
            padding: 8px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            background: #1890ff;
            color: white;
            
            &:hover {
                background: #40a9ff;
            }
        }
    }
}
```

### 步骤 4：注册组件

```typescript
// src/app/app.module.ts

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MyWidgetComponent } from './components/my-widget/my-widget.component';

@NgModule({
    declarations: [
        MyWidgetComponent
    ],
    imports: [
        CommonModule
    ],
    exports: [
        MyWidgetComponent
    ]
})
export class AppModule { }
```

### 步骤 5：导出组件

```typescript
// src/index.ts

export * from './app/components/my-widget/my-widget.component';
```

## 8.6 打包与部署

```bash
# 开发模式（热更新）
yarn start

# 生产打包
yarn build

# 输出文件
# target/generated-resources/thingsboard-extension-widgets.js
```

### 部署到 ThingsBoard

1. 进入 **Resources → JavaScript library**
2. 点击 **+** 添加资源
3. **JavaScript type**: 选择 `Extension`
4. **Title**: 输入扩展名称
5. **上传文件**: 选择打包后的 JS 文件
6. 点击 **Add**

## 8.7 在 Widget 中使用 Extension

### Widget Resources 配置

1. 进入 Widget Editor → Resources tab
2. 点击 Add
3. 勾选 "Is extension"
4. 选择已上传的 Extension

### Widget HTML

```html
<tb-my-widget [ctx]="ctx"></tb-my-widget>
```

### Widget JavaScript

```javascript
self.onInit = function() {
    // 初始化完成
};

self.onDataUpdated = function() {
    // 通知组件数据更新
    if (self.ctx.$scope.myWidgetComponent) {
        self.ctx.$scope.myWidgetComponent.onDataUpdated();
    }
};

self.onResize = function() {
    // 处理尺寸变化
};

// Widget 行为配置
self.typeParameters = function() {
    return {
        maxDatasources: 1,      // 最大数据源数量
        singleEntity: true,     // 只允许单个实体
        previewWidth: '300px',  // 预览宽度
        previewHeight: '200px', // 预览高度
        embedTitlePanel: true,  // 隐藏标题面板
    };
};
```

## 8.8 Extensions 优势对比

| 特性 | 原生 Widget | Extensions |
|------|------------|------------|
| 开发语言 | JavaScript | TypeScript |
| 框架支持 | 无 | Angular + RXJS |
| 代码复用 | 困难 | 容易 |
| 复杂度 | 适合简单逻辑 | 适合复杂业务 |
| 第三方库 | 手动引入 | npm 安装 |
| 类型检查 | 无 | 强类型 |
| IDE 支持 | 有限 | 完整 |

## 8.9 官方示例

thingsboard-extensions 仓库提供了多个示例：

| 示例 | 路径 | 说明 |
|------|------|------|
| example-table | `examples/example-table` | 基础表格组件 |
| example-chart | `examples/example-chart` | ECharts 集成 |
| example-table-with-custom-settings | `examples/example-table-with-custom-settings` | 自定义设置 |
| example-table-with-custom-subscription | `examples/example-table-with-custom-subscription` | 自定义数据订阅 |
| example-of-using-third-party-library | `examples/example-of-using-third-party-library` | 第三方库使用 |
| example-action | `examples/example-action` | 自定义动作 |

## 8.10 第三方库集成

```bash
# 安装第三方库
yarn add lodash
yarn add @angular/material
yarn add echarts
```

```typescript
// 在组件中使用
import * as _ from 'lodash';
import * as echarts from 'echarts';

@Component({...})
export class ChartWidgetComponent {
    
    processData(data: any[]) {
        // 使用 lodash
        return _.groupBy(data, 'category');
    }
    
    initChart() {
        // 使用 echarts
        const chart = echarts.init(this.chartElement);
        chart.setOption({...});
    }
}
```
