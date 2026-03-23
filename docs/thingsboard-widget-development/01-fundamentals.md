# 第一章：基础概念与 Widget 类型

## 1.1 什么是 ThingsBoard Widget？

Widget 是 ThingsBoard 仪表盘（Dashboard）中的**可复用 UI 模块**，用于：

- 📊 **数据可视化**（图表、仪表盘）
- 🎮 **远程设备控制**（按钮、开关）
- 🚨 **告警管理**
- 📝 **静态 HTML 内容展示**

## 1.2 五种 Widget 类型详解

| 类型 | 图标 | 用途 | 典型场景 |
|------|:----:|------|----------|
| **Latest values** | 📈 | 显示最新数值 | 温度仪表盘、实时状态卡片 |
| **Time series** | 📉 | 显示历史趋势 | 折线图、柱状图、趋势分析 |
| **Control widget** | 🎮 | 发送 RPC 命令 | 开关控制、参数调节 |
| **Alarm widget** | 🚨 | 告警展示 | 告警列表、告警统计 |
| **Static widget** | 📝 | 静态内容 | HTML 卡片、说明文字 |

### 详细说明

#### Latest values（最新值）
- 设计用于展示实体的最新属性值或时间序列数据点
- 使用实体属性或时间序列值作为数据源
- 示例：数字仪表盘显示当前温度

#### Time series（时间序列）
- 显示选定时间段的历史值，或特定时间窗口的最新值
- 仅使用时间序列值作为数据源
- 使用 Time window 设置指定显示值的时间范围
- 可以是 **Realtime**（动态变化的最新时间区间）或 **History**（固定历史时间区间）

#### Control widget（控制组件）
- 允许向设备发送 RPC 命令
- 处理和可视化设备回复
- 通过指定目标设备作为 RPC 命令的目标端点进行配置

#### Alarm widget（告警组件）
- 显示与指定实体相关的告警
- 配置参数：
  - **Alarm status**: 获取告警的状态
  - **Alarm severity**: 告警获取频率（秒）
  - **Alarm Type**: 告警主要来源标识

#### Static widget（静态组件）
- 显示静态可定制的 HTML 内容
- 不使用任何数据源
- 通常通过指定静态 HTML 内容和可选 CSS 样式进行配置

## 1.3 Widget 与 Dashboard 的关系

```
Dashboard (仪表盘)
    ├── Widget 1 (温度图表)
    ├── Widget 2 (设备开关)
    ├── Widget 3 (告警列表)
    └── ...
```

## 1.4 数据源类型

每个 Widget 类型有特定的数据源配置：

| 数据源类型 | 用途 | 适用 Widget |
|-----------|------|------------|
| **Alarm source** | 显示相关告警及字段 | Alarm widgets |
| **Alarms count** | 告警数量统计 | Latest values widgets |
| **Device** | 目标设备 + 时间序列键/属性名 | Time-series / Latest values |
| **Entities count** | 实体数量统计 | Latest values widgets |
| **Entity** | 通过 entity alias 选择目标实体 | Time-series / Latest values |
| **Function** | JavaScript 函数模拟数据 | 调试用途 |

## 1.5 Widget Bundles（组件包）

Widgets 按用途分组为 Widget Bundles：

- **系统级 Bundles**: 系统管理员管理，所有租户可用
- **租户级 Bundles**: 租户管理员管理，仅该租户及其客户可用

常见 Bundles：
- Air quality（空气质量）
- Alarm widgets（告警组件）
- Analog gauges（模拟仪表盘）
- Buttons（按钮）
- Cards（卡片）
- Charts（图表）
- Control widgets（控制组件）
- Maps（地图）
- Tables（表格）
- ...

---

## 下一步

继续学习 [第二章：Widget Editor 界面详解](./02-widget-editor.md)
