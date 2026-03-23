# ThingsBoard 自定义组件开发 - 专题索引

> 📅 创建日期: 2026-03-21
> 📝 整理者: 小牛牛
> 
> **使用准则**: 记住文件路径，需要时查阅详细内容

---

## 📚 文档列表

| 序号 | 专题 | 文件路径 | 一句话摘要 |
|:----:|------|----------|-----------|
| 01 | 基础概念 | [`01-fundamentals.md`](./01-fundamentals.md) | 5种Widget类型、数据源类型 |
| 02 | Widget Editor | [`02-widget-editor.md`](./02-widget-editor.md) | 四大区域、工具栏、界面布局 |
| 03 | 生命周期与API | [`03-lifecycle-api.md`](./03-lifecycle-api.md) | onInit/onDataUpdated/onResize/onDestroy |
| 04 | Context对象 | [`04-context-object.md`](./04-context-object.md) | ctx.data/datasources/settings/timeWindow |
| 05 | Settings Schema | [`05-settings-schema.md`](./05-settings-schema.md) | JSON Schema、表单控件、条件显示 |
| 06 | 实战示例 | [`06-practical-examples.md`](./06-practical-examples.md) | gauge.js图表、Chart.js、开关控制 |
| 07 | 调试技巧 | [`07-debugging.md`](./07-debugging.md) | console.log、debugger、常见问题 |
| 08 | Extensions高级 | [`08-extensions-advanced.md`](./08-extensions-advanced.md) | Angular组件、打包部署、第三方库 |
| 09 | 实战项目-温控面板 | [`09-project-temperature-panel.md`](./09-project-temperature-panel.md) | 完整智能温控面板代码 |
| 10 | 最佳实践 | [`10-best-practices.md`](./10-best-practices.md) | 性能优化、内存管理、错误处理 |
| - | 🏆 最佳实践案例-跌倒告警 | [`case-study-fall-alarm.md`](./case-study-fall-alarm.md) | 完整案例分析+架构图 |
| - | 跌倒告警组件代码 | [`fall-alarm-widget.md`](./fall-alarm-widget.md) | Widget 完整代码 |

---

## 🗂️ 专题分类

### 基础篇
- [01-fundamentals.md](./01-fundamentals.md) - Widget 类型与数据源
- [02-widget-editor.md](./02-widget-editor.md) - Widget Editor 界面
- [03-lifecycle-api.md](./03-lifecycle-api.md) - 生命周期方法
- [04-context-object.md](./04-context-object.md) - ctx 对象
- [05-settings-schema.md](./05-settings-schema.md) - 配置系统

### 实战篇
- [06-practical-examples.md](./06-practical-examples.md) - 基础示例
- [fall-alarm-widget.md](./fall-alarm-widget.md) - 跌倒告警卡片 ⭐
- [09-project-temperature-panel.md](./09-project-temperature-panel.md) - 智能温控面板

### 进阶篇
- [07-debugging.md](./07-debugging.md) - 调试技巧
- [08-extensions-advanced.md](./08-extensions-advanced.md) - Extensions 开发
- [10-best-practices.md](./10-best-practices.md) - 最佳实践

---

## 🔍 快速查找

### 按需求查找

| 你想做什么 | 查看文档 |
|-----------|----------|
| 了解 Widget 类型 | [01-fundamentals.md](./01-fundamentals.md) |
| 熟悉开发界面 | [02-widget-editor.md](./02-widget-editor.md) |
| 获取数据/显示数据 | [04-context-object.md](./04-context-object.md) |
| 添加配置选项 | [05-settings-schema.md](./05-settings-schema.md) |
| 控制设备(RPC) | [04-context-object.md](./04-context-object.md) #rpc |
| 调试代码 | [07-debugging.md](./07-debugging.md) |
| 使用 Angular 开发 | [08-extensions-advanced.md](./08-extensions-advanced.md) |
| 优化性能 | [10-best-practices.md](./10-best-practices.md) |
| 参考完整代码 | [fall-alarm-widget.md](./fall-alarm-widget.md) |

### 按问题查找

| 遇到的问题 | 查看文档 |
|-----------|----------|
| 数据不更新 | [07-debugging.md](./07-debugging.md) #数据不更新 |
| 样式不生效 | [07-debugging.md](./07-debugging.md) #样式不生效 |
| 图表不显示 | [07-debugging.md](./07-debugging.md) #图表不显示 |
| RPC 调用失败 | [10-best-practices.md](./10-best-practices.md) #错误处理 |
| 内存泄漏 | [10-best-practices.md](./10-best-practices.md) #内存管理 |

---

## 📖 核心资源链接

- **官方文档**: https://thingsboard.io/docs/user-guide/contribution/widgets-development/
- **Extensions GitHub**: https://github.com/thingsboard/thingsboard-extensions
- **高级开发指南**: https://thingsboard.io/docs/user-guide/contribution/ui/advanced-development/

---

## 📝 学习记录

- [x] 2026-03-21: 完成基础概念学习
- [x] 2026-03-21: 完成 Widget Editor 界面学习
- [x] 2026-03-21: 完成生命周期与 API 学习
- [x] 2026-03-21: 完成 Context 对象学习
- [x] 2026-03-21: 完成 Settings Schema 学习
- [x] 2026-03-21: 开发跌倒告警卡片 Widget

---

*记住路径，随查随用*
