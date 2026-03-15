# 记忆管理系统 - 配置指南

> 详细配置说明和示例

---

## 配置文件位置

```
scripts/memory/
├── config.yaml          # 主配置（推荐）
└── config.json          # 备用配置（无PyYAML时使用）
```

---

## 完整配置示例

```yaml
# ========================================
# 基础路径配置
# ========================================
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

# ========================================
# 归档配置
# ========================================
archive:
  retention_days: 7           # 归档保留天数（超过此天数的文件会被归档）
  incremental: true           # 启用增量归档（只读取新增内容）
  compress: false             # 是否压缩归档文件（gzip）

# ========================================
# 备份配置
# ========================================
backup:
  enabled: true               # 启用自动备份
  daily: true                 # 启用每日备份
  weekly: true                # 启用每周备份
  retention_daily: 7          # 保留最近7个每日备份
  retention_weekly: 4         # 保留最近4个每周备份
  weekly_day: 0               # 周日进行周备份（0=周日，1=周一...）
  daily_hour: 3               # 每日备份时间（凌晨3点）

# ========================================
# 报告配置
# ========================================
reports:
  morning:
    enabled: true             # 启用晨报
    hour: 8                   # 生成时间（早上8点）
    send_feishu: false        # 发送到飞书（需配置飞书渠道）
    
  health:
    enabled: true             # 启用健康报告
    hour: 4                   # 检查时间（凌晨4点）
    send_alert: false         # 发送告警通知

# ========================================
# 通知配置
# ========================================
notification:
  feishu:
    enabled: false            # 启用飞书通知
    channel: "feishu"         # 飞书渠道名称
    morning_report: true      # 发送晨报
    health_alert: true        # 发送健康告警

# ========================================
# 智能待办配置
# ========================================
todo:
  smart_priority: true        # 启用智能优先级分析
  
  # 高优先级关键词（匹配任一即标记为高优先级）
  high_keywords:
    - "紧急"
    - "重要"
    - "critical"
    - "urgent"
    - "必须"
    - "立即"
    - "马上"
  
  # 中优先级关键词
  medium_keywords:
    - "建议"
    - "todo"
    - "应该"
    - "需要"
    - "考虑"
    - "推荐"

# ========================================
# 磁盘阈值配置
# ========================================
disk:
  warning: 80                 # 磁盘使用率警告阈值（%）
  critical: 90                # 磁盘使用率严重阈值（%）
  log_size_threshold: "100M"  # 日志文件大小阈值（超过则告警）

# ========================================
# 索引配置
# ========================================
index:
  enabled: true               # 启用自动索引
  max_keywords: 5             # 每篇记忆提取的关键词数量
  auto_generate: true         # 自动生成索引

# ========================================
# 日志配置
# ========================================
logging:
  level: "INFO"               # 日志级别（DEBUG/INFO/WARNING/ERROR）
  format: "[{timestamp}] {level}: {message}"
```

---

## 配置项说明

### paths（路径配置）

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| workspace | 工作区根目录 | /home/node/.openclaw/workspace |
| memory | 日记层目录 | workspace/memory |
| self_improving | 身份层目录 | workspace/self-improving |
| learnings | 任务层目录 | workspace/.learnings |
| reports | 报告输出目录 | workspace/reports |
| archive | 归档目录 | workspace/archive |
| backup | 备份目录 | workspace/.backup |

### archive（归档配置）

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| retention_days | 保留天数 | 7（一周） |
| incremental | 增量归档 | true |
| compress | 压缩归档 | false（如需节省空间可开启） |

### backup（备份配置）

| 配置项 | 说明 | 推荐值 |
|--------|------|--------|
| enabled | 启用备份 | true |
| daily | 每日备份 | true |
| weekly | 每周备份 | true |
| retention_daily | 每日备份保留数 | 7 |
| retention_weekly | 每周备份保留数 | 4 |

### todo（智能待办）

可自定义关键词匹配规则：

```yaml
todo:
  smart_priority: true
  high_keywords:
    - "紧急"
    - "重要"
    # 添加更多...
  medium_keywords:
    - "建议"
    # 添加更多...
```

---

## 环境特定配置

### 开发环境

```yaml
logging:
  level: "DEBUG"              # 更详细的日志

backup:
  enabled: false              # 开发环境可关闭备份

notification:
  feishu:
    enabled: false            # 开发环境不发送通知
```

### 生产环境

```yaml
logging:
  level: "INFO"

backup:
  enabled: true
  daily: true
  weekly: true

notification:
  feishu:
    enabled: true             # 生产环境开启通知
    morning_report: true
    health_alert: true
```

---

## 配置热加载

当前版本**不支持**热加载，修改配置后需要重启定时任务或手动执行命令生效。

---

*最后更新: 2026-03-12*
