# 记忆管理系统 v2.0

> 双记忆系统的自动化工具层  
> 创建时间: 2026-03-12  
> 作者: 小牛牛

---

## 📋 系统概述

记忆管理系统是 OpenClaw 的自动化记忆管理工具，作为**双记忆系统的工具层**，与原有的记忆架构互补协作。

### 设计目标

- **自动化**: 自动归档、整理、生成报告
- **互补**: 不替代原有系统，而是增强
- **智能**: 智能待办优先级、增量归档
- **可视化**: 生成报告，直观查看状态

---

## 🏗️ 架构设计

### 双记忆架构关系

```
┌─────────────────────────────────────────────────────────┐
│                    双记忆系统（数据层）                   │
├─────────────────────────────────────────────────────────┤
│  📁 memory/          📁 self-improving/    📁 .learnings/ │
│  （日记-原始记录）    （身份-HOT/WARM/COLD） （任务-结构化） │
└─────────────────────────────────────────────────────────┘
                            ↓
              ┌─────────────────────────┐
              │   记忆管理系统 v2.0      │  ← 工具层
              │   （本系统）             │
              └─────────────────────────┘
                            ↓
              ┌─────────────────────────┐
              │   📁 reports/           │
              │   📁 archive/memory/    │
              │   📁 .backup/           │
              └─────────────────────────┘
```

### 系统组件

```
scripts/memory/
├── run.sh                    # Bash入口（定时任务调用）
├── memory_manager.py         # Python核心（命令调度）
├── config.yaml               # YAML配置
├── config.json               # JSON配置（备用）
├── requirements.txt          # Python依赖
└── modules/                  # 功能模块
    ├── __init__.py
    ├── reader.py             # 数据读取（双记忆系统）
    ├── analyzer.py           # 分析提取
    ├── reporter.py           # 报告生成
    ├── archiver.py           # 归档维护
    └── health.py             # 健康检查
```

---

## ⚙️ 配置说明

### 配置文件: `config.yaml`

```yaml
# 基础路径
paths:
  workspace: "/home/node/.openclaw/workspace"
  memory: "/home/node/.openclaw/workspace/memory"
  self_improving: "/home/node/.openclaw/workspace/self-improving"
  learnings: "/home/node/.openclaw/workspace/.learnings"
  memory_md: "/home/node/.openclaw/workspace/MEMORY.md"
  reports: "/home/node/.openclaw/workspace/reports"
  archive: "/home/node/.openclaw/workspace/archive"
  backup: "/home/node/.openclaw/workspace/.backup"
  positions: "/home/node/.openclaw/workspace/.positions"
  logs: "/home/node/.openclaw/workspace/logs"

# 归档配置
archive:
  retention_days: 7           # 7天后归档
  incremental: true           # 启用增量归档

# 备份配置
backup:
  enabled: true
  daily: true
  weekly: true
  retention_daily: 7
  retention_weekly: 4

# 通知配置
notification:
  feishu:
    enabled: false            # 默认关闭，需手动开启
    morning_report: true
    health_alert: true

# 智能待办
todo:
  smart_priority: true
  high_keywords: ["紧急", "重要", "critical", "urgent", "必须"]
  medium_keywords: ["建议", "todo", "应该", "需要"]
```

---

## 🚀 使用指南

### 命令列表

```bash
# 查看系统状态
bash scripts/memory/run.sh status

# 生成晨报
bash scripts/memory/run.sh report

# 健康检查
bash scripts/memory/run.sh health

# 每日归档
bash scripts/memory/run.sh daily

# 记忆维护
bash scripts/memory/run.sh maintenance

# 生成索引
bash scripts/memory/run.sh index

# 手动备份
bash scripts/memory/run.sh backup

# 执行全部任务
bash scripts/memory/run.sh all
```

### 定时任务配置

```bash
# 每日归档（多次运行）
0 0,6,12,18 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh daily

# 记忆维护（每天检查）
0 2 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh maintenance

# 生成日报（早上8点）
0 8 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh report

# 健康检查（凌晨4点）
0 4 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh health

# 自动备份（凌晨3点）
0 3 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh backup

# 生成索引（每周一）
0 1 * * 1 /home/node/.openclaw/workspace/scripts/memory/run.sh index
```

---

## 📊 功能详解

### 1. 每日归档 (daily)

**功能**:
- 归档昨天记忆（添加归档标记）
- 整理今天记忆（创建或追加）
- 继承昨天待办
- 防重复机制

**流程**:
```
1. 检查昨天是否已归档 → 跳过或归档
2. 读取昨天内容 → 提取待办
3. 创建/打开今天文件 → 继承待办
4. 添加归档标记
```

### 2. 记忆维护 (maintenance)

**功能**:
- 每3天：整理长期记忆 → MEMORY.md
- 每7天：归档旧记忆 → archive/memory/
- 自动判断执行条件

**流程**:
```
日期 % 3 == 0 → 整理长期记忆
日期 % 7 == 0 → 归档旧记忆
```

### 3. 报告生成 (report)

**功能**:
- 读取昨天记忆统计
- 统计学习记录
- 提取待办（按优先级分组）
- 生成智能建议

**输出**:
- `reports/daily/YYYY-MM-DD-morning.md`

### 4. 健康检查 (health)

**检查项**:
- 日记层：记忆文件数量
- 身份层：HOT记忆存在性
- 任务层：学习记录统计
- 磁盘空间：使用率
- 日志大小：大日志文件
- 备份：备份文件数量

**输出**:
- `reports/daily/YYYY-MM-DD-health.md`

### 5. 智能待办优先级

**优先级规则**:
- 🔴 高优先级：包含"紧急|重要|critical|urgent|必须"
- 🟡 中优先级：包含"建议|todo|应该|需要"
- 🟢 低优先级：其他

---

## 🔧 技术实现

### 混合架构

- **Bash入口**: `run.sh` - 简单的命令转发
- **Python核心**: `memory_manager.py` - 复杂的业务逻辑
- **优势**: 定时任务简单，功能强大灵活

### 模块设计

| 模块 | 职责 | 关键类/函数 |
|------|------|------------|
| reader | 读取双记忆系统数据 | MemoryReader |
| analyzer | 分析提取内容 | MemoryAnalyzer |
| reporter | 生成报告 | ReportGenerator |
| archiver | 归档维护 | Archiver |
| health | 健康检查 | HealthChecker |

### 依赖管理

```
PyYAML >= 6.0          # YAML配置
python-dateutil        # 日期处理
```

**容器内无pip处理**:
- 自动检测PyYAML，不存在则使用JSON配置
- 静默处理，不报错

---

## 📁 输出目录

```
workspace/
├── reports/
│   ├── daily/
│   │   ├── 2026-03-12-morning.md    # 晨报
│   │   └── 2026-03-12-health.md     # 健康报告
│   ├── weekly/                       # 周报（预留）
│   └── monthly/                      # 月报（预留）
├── archive/memory/
│   ├── 2026-03-01.md                 # 归档的记忆
│   └── README.md                     # 归档索引
└── .backup/
    ├── daily-20260312.tar.gz         # 每日备份
    └── weekly-20260310.tar.gz        # 每周备份
```

---

## 🎯 设计原则

### 1. 互补而非替代

- 不修改双记忆系统的数据
- 只读取、分析、生成报告
- 原有系统继续正常工作

### 2. 自动化优先

- 定时任务自动执行
- 智能判断执行条件
- 减少人工干预

### 3. 可配置

- YAML/JSON双配置支持
- 阈值可调
- 功能可开关

### 4. 健壮性

- 错误处理完善
- 依赖缺失降级
- 日志记录详细

---

## 📝 版本历史

### v2.0 (2026-03-12)

- ✅ 完整Python重构
- ✅ 混合架构（Bash + Python）
- ✅ 增量归档
- ✅ 智能待办优先级
- ✅ 健康检查
- ✅ 自动备份
- ✅ 互补双记忆系统

### v1.0 (2026-03-10 ~ 2026-03-11)

- Bash脚本版本
- 基础归档功能
- 简单日报生成

---

## 🔗 相关文档

- [双记忆架构指南](../memory-architecture-guide.md)
- [定时任务配置](../cron-tasks-config.md)
- [系统使用示例](./examples.md)

---

## 💡 使用建议

1. **首次运行**: 先执行 `run.sh status` 查看状态
2. **定时任务**: 复制 crontab 配置到宿主机
3. **飞书通知**: 修改 config.yaml 开启通知
4. **备份策略**: 默认每日+每周，可根据需要调整

---

*最后更新: 2026-03-12 11:47*  
*文档版本: v2.0*
