# OpenClaw 记忆架构配置指南

> 本文档指导如何配置和管理 OpenClaw Agent 的三层记忆系统

---

## 📋 目录

1. [架构概述](#架构概述)
2. [三层记忆系统](#三层记忆系统)
3. [自动维护配置](#自动维护配置)
4. [手动操作指南](#手动操作指南)
5. [故障排除](#故障排除)

---

## 架构概述

OpenClaw 采用**三层分级记忆系统**，确保对话连续性、历史可追溯性和知识持久化。

```
┌─────────────────────────────────────────────────────────────┐
│                      记忆系统架构                            │
├─────────────────────────────────────────────────────────────┤
│  🔥 HOT (热数据)        📝 DAILY (日数据)      🧠 LONG (长期) │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐  │
│  │ 活跃模式    │      │ 每日记录    │      │ 核心档案    │  │
│  │ 实时更新    │      │ 自动归档    │      │ 定时整理    │  │
│  │ ≤100行     │      │ 永久保留    │      │ 跨会话保留  │  │
│  └─────────────┘      └─────────────┘      └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 三层记忆系统

### 1. 🔥 HOT - 热数据（高频访问）

**存储位置：** `~/workspace/self-improving/memory.md`

**用途：**
- 当前活跃的模式和偏好
- 最近学习的有效策略
- 待办事项和提醒
- 临时笔记（≤100行）

**更新频率：** 实时（对话中即时写入）

**触发条件：**
- 用户明确说"记住这个"
- 重要配置变更
- 新技能安装
- 用户偏好表达（"我喜欢..."）

**示例内容：**
```markdown
- 用户喜欢直接、高效的沟通方式
- 偏好飞书作为消息渠道
- 待办：2026-03-10 15:00 聚餐提醒
- 有效模式：配置变更后重启网关生效
```

---

### 2. 📝 DAILY - 日数据（历史记录）

**存储位置：** `~/workspace/memory/YYYY-MM-DD.md`

**用途：**
- 每日完整对话记录
- 技术操作日志
- 系统配置变更
- 重要事件时间线

**更新机制：**
- **实时追加：** 对话过程中即时写入
- **自动归档：** 每天午夜 00:00 创建新文件

**文件命名：** `2026-03-10.md`

**示例结构：**
```markdown
# 2026-03-10 周二

## 今日概要
- 日期: 2026-03-10
- 主要事件: 配置记忆系统

## 技术配置
- 配置自动每日记忆归档
- 设置定时维护任务

## 对话记录
### 01:53
用户配置自动记忆维护：
- 每3天整理长期记忆
- 每7天归档旧记忆
```

---

### 3. 🧠 LONG-TERM - 长期记忆（核心档案）

**存储位置：** `~/workspace/self-improving/long-term-memory.md`

**用途：**
- 用户档案（姓名、地点、时区、偏好）
- 关系历史（首次见面、重要事件）
- 技术配置（渠道、技能、模型）
- 学习积累（有效模式、经验教训）

**更新频率：** 每3天自动整理

**维护机制：**
- 从 DAILY 记忆提取关键信息
- 手动审核和整理
- 跨会话持久化

**标准结构：**
```markdown
# Agent 名称 - 长期记忆档案

## 👤 用户档案
- **姓名**: 用户名
- **地点**: 城市
- **时区**: UTC+8
- **首次见面**: 日期

## 🛠️ 已配置系统
### 渠道
- ✅ 飞书 (Feishu)
- ✅ WebChat

### 技能
- skill-name (描述)

## 🧠 学习积累
### 有效模式
- 模式描述

### 待改进
- 改进项
```

---

## 自动维护配置

### 定时任务设置

**任务1：每日归档（每天 00:00）**
- 创建新的 `YYYY-MM-DD.md` 文件
- 归档前一天的对话记录

**任务2：整理长期记忆（每3天 02:00）**
- 读取最近3天的 DAILY 记忆
- 提取关键信息到 LONG-TERM
- 更新用户档案和偏好

**任务3：归档旧记忆（每7天 02:00）**
- 移动7天前的记忆文件到 `archive/`
- 清理临时文件

### 配置步骤

#### 1. 创建维护脚本

```bash
mkdir -p ~/workspace/scripts
cat > ~/workspace/scripts/memory-maintenance.sh << 'EOF'
#!/bin/bash
# 记忆维护脚本

WORKSPACE="/home/node/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SELF_IMPROVING="$WORKSPACE/self-improving"
LOG_FILE="$WORKSPACE/logs/memory-maintenance.log"

mkdir -p "$WORKSPACE/logs"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始记忆维护..." >> "$LOG_FILE"

# 每3天整理长期记忆
DAY_OF_MONTH=$(date +%d)
if [ $((DAY_OF_MONTH % 3)) -eq 0 ]; then
    echo "[$(date)] 整理长期记忆..." >> "$LOG_FILE"
    # 提取关键信息逻辑
fi

# 每7天归档旧记忆
if [ $((DAY_OF_MONTH % 7)) -eq 0 ]; then
    echo "[$(date)] 归档旧记忆..." >> "$LOG_FILE"
    find "$MEMORY_DIR" -name "*.md" -mtime +7 -exec mv {} "$SELF_IMPROVING/archive/" \;
fi

echo "[$(date)] 维护结束" >> "$LOG_FILE"
EOF

chmod +x ~/workspace/scripts/memory-maintenance.sh
```

#### 2. 配置系统定时任务

```bash
# 创建系统级 cron 任务
sudo tee /etc/cron.d/openclaw-memory << 'EOF'
# OpenClaw 记忆维护任务
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
HOME=/home/node

# 每天凌晨2点运行
0 2 * * * node /home/node/.openclaw/workspace/scripts/memory-maintenance.sh >> /home/node/.openclaw/workspace/logs/cron-memory.log 2>&1
EOF

sudo chmod 644 /etc/cron.d/openclaw-memory
```

#### 3. 验证配置

```bash
# 查看定时任务
cat /etc/cron.d/openclaw-memory

# 查看日志
tail -f ~/workspace/logs/memory-maintenance.log
```

---

## 手动操作指南

### 立即整理长期记忆

```bash
~/workspace/scripts/memory-maintenance.sh
```

### 查看今日记忆

```bash
cat ~/workspace/memory/$(date '+%Y-%m-%d').md
```

### 更新长期记忆

1. 编辑文件：
   ```bash
   nano ~/workspace/self-improving/long-term-memory.md
   ```

2. 添加重要信息：
   ```markdown
   ## 📅 新事件
   - 日期: 2026-03-10
   - 事件: 配置新系统
   - 结果: 成功
   ```

3. 保存并退出

### 备份记忆系统

```bash
# 创建备份
tar -czf memory-backup-$(date '+%Y%m%d').tar.gz \
  ~/workspace/memory/ \
  ~/workspace/self-improving/

# 移动备份到安全位置
mv memory-backup-*.tar.gz ~/backups/
```

---

## 故障排除

### 问题1：记忆文件没有自动创建

**检查：**
```bash
ls -la ~/workspace/memory/
```

**解决：**
- 确认目录权限：`chmod 755 ~/workspace/memory/`
- 手动创建今日文件：`touch ~/workspace/memory/$(date '+%Y-%m-%d').md`

### 问题2：定时任务不执行

**检查：**
```bash
# 查看系统日志
grep CRON /var/log/syslog | tail -20

# 检查脚本权限
ls -l ~/workspace/scripts/memory-maintenance.sh
```

**解决：**
- 确保脚本可执行：`chmod +x ~/workspace/scripts/memory-maintenance.sh`
- 检查 cron 服务状态：`systemctl status cron`

### 问题3：长期记忆没有更新

**检查：**
```bash
ls -la ~/workspace/self-improving/long-term-memory.md
```

**解决：**
- 手动运行整理脚本
- 检查日志文件：`cat ~/workspace/logs/memory-maintenance.log`

---

## 最佳实践

### 1. 定期审查
- **每周：** 检查本周记忆文件完整性
- **每月：** 审查长期记忆，删除过时信息
- **每季度：** 备份整个记忆系统

### 2. 敏感信息处理
- API Keys → 存储在 Gist 私有仓库
- 密码 → 使用环境变量
- 个人敏感信息 → 加密存储

### 3. 性能优化
- 定期归档旧文件（>30天）
- 限制单个记忆文件大小（<1MB）
- 清理临时日志文件

---

## 参考

- **文档位置：** `~/workspace/docs/memory-architecture-guide.md`
- **脚本位置：** `~/workspace/scripts/memory-maintenance.sh`
- **日志位置：** `~/workspace/logs/memory-maintenance.log`
- **配置位置：** `/etc/cron.d/openclaw-memory`

---

*最后更新：2026-03-10*
*版本：1.0*