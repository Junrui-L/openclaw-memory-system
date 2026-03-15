# 记忆管理系统 - 使用示例

> 常见使用场景和示例

---

## 快速开始

### 1. 查看系统状态

```bash
bash scripts/memory/run.sh status
```

**输出示例**:
```
📈 记忆系统统计
----------------------------------------
记忆文件: 4 个
学习记录: 5 条
待处理学习: 1 条
错误记录: 2 条
----------------------------------------
```

### 2. 生成晨报

```bash
bash scripts/memory/run.sh report
```

**输出示例**:
```
📊 生成报告...
==================================================
📅 日期: 2026-03-12
📅 昨日: 2026-03-11

✅ 报告已保存: reports/daily/2026-03-12-morning.md
==================================================
```

**报告内容预览**:
```markdown
# 🌅 早上好！今日记忆日报

📅 **日期**: 2026-03-12 (Thursday)
⏰ **报告时间**: 10:55

## 📊 昨日回顾 (2026-03-11)
✅ 昨日有记忆记录
- 📝 关键事件: 19 项
- ⏰ 待办事项: 8 项
- 💡 经验教训: 0 条

## 📈 学习统计
- 📚 学习记录: 5 条
  - 待处理: 1 条
  - 已解决: 3 条

## ⏰ 待办提醒
**共 8 项待办（从昨日继承）:**

🟡 **中优先级:**
- 考虑添加自动备份脚本
- 考虑使用 web_fetch 作为替代方案

🟢 **低优先级:**
- 飞书插件重复配置警告（不影响使用）
```

### 3. 健康检查

```bash
bash scripts/memory/run.sh health
```

**输出示例**:
```
🏥 执行健康检查...
==================================================
🔍 开始健康检查...

  ✅ 日记层: 4 个记忆文件
  ✅ 身份层: HOT记忆存在
  ✅ 任务层: 5 条学习记录
  ✅ 磁盘空间: 12.5% 已使用
  ✅ 日志大小: 0 个大日志文件
  ✅ 备份: 0 个备份文件

==================================================
📊 健康检查摘要
==================================================
✅ 日记层: 记忆文件: 4 个
✅ 身份层: HOT记忆: 存在
✅ 任务层: 学习记录: 5 条
✅ 磁盘空间: 使用率: 12.5%
✅ 日志大小: 大日志文件: 0 个
✅ 备份: 备份文件: 0 个

✅ 所有检查通过，系统健康！
==================================================
```

---

## 定时任务场景

### 场景1: 每小时归档

**需求**: 每小时检查并归档

**配置**:
```bash
# crontab
0 * * * * /home/node/.openclaw/workspace/scripts/memory/run.sh daily
```

**说明**: 每小时运行一次，自动判断是否需要归档

### 场景2: 每天早上8点报告

**需求**: 早上生成报告并发送到飞书

**配置**:
```bash
# 1. 修改 config.yaml
notification:
  feishu:
    enabled: true
    morning_report: true

# 2. crontab
0 8 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh report --send-feishu
```

### 场景3: 健康检查告警

**需求**: 每天检查健康状态，有告警时通知

**配置**:
```bash
# 1. 修改 config.yaml
notification:
  feishu:
    enabled: true
    health_alert: true

# 2. crontab
0 4 * * * /home/node/.openclaw/workspace/scripts/memory/run.sh health --send-alert
```

---

## 高级用法

### 强制归档

**场景**: 需要强制归档，忽略重复检查

```bash
bash scripts/memory/run.sh daily --force
```

### 详细健康检查

**场景**: 查看详细健康信息

```bash
bash scripts/memory/run.sh health --verbose
```

### 生成索引

**场景**: 手动生成记忆索引

```bash
bash scripts/memory/run.sh index
```

**输出**: `memory/INDEX.md`

### 手动备份

**场景**: 立即执行备份

```bash
bash scripts/memory/run.sh backup
```

**输出**:
```
💾 执行备份...
==================================================
  ✅ 每日备份: daily-20260312.tar.gz
==================================================
```

### 执行全部任务

**场景**: 手动执行所有任务

```bash
bash scripts/memory/run.sh all
```

**执行顺序**:
1. daily（每日归档）
2. maintenance（记忆维护）
3. report（生成报告）

---

## 故障排查

### 问题1: Python模块未找到

**现象**:
```
ModuleNotFoundError: No module named 'yaml'
```

**解决**:
- 系统会自动降级到JSON配置
- 无需处理，正常使用

### 问题2: 权限不足

**现象**:
```
Permission denied: reports/daily/
```

**解决**:
```bash
# 检查目录权限
ls -la /home/node/.openclaw/workspace/reports/

# 修复权限
chmod 755 /home/node/.openclaw/workspace/reports/
```

### 问题3: 记忆文件未更新

**现象**: 今天记忆文件没有新内容

**检查**:
```bash
# 查看今天文件
ls -la memory/2026-03-12.md

# 手动运行归档
bash scripts/memory/run.sh daily
```

---

## 自定义扩展

### 添加自定义报告

**步骤**:
1. 在 `modules/reporter.py` 添加新方法
2. 在 `memory_manager.py` 添加新命令
3. 测试并文档化

### 修改智能待办规则

**配置**:
```yaml
# config.yaml
todo:
  smart_priority: true
  high_keywords:
    - "紧急"
    - "重要"
    - "你的自定义关键词"
```

---

## 最佳实践

### 1. 首次部署

```bash
# 1. 测试所有命令
bash scripts/memory/run.sh status
bash scripts/memory/run.sh report
bash scripts/memory/run.sh health

# 2. 配置定时任务
# 复制 crontab 配置到宿主机

# 3. 验证定时任务
grep memory /var/log/cron.log
```

### 2. 日常监控

```bash
# 每周查看健康报告
cat reports/daily/$(date +%Y-%m-%d)-health.md

# 检查备份
ls -la .backup/

# 检查归档
ls -la archive/memory/
```

### 3. 故障恢复

```bash
# 从备份恢复
cd /home/node/.openclaw/workspace
tar xzf .backup/daily-20260312.tar.gz

# 从归档恢复
cp archive/memory/2026-03-01.md memory/
```

---

*最后更新: 2026-03-12*
