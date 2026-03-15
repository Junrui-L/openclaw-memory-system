# HEARTBEAT.md - 定时检查任务

> HEARTBEAT 频率: 每30分钟（默认）  
> 与定时任务关系: 互补检查，可同时触发  
> 更新日期: 2026-03-12

---

## 检查时机

HEARTBEAT 每30分钟触发一次，与定时任务时间关系：

| 时间 | HEARTBEAT | 定时任务 | 检查重点 |
|------|:---------:|----------|----------|
| 00:00 | ✅ | memory-daily | 检查归档是否完成 |
| 00:30 | ✅ | - | 一般检查 |
| 01:00 | ✅ | memory-index(周一) | 检查索引生成 |
| 01:30 | ✅ | - | 一般检查 |
| 02:00 | ✅ | memory-maintenance | 检查维护执行 |
| 02:30 | ✅ | - | 一般检查 |
| 03:00 | ✅ | memory-backup | 检查备份完成 |
| 03:30 | ✅ | - | 一般检查 |
| 04:00 | ✅ | memory-health | 检查健康报告 |
| 04:30 | ✅ | - | 一般检查 |
| 06:00 | ✅ | memory-daily | 检查归档是否完成 |
| 06:30 | ✅ | - | 一般检查 |
| 08:00 | ✅ | memory-report | 检查晨报生成 |
| 08:30 | ✅ | - | 一般检查 |
| 12:00 | ✅ | memory-daily | 检查归档是否完成 |
| 12:30 | ✅ | - | 一般检查 |
| 18:00 | ✅ | memory-daily | 检查归档是否完成 |
| 18:30 | ✅ | - | 一般检查 |

---

## 检查清单

### 1. 记忆文件更新检查 ⭐ 核心

**触发**: 每次 HEARTBEAT
**执行**:
```bash
bash scripts/memory/run.sh daily
```

**检查内容**:
- 今天记忆文件是否存在
- 最后更新时间是否在1小时内
- 如果超过1小时未更新，提醒用户

### 2. 定时任务执行状态检查

**触发**: 与定时任务同时触发时
**检查内容**:
- 定时任务是否成功执行
- 报告文件是否生成（`reports/daily/YYYY-MM-DD-*.md`）
- 是否有错误日志

### 3. 系统健康检查

**触发**: 每天2-4次
**执行**:
```bash
bash scripts/memory/run.sh health
```

---

## 响应规则

### 如果记忆文件超过1小时未更新

**动作**:
1. 执行 `bash scripts/memory/run.sh daily`
2. 提醒用户："今天记忆文件已更新"

### 如果定时任务未生成预期文件

**动作**:
1. 检查日志文件 `logs/cron-*.log`
2. 手动执行对应任务
3. 报告问题

### 如果有健康告警

**动作**:
1. 显示告警内容
2. 建议查看详细报告 `reports/daily/YYYY-MM-DD-health.md`

---

## 与定时任务的关系

> **设计原则**: HEARTBEAT 和定时任务互补，不是替代
> 
> - **定时任务**: 精确时间执行具体功能（归档、报告、备份等）
> - **HEARTBEAT**: 定期检查状态，发现问题，补充执行

### 两者同时触发时

```
时间: 00:00
├── 定时任务: memory-daily 执行归档
└── HEARTBEAT: 检查归档结果
    └── 如果未生成文件 → 补充执行
```

**不冲突原因**:
- 定时任务优先执行功能
- HEARTBEAT 检查执行结果
- 可并行执行，互不干扰

---

## 关键命令

```bash
# 立即执行每日归档
bash scripts/memory/run.sh daily

# 生成报告
bash scripts/memory/run.sh report

# 健康检查
bash scripts/memory/run.sh health

# 查看状态
bash scripts/memory/run.sh status
```

---

## 文档

- [记忆系统文档](docs/memory-system/README.md)
- [配置说明](docs/memory-system/CONFIG.md)
- [定时任务配置](docs/memory-system/CRON.md)
- [GitHub 仓库](https://github.com/Junrui-L/openclaw-memory-system)

---

## 定时任务完整列表

| 任务名 | 频率 | 时间 | 功能 |
|--------|------|------|------|
| memory-daily | 每天4次 | 00:00, 06:00, 12:00, 18:00 | 增量归档，整理今天 |
| memory-index | 每周1次 | 周一 01:00 | 生成索引 |
| memory-maintenance | 每天1次 | 02:00 | 每3天整理，每7天归档 |
| memory-backup | 每天1次 | 03:00 | 自动备份 |
| memory-health | 每天1次 | 04:00 | 健康检查 |
| memory-report | 每天1次 | 08:00 | 生成晨报 |

---

*最后更新: 2026-03-12 13:56*  
*方案: 保持默认30分钟，与定时任务互补*
