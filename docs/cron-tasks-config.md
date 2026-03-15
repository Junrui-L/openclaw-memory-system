# OpenClaw 定时任务配置文档

> 记录 OpenClaw 定时任务的配置详情
> 最后更新: 2026-03-12

---

## 📋 概述

OpenClaw 使用内置的 Cron 调度器管理定时任务，所有任务配置存储在 `/home/node/.openclaw/cron/jobs.json`。

---

## ⏰ 定时任务列表

当前共有 **2 个定时任务**在运行：

### 任务 1: daily-memory-archive（每日记忆归档）

| 属性 | 值 |
|------|-----|
| **ID** | `28d002b4-3003-4ec5-9a85-1086b3f7511a` |
| **名称** | daily-memory-archive |
| **执行时间** | 每天 00:30 |
| **Cron 表达式** | `30 0 * * *` |
| **执行脚本** | `memory-maintenance.sh && generate-daily-report.sh` |
| **目标 Agent** | main |
| **状态** | ✅ 已启用 |
| **发送目标** | 飞书聊天 `oc_f55bc4b692dd99d18ba8b46d73e902cb` |

**功能说明**:
- 运行记忆维护脚本（每3天整理长期记忆，每7天归档旧记忆）
- 生成每日报告（简洁版）
- 发送归档完成通知到飞书

**消息模板**:
```
✅ 每日记忆归档完成

📅 日期: YYYY-MM-DD
📝 记忆文件: memory/YYYY-MM-DD.md
⏰ 归档时间: 00:30

📊 昨日记忆摘要
📈 学习统计
⏰ 待办提醒

📌 归档状态: 已完成
🔄 下次归档: 明日 00:30
```

---

### 任务 2: daily-memory-report（每日记忆报告）

| 属性 | 值 |
|------|-----|
| **ID** | `995f7f3e-a8f5-49d5-b845-b9b5eda238dc` |
| **名称** | daily-memory-report |
| **执行时间** | 每天 08:00 |
| **Cron 表达式** | `0 8 * * *` |
| **执行脚本** | `generate-morning-report.sh` |
| **目标 Agent** | main |
| **状态** | ✅ 已启用 |
| **发送目标** | 飞书聊天 `oc_f55bc4b692dd99d18ba8b46d73e902cb` |

**功能说明**:
- 生成早上问候版日报
- 包含昨日回顾、学习统计、待办提醒
- 智能生成今日建议
- 发送祝福到飞书

**消息模板**:
```
🌅 早上好！今日记忆日报

📅 日期: YYYY-MM-DD
📝 昨日记忆: memory/YYYY-MM-DD.md
⏰ 报告时间: 08:00

☀️ 早安！新的一天开始了

📊 昨日回顾
📄 记忆文件: XXX 行
📝 关键事件: XX 项
昨日亮点:
• ...

📈 学习统计
❌ 错误记录: X
📖 学习记录: X
💭 功能请求: X
💡 昨日共记录 X 条学习

⏰ 今日待办
共 X 项待办:
• ...

🎯 今日建议
• ...

💪 祝你今天工作顺利！

---
*日报生成时间: 08:00*
*下次报告: 明日 08:00*
```

---

## 📁 相关文件

### 配置文件
| 文件路径 | 说明 |
|----------|------|
| `/home/node/.openclaw/cron/jobs.json` | 定时任务主配置 |
| `/home/node/.openclaw/cron/` | Cron 数据目录 |

### 执行脚本
| 脚本路径 | 说明 |
|----------|------|
| `/home/node/.openclaw/workspace/scripts/memory-maintenance.sh` | 记忆维护（每3天整理/每7天归档）|
| `/home/node/.openclaw/workspace/scripts/generate-daily-report.sh` | 生成每日报告（简洁版）|
| `/home/node/.openclaw/workspace/scripts/generate-morning-report.sh` | 生成早上日报（问候版）|

---

## 🔧 管理命令

```bash
# 查看定时任务状态
openclaw cron status

# 列出所有定时任务
openclaw cron list

# 添加新定时任务
openclaw cron add --name "任务名" --schedule "0 8 * * *" --target main

# 删除定时任务
openclaw cron rm <任务ID>

# 立即运行某个任务（调试用）
openclaw cron run <任务ID>

# 查看运行历史
openclaw cron runs

# 启用/禁用任务
openclaw cron enable <任务ID>
openclaw cron disable <任务ID>
```

---

## 📝 配置格式

### Cron 表达式
```
分 时 日 月 周
│  │  │  │  │
│  │  │  │  └── 星期 (0-6, 0=周日)
│  │  │  └──── 月份 (1-12)
│  │  └────── 日期 (1-31)
│  └──────── 小时 (0-23)
└────────── 分钟 (0-59)
```

### 示例
| 表达式 | 说明 |
|--------|------|
| `0 8 * * *` | 每天 8:00 |
| `30 0 * * *` | 每天 0:30 |
| `0 2 */3 * *` | 每3天 2:00 |
| `0 3 * * 0` | 每周日 3:00 |

---

## 🔄 修改历史

| 日期 | 修改内容 | 操作人 |
|------|----------|--------|
| 2026-03-12 | 将 daily-memory-report 脚本从 `daily-memory-report.sh` 改为 `generate-morning-report.sh` | 锐哥 |
| 2026-03-12 | 创建本文档 | 锐哥 |

---

## 📌 注意事项

1. **任务状态**: 两个任务都已启用，运行正常
2. **发送目标**: 都发送到同一个飞书聊天
3. **日志位置**: 任务执行日志在 `~/.openclaw/workspace/logs/`
4. **备份**: 修改配置前建议备份 `jobs.json`

---

*文档版本: 1.0*
*最后更新: 2026-03-12 02:25*
