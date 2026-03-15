# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## 🔧 核心环境

### 工作区路径
- **容器内**: `/home/node/.openclaw/workspace/`
- **记忆系统**: `/home/node/.openclaw/workspace/scripts/openclaw-memory-system/`

---

## 🐳 Docker 环境

### 服务架构
- **OpenClaw Gateway**: `openclaw-gateway:18789`
- **Nginx 反向代理**: `nginx` (端口 8443 → 443)
- **网络**: `openclaw-net` (bridge)

### 常用命令
```bash
# 查看容器状态
docker ps

# 重启 OpenClaw
docker-compose restart openclaw-gateway

# 重启 Nginx
docker-compose restart nginx

# 查看日志
docker logs -f openclaw-gateway
```

---

## 📁 项目路径

### 记忆管理系统
- **仓库**: `https://github.com/Junrui-L/openclaw-memory-system`
- **本地路径**: `/home/node/.openclaw/workspace/scripts/openclaw-memory-system/`
- **入口脚本**: `run.sh`
- **核心模块**: `memory_manager.py`

### 配置文件
- **主配置**: `config.yaml` / `config.json`
- **定时任务**: `crontab-v3.txt`
- **安装脚本**: `install-cron-v3.sh`

---

## 🌐 网络配置

### v2rayA 代理
- **Web UI**: `http://192.168.1.69:2017`
- **HTTP 代理**: `20171`
- **SOCKS5 代理**: `20170`
- **用途**: GitHub 访问、Docker 镜像拉取

### Git 代理设置
```bash
# 设置代理
git config --global http.proxy http://192.168.1.69:20171
git config --global https.proxy http://192.168.1.69:20171

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

## 🔑 访问地址

### OpenClaw
- **本地**: `http://localhost:18789`
- **HTTPS**: `https://192.168.1.69:8443`

### 其他服务
- **v2rayA**: `http://192.168.1.69:2017`
- **生日页面**: `https://192.168.1.69:8443/birthday`

---

## 📝 常用快捷命令

### 记忆系统
```bash
# 查看状态
bash scripts/openclaw-memory-system/run.sh status

# 生成晨报
bash scripts/openclaw-memory-system/run.sh report

# 手动执行 daily
bash scripts/openclaw-memory-system/run.sh daily

# 健康检查
bash scripts/openclaw-memory-system/run.sh health
```

### Git 操作
```bash
# 默认推送到双分支
git push origin master
git checkout main && git merge master && git push origin main
git checkout master
```

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
