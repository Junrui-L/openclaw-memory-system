# ThingsBoard 自定义组件开发 - 完整学习文档

> 学习日期: 2026-03-21
> 学习者: 锐哥
> 整理者: 小牛牛

---

## 目录

1. [基础概念与 Widget 类型](./01-fundamentals.md)
2. [Widget Editor 界面详解](./02-widget-editor.md)
3. [Widget 生命周期与核心 API](./03-lifecycle-api.md)
4. [Context (ctx) 对象详解](./04-context-object.md)
5. [Settings Schema 配置系统](./05-settings-schema.md)
6. [完整实战示例](./06-practical-examples.md)
7. [调试技巧](./07-debugging.md)
8. [Extensions 高级开发](./08-extensions-advanced.md)
9. [实战项目 - 智能温控面板](./09-project-temperature-panel.md)
10. [最佳实践与注意事项](./10-best-practices.md)

---

## 学习路线图

```
Week 1: 基础 Widget
├── Day 1-2: 熟悉 Widget Editor
├── Day 3-4: 掌握 ctx 和数据获取
└── Day 5-7: 完成 2-3 个简单 Widget

Week 2: Extensions 入门
├── Day 1-2: 搭建开发环境
├── Day 3-4: 学习 Angular 组件基础
└── Day 5-7: 完成第一个 Extension

Week 3: 实战项目
├── Day 1-3: 设计复杂 Widget
├── Day 4-6: 开发实现
└── Day 7: 测试优化
```

---

## 核心资源

- **官方文档**: https://thingsboard.io/docs/user-guide/contribution/widgets-development/
- **Extensions GitHub**: https://github.com/thingsboard/thingsboard-extensions
- **高级开发指南**: https://thingsboard.io/docs/user-guide/contribution/ui/advanced-development/

---

## 快速参考

### Widget 5 种类型

| 类型 | 用途 | 数据源 |
|------|------|--------|
| Latest values | 显示最新数值 | Entity attributes / Time series |
| Time series | 显示历史趋势 | Time series only |
| Control widget | 设备控制 | RPC 命令 |
| Alarm widget | 告警展示 | Alarm source |
| Static widget | 静态内容 | 无数据源 |

### 生命周期方法

```javascript
self.onInit = function() { /* 初始化 */ };
self.onDataUpdated = function() { /* 数据更新 */ };
self.onResize = function() { /* 尺寸变化 */ };
self.onDestroy = function() { /* 销毁清理 */ };
```

### 核心 ctx 属性

```javascript
ctx.data              // 数据数组
ctx.datasources       // 数据源配置
ctx.defaultSubscription // 默认订阅
ctx.timeWindow        // 时间窗口
ctx.width/height      // Widget 尺寸
ctx.$container        // DOM 容器
ctx.settings          // Widget 设置
```

---

*最后更新: 2026-03-21*
