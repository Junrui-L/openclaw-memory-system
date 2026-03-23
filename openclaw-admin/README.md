# OpenClaw Admin

OpenClaw 多实例 Web 管理界面

## 功能

- 📊 实时查看所有实例状态
- 🎮 启动/停止/重启容器
- 📋 查看容器日志
- 📈 监控 CPU/内存资源

## 快速开始

```bash
cd openclaw-admin

# 启动管理界面
docker-compose up -d

# 访问
http://192.168.1.69:3000
```

## 截图

- 实例状态卡片（运行/停止）
- 资源监控面板
- 日志查看弹窗

## API

| 接口 | 说明 |
|------|------|
| GET /api/instances | 获取所有实例状态 |
| POST /api/instances/:id/start | 启动实例 |
| POST /api/instances/:id/stop | 停止实例 |
| POST /api/instances/:id/restart | 重启实例 |
| POST /api/instances/:id/logs | 获取日志 |
| GET /api/stats | 获取资源统计 |

## 技术栈

- Node.js + Express
- 原生 JavaScript
- Docker API
