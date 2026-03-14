# OpenClaw Memory System v2.0

> 双记忆系统的自动化工具层

## 简介

记忆管理系统是 OpenClaw 的自动化记忆管理工具，与双记忆系统互补协作。

## 功能特性

- 📅 **每日归档** - 自动归档昨天，整理今天
- 🔧 **记忆维护** - 每3天整理，每7天归档
- 📊 **智能报告** - 生成晨报，智能待办优先级
- 🏥 **健康检查** - 监控日记层/身份层/任务层
- 💾 **自动备份** - 每日+每周备份

## 快速开始

```bash
# 查看状态
bash scripts/memory/run.sh status

# 生成晨报
bash scripts/memory/run.sh report

# 健康检查
bash scripts/memory/run.sh health
```

## 文档

- [详细文档](https://gist.github.com/Junrui-L/61b1041778b2f1e3c21fc00ade129c41)

## 架构

```
scripts/memory/
├── run.sh              # Bash入口
├── memory_manager.py   # Python核心
├── config.yaml         # 配置文件
└── modules/            # 功能模块
    ├── reader.py       # 数据读取
    ├── analyzer.py     # 分析提取
    ├── reporter.py     # 报告生成
    ├── archiver.py     # 归档维护
    └── health.py       # 健康检查
```

## 许可证

MIT
