# OpenClaw Memory System v3.1

> 双记忆系统的自动化工具层 - Python 重构版

## 简介

记忆管理系统是 OpenClaw 的自动化记忆管理工具，与双记忆系统互补协作。

**v3.1 更新**：Sessions 对话记录分离，优化搜索体验

## 功能特性

### v3.1 新特性
- 📄 **Sessions 分离存储** - 详细对话记录独立存放，可被 `memory_search` 搜索
- 🔍 **优化搜索体验** - `session-daily-*.md` 放在 `memory/` 目录下，支持全文检索
- 📊 **精简每日记忆** - `YYYY-MM-DD.md` 只保留 Sessions 统计摘要，减少冗余

### v3.0 特性
- 🐍 **Python 混合架构** - Bash 入口 + Python 核心，最佳实践
- 📦 **模块化设计** - 独立模块，易于维护和扩展
- 🔧 **智能配置** - JSON/YAML 双支持，容器友好
- 🧪 **完整测试** - 26 个单元测试，质量保证
- 📝 **详细文档** - 架构说明 + 使用指南

### 核心功能
- 📅 **每日归档** - 自动归档昨天，整理今天
- 💬 **Sessions 提取** - 自动提取对话记录，生成可搜索的日志
- 🔧 **记忆维护** - 每3天整理，每7天归档
- 📊 **智能报告** - 生成晨报，智能待办优先级
- 🏥 **健康检查** - 监控日记层/身份层/任务层
- 💾 **自动备份** - 每日+每周备份

## 快速开始

```bash
# 查看状态
bash run.sh status

# 生成晨报
bash run.sh report

# 健康检查
bash run.sh health

# 运行测试
bash run.sh test
```

## 系统架构

### 双记忆系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      双记忆系统架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  数据层 (双记忆系统)                  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  📁 memory/          🔥 self-improving/    📋 .learnings/ │
│  │  (日记层)            (身份层)              (任务层)     │
│  │  原始对话记录        用户偏好习惯          结构化学习   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              工具层 (记忆管理系统 v3.1)              │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  📊 读取分析 → 💬 Sessions提取 → 📈 生成报告        │   │
│  │       ↓              ↓                              │   │
│  │  📦 归档维护 → 💾 备份                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    输出层                            │   │
│  │  📁 reports/    📁 archive/    📁 .backup/         │   │
│  │  每日报告       归档文件        自动备份             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Sessions 对话记录存储 (v3.1)

```
memory/
├── 2026-03-15.md                    ← 每日记忆（精简版）
│   ├── 今日概要
│   ├── 关键事件
│   └── ### Sessions 统计            ← 只保留统计摘要
│       ├── Sessions 数量: 7
│       ├── 总消息数: 101
│       ├── Session 列表（ID + 摘要）
│       └── 📄 详细对话记录: 见 session-daily-2026-03-15.md
│
├── session-daily-2026-03-15.md      ← 详细对话记录（可搜索）✨ NEW
│   ├── # Sessions 对话记录
│   ├── ## Session: xxx
│   │   ├── ### 💬 详细对话记录
│   │   │   ├── **👤 用户**: ...
│   │   │   └── **🤖 助手**: ...
│   │   └── ### 📝 对话主题摘要
│   └── ...
│
└── INDEX.md                          ← 记忆索引
```

### v3.1 代码架构

```
openclaw-memory-system/
├── run.sh                          # Bash 入口脚本
├── memory_manager.py               # Python 核心调度
├── config.yaml                     # YAML 配置
├── config.json                     # JSON 配置
├── requirements.txt                # Python 依赖
├── modules/                        # 功能模块
│   ├── __init__.py
│   ├── reader.py                   # 数据读取模块
│   ├── reader_v3.py                # v3 读取增强
│   ├── analyzer.py                 # 分析提取模块
│   ├── reporter.py                 # 报告生成模块
│   ├── archiver.py                 # 归档维护模块
│   ├── health.py                   # 健康检查模块
│   ├── health_v3.py                # v3 健康检查
│   ├── session_extractor.py        # Sessions 提取器（原版）
│   ├── session_extractor_unified.py # Sessions 统一版（v3.1）
│   └── session_extractor_optimized.py # Sessions 优化版（v3.1）✨ NEW
└── tests/                          # 单元测试
    ├── test_analyzer.py
    ├── test_archiver.py
    ├── test_health.py
    └── run_tests.py
```

## 核心模块

| 模块 | 功能 | 文件 |
|------|------|------|
| **入口** | Bash 命令转发 | `run.sh` |
| **核心** | Python 命令调度 | `memory_manager.py` |
| **读取** | 读取双记忆数据 | `modules/reader.py` |
| **分析** | 分析提取内容 | `modules/analyzer.py` |
| **报告** | 生成晨报 | `modules/reporter.py` |
| **归档** | 归档维护 | `modules/archiver.py` |
| **健康** | 健康检查 | `modules/health.py` |
| **Sessions提取** | 提取对话记录（优化版） | `modules/session_extractor_optimized.py` |
| **Sessions统一** | 提取并合并到记忆 | `modules/session_extractor_unified.py` |

## 定时任务

| 任务名 | 频率 | 时间 | 功能 |
|--------|------|------|------|
| memory-daily | 每天4次 | 00:00, 06:00, 12:00, 18:00 | 增量归档 + Sessions提取 |
| memory-index | 每周1次 | 周一 01:00 | 生成索引 |
| memory-maintenance | 每天1次 | 02:00 | 维护整理 |
| memory-backup | 每天1次 | 03:00 | 自动备份 |
| memory-health | 每天1次 | 04:00 | 健康检查 |
| memory-report | 每天1次 | 08:00 | 生成晨报 |

### Sessions 提取说明 (v3.1)

`memory-daily` 任务现在会自动：

1. **归档记忆** - 归档昨天，整理今天
2. **提取 Sessions** - 从 `agents/main/sessions/*.jsonl` 提取对话
3. **生成详细日志** - 写入 `memory/session-daily-YYYY-MM-DD.md`
4. **记录统计摘要** - 写入 `memory/YYYY-MM-DD.md` 的 `### Sessions 统计` 部分

**输出文件**:
- `memory/YYYY-MM-DD.md` - 每日记忆（包含 Sessions 统计摘要）
- `memory/session-daily-YYYY-MM-DD.md` - 详细对话记录（可被 `memory_search` 搜索）

## 使用示例

### 查看 Sessions 对话记录

```bash
# 方法1: 直接读取文件
cat memory/session-daily-2026-03-15.md

# 方法2: 使用 memory_search 搜索（推荐）
# 在 OpenClaw 中执行：
memory_search("查找今天的对话记录")
```

### 搜索特定对话

```bash
# 搜索包含特定关键词的对话
memory_search("记忆搜索 session-daily")

# 搜索特定日期的对话
memory_search("2026-03-15 的 Sessions 对话")
```

### 手动执行 Sessions 提取

```bash
# 提取今天的 Sessions
python3 memory_manager.py session-merge --output log

# 提取指定日期
python3 memory_manager.py session-merge --date 2026-03-14 --output log

# 同时生成日志并合并到记忆
python3 memory_manager.py session-merge --output both
```

## 文档

- [架构说明](./DUAL_MEMORY_ARCHITECTURE.md) - 双记忆系统详细架构
- [GitHub 仓库](https://github.com/Junrui-L/openclaw-memory-system)

## 版本历史

### v3.1.1 (2026-03-15) - 健康检查修复
- ✅ **修复数据新鲜度检查** - 改为直接检查文件系统，不再依赖 TODO 状态的 search 方法
- ✅ **修复索引一致性检查** - 支持新的表格格式 INDEX.md
- ✅ **关键词提取优化** - 扩展关键词列表，添加聊天/进展/经验相关词汇
- ✅ **记忆文件清理** - 合并 9 个不规范命名文件，统一为 `YYYY-MM-DD.md` 格式
- ✅ **关键词去重机制** - 双重去重，避免重复追加到 MEMORY.md

### v3.1 (2026-03-15) - Sessions 对话记录优化
- 📄 **Sessions 分离存储** - 详细对话记录独立存放到 `session-daily-*.md`
- 🔍 **支持 memory_search** - `session-daily-*.md` 放在 `memory/` 目录，可被全文搜索
- 📊 **精简每日记忆** - `YYYY-MM-DD.md` 只保留 Sessions 统计摘要
- 💬 **优化对话格式** - 新增 `👤 用户` / `🤖 助手` 格式，更易阅读

### v3.0 (2026-03-14) - Python 重构版
- 🐍 采用 Python 混合架构（Bash + Python）
- 📦 模块化设计，独立功能模块
- 🔧 JSON/YAML 双配置支持
- 🧪 26 个单元测试完整覆盖
- 📚 详细架构文档

### v2.0 (2026-03-12) - 双记忆系统自动化工具层
- 📅 每日自动归档（00:00, 06:00, 12:00, 18:00）
- 🔧 记忆维护（每3天整理，每7天归档）
- 📊 智能晨报生成
- 🏥 三层健康检查（日记层/身份层/任务层）
- 💾 自动备份（每日+每周）
- ⏰ 6 个 Cron 定时任务
- 📡 HEARTBEAT 集成

### v1.0 (2026-03-09) - 初始版本
- 📝 基础记忆记录
- 🔍 简单搜索功能
- 📁 文件归档

## 许可证

MIT
