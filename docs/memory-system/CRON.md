# 记忆管理系统 - 定时任务配置

> 完整的 crontab 配置指南

---

## 配置方法

### 方法1: 宿主机 crontab（推荐）

```bash
# SSH 登录宿主机
ssh jeremy@Qiliwind

# 编辑 crontab
crontab -e

# 粘贴下面的配置
```

### 方法2: Docker 容器内（如支持）

```bash
# 进入容器
docker exec -it openclaw-gateway bash

# 安装 cron（如未安装）
apt-get update && apt-get install -y cron

# 配置定时任务
crontab -e
```

---

## 推荐配置

### 基础配置（最小化）

```bash
# 记忆管理系统 - 基础定时任务
# 每天早上8点生成日报
0 8 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report

# 每天凌晨2点执行维护
0 2 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh maintenance
```

### 完整配置（推荐）

```bash
# ========================================
# 记忆管理系统 - 完整定时任务配置
# ========================================

# 日志目录
LOG_DIR="/vol2/1000/Projects/openclaw/logs"

# ---------- 每日归档 ----------
# 多次运行，增量归档
# 0点、6点、12点、18点
0 0,6,12,18 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh daily >> $LOG_DIR/cron-daily.log 2>&1

# ---------- 记忆维护 ----------
# 每天凌晨2点检查
# 自动判断：每3天整理，每7天归档
0 2 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh maintenance >> $LOG_DIR/cron-maintenance.log 2>&1

# ---------- 生成日报 ----------
# 每天早上8点
0 8 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report >> $LOG_DIR/cron-report.log 2>&1

# ---------- 健康检查 ----------
# 每天凌晨4点
0 4 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh health >> $LOG_DIR/cron-health.log 2>&1

# ---------- 自动备份 ----------
# 每天凌晨3点
0 3 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh backup >> $LOG_DIR/cron-backup.log 2>&1

# ---------- 生成索引 ----------
# 每周一凌晨1点
0 1 * * 1 docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh index >> $LOG_DIR/cron-index.log 2>&1

# ---------- 每周完整检查 ----------
# 每周日半夜12点执行全部
0 0 * * 0 docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh all >> $LOG_DIR/cron-weekly.log 2>&1
```

### 飞书通知配置

```bash
# 需要先在 config.yaml 中启用飞书通知
# notification.feishu.enabled: true

# 生成报告并发送到飞书
0 8 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report --send-feishu >> $LOG_DIR/cron-report.log 2>&1

# 健康告警发送到飞书
0 4 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh health --send-alert >> $LOG_DIR/cron-health.log 2>&1
```

---

## 配置详解

### 时间格式

```
# 格式: 分 时 日 月 周
# 示例:
0 8 * * *    # 每天8点0分
0 2 * * 0    # 每周日凌晨2点
*/30 * * * * # 每30分钟
```

### 任务说明

| 任务 | 频率 | 时间 | 说明 |
|------|------|------|------|
| daily | 每天4次 | 00:00, 06:00, 12:00, 18:00 | 增量归档，整理今天 |
| maintenance | 每天1次 | 02:00 | 每3天整理，每7天归档 |
| report | 每天1次 | 08:00 | 生成晨报 |
| health | 每天1次 | 04:00 | 健康检查 |
| backup | 每天1次 | 03:00 | 自动备份 |
| index | 每周1次 | 周一 01:00 | 生成索引 |
| all | 每周1次 | 周日 00:00 | 执行全部任务 |

### 日志管理

```bash
# 创建日志目录
mkdir -p /vol2/1000/Projects/openclaw/logs

# 日志轮转（可选）
# 安装 logrotate
sudo apt-get install logrotate

# 配置 /etc/logrotate.d/openclaw-memory
/vol2/1000/Projects/openclaw/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 node node
}
```

---

## 验证配置

### 检查定时任务

```bash
# 查看当前用户的定时任务
crontab -l

# 查看系统定时任务日志
tail -f /var/log/cron.log

# 查看特定任务日志
tail -f /vol2/1000/Projects/openclaw/logs/cron-daily.log
```

### 手动测试

```bash
# 模拟定时任务执行
docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh daily

# 检查输出
echo $?
```

### 监控任务执行

```bash
# 查看最近执行的任务
ls -lt /vol2/1000/Projects/openclaw/logs/cron-*.log | head -5

# 查看报告生成情况
ls -lt /home/node/.openclaw/workspace/reports/daily/*.md | head -5

# 查看备份情况
ls -lt /home/node/.openclaw/workspace/.backup/*.tar.gz | head -5
```

---

## 故障排查

### 问题1: 定时任务未执行

**检查**:
```bash
# 1. 检查 cron 服务
sudo service cron status

# 2. 检查定时任务语法
crontab -l | grep memory

# 3. 检查日志
tail /var/log/syslog | grep CRON
```

### 问题2: Docker 命令失败

**检查**:
```bash
# 1. 检查容器运行
docker ps | grep openclaw-gateway

# 2. 手动执行测试
docker exec openclaw-gateway echo "test"

# 3. 检查路径
ls -la /home/node/.openclaw/workspace/scripts/memory/run.sh
```

### 问题3: 权限不足

**解决**:
```bash
# 确保日志目录可写
chmod 755 /vol2/1000/Projects/openclaw/logs
chown node:node /vol2/1000/Projects/openclaw/logs
```

---

## 高级配置

### 环境变量

```bash
# 在 crontab 中设置环境变量
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/node
LOG_DIR=/vol2/1000/Projects/openclaw/logs

# 任务
0 8 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report >> $LOG_DIR/cron-report.log 2>&1
```

### 条件执行

```bash
# 只在工作日执行
0 8 * * 1-5 docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report

# 只在周末执行
0 8 * * 0,6 docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh report
```

### 邮件通知

```bash
# 配置邮件（需安装 mailutils）
MAILTO="admin@example.com"

# 任务（输出会邮件发送）
0 8 * * * docker exec openclaw-gateway bash /home/node/.openclaw/workspace/scripts/memory/run.sh health
```

---

## 最佳实践

### 1. 逐步启用

```bash
# 第一周：只启用 report
0 8 * * * docker exec ... run.sh report

# 第二周：添加 daily
0 0,12 * * * docker exec ... run.sh daily

# 第三周：添加 health
0 4 * * * docker exec ... run.sh health

# 第四周：启用全部
```

### 2. 监控告警

```bash
# 检查今天是否有报告生成
if [ ! -f "/home/node/.openclaw/workspace/reports/daily/$(date +%Y-%m-%d)-morning.md" ]; then
    echo "警告：今天晨报未生成" | mail -s "Memory System Alert" admin@example.com
fi
```

### 3. 备份 crontab

```bash
# 导出 crontab
crontab -l > /vol2/1000/Projects/openclaw/config/crontab-backup.txt

# 恢复 crontab
crontab /vol2/1000/Projects/openclaw/config/crontab-backup.txt
```

---

*最后更新: 2026-03-12*
