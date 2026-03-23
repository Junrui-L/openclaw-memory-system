# OpenClaw 多实例部署指南

> 在同一台宿主机上部署多个 OpenClaw 实例，实现工作/测试/开发环境隔离

## 目录

- [架构概述](#架构概述)
- [部署方案对比](#部署方案对比)
- [推荐方案：独立端口 + Nginx](#推荐方案独立端口--nginx)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [常见问题](#常见问题)
- [维护操作](#维护操作)

---

## 架构概述

```
┌─────────────────────────────────────────────────────────┐
│                    宿主机 (192.168.1.69)                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────┐ │
│  │ openclaw-gateway│  │  openclaw-work  │  │openclaw- │ │
│  │   (主实例)      │  │   (工作实例)     │  │  test    │ │
│  │                 │  │                 │  │(测试实例)│ │
│  │  端口: 18789    │  │  端口: 18789    │  │ 端口:18789│ │
│  │  HTTPS: 8443    │  │  映射: 17789    │  │ 映射:16789│ │
│  │                 │  │  HTTPS: 8447    │  │ HTTPS:8445│ │
│  └────────┬────────┘  └────────┬────────┘  └─────┬────┘ │
│           │                    │                  │      │
│  ┌────────┴────────────────────┴──────────────────┴────┐ │
│  │              Nginx 反向代理 (每个实例独立)            │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 部署方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **路径代理** (`/work/`, `/test/`) | 单域名，配置简单 | WebSocket 易出问题，Cookie 冲突 | 简单测试 |
| **多端口直接** (`:8444`, `:8445`) | 完全隔离，无冲突 | 需要多个端口 | 生产环境 |
| **子域名** (`work.domain.com`) | 最优雅 | 需要域名和 DNS | 有域名环境 |
| **独立端口 + Nginx** (推荐) | 隔离性好，支持 HTTPS | 配置稍复杂 | 生产环境 |

---

## 推荐方案：独立端口 + Nginx

### 目录结构

```
workspace/
├── openclaw-work/              # 工作实例
│   ├── docker-compose.yml     # Docker 编排
│   ├── nginx/
│   │   └── nginx.conf         # Nginx 配置
│   ├── ssl/                   # SSL 证书
│   ├── config/                # OpenClaw 配置
│   └── workspace/             # 工作区
│
├── openclaw-test/              # 测试实例
│   ├── docker-compose.yml
│   ├── nginx/
│   │   └── nginx.conf
│   ├── ssl/
│   ├── config/
│   └── workspace/
│
└── deploy-all.sh              # 统一部署脚本
```

### 端口分配

| 实例 | 容器内端口 | 宿主机 WebSocket | HTTPS 端口 | 用途 |
|------|-----------|------------------|-----------|------|
| openclaw-gateway | 18789 | - | 8443 | 主实例 |
| openclaw-work | 18789 | 17789 | 8447 | 工作 |
| openclaw-test | 18789 | 16789 | 8445 | 测试 |

---

## 快速开始

### 1. 创建目录结构

```bash
mkdir -p openclaw-{work,test}/{config,workspace,ssl,nginx}
```

### 2. 复制配置模板

```bash
# 工作实例
cat > openclaw-work/docker-compose.yml << 'EOF'
version: '3.8'

services:
  openclaw-work:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw-work
    restart: unless-stopped
    ports:
      - "0.0.0.0:17789:18789"  # WebSocket 端口
    expose:
      - "18789"
    networks:
      - openclaw-work-net
    environment:
      - NODE_ENV=production
      - TZ=Asia/Shanghai
      - INSTANCE_NAME=work
    volumes:
      - ./config:/home/node/.openclaw
      - ./workspace:/home/node/.openclaw/workspace
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:18789/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx-work:
    image: nginx:alpine
    container_name: nginx-work
    restart: unless-stopped
    ports:
      - "8447:443"    # HTTPS 端口
      - "8087:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/ssl:ro
    networks:
      - openclaw-work-net
    depends_on:
      - openclaw-work

networks:
  openclaw-work-net:
    driver: bridge
EOF
```

### 3. 生成 SSL 证书

```bash
cd openclaw-work
mkdir -p ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=OpenClaw/CN=192.168.1.69" \
  -addext "subjectAltName=IP:192.168.1.69,DNS:localhost"
```

### 4. 创建 Nginx 配置

```bash
cat > openclaw-work/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 禁用缓冲（WebSocket 需要）
    proxy_buffering off;
    proxy_cache off;
    
    server {
        listen 443 ssl;
        http2 on;
        server_name _;
        
        ssl_certificate /ssl/cert.pem;
        ssl_certificate_key /ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        
        location / {
            proxy_pass http://openclaw-work:18789;
            proxy_http_version 1.1;
            
            # WebSocket 支持
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_read_timeout 86400;
        }
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        return 301 https://$host$request_uri;
    }
}
EOF
```

### 5. 启动实例

```bash
cd openclaw-work
docker-compose up -d
```

---

## 详细配置

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `INSTANCE_NAME` | 实例标识 | `work`, `test`, `dev` |
| `TZ` | 时区 | `Asia/Shanghai` |
| `PUPPETEER_EXECUTABLE_PATH` | 浏览器路径 | `/usr/bin/chromium` |

### Nginx 关键配置

```nginx
# WebSocket 支持（必须）
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";

# 禁用缓冲（WebSocket 需要）
proxy_buffering off;
proxy_cache off;

# 超时设置
proxy_read_timeout 86400;
```

### OpenClaw 配置

编辑 `config/.openclaw/config.json`：

```json
{
  "gateway": {
    "port": 18789,
    "bind": "lan",
    "mode": "local"
  },
  "instance": "work"
}
```

---

## 常见问题

### Q1: CLI 无法连接 Gateway

**现象**：`openclaw devices list` 报错 `gateway closed`

**原因**：容器内 Gateway 监听 `0.0.0.0`，但 CLI 默认连 `127.0.0.1`

**解决**：
```bash
# 使用宿主机 IP 连接
openclaw --gateway ws://192.168.1.69:17789 devices list

# 或使用 HTTPS
openclaw --gateway https://192.168.1.69:8447 devices list
```

### Q2: WebSocket 连接失败

**检查**：
1. Nginx 配置是否包含 `Upgrade` 和 `Connection` 头
2. `proxy_buffering off` 是否设置
3. 防火墙是否放行端口

### Q3: SSL 证书错误

**解决**：
```bash
# 重新生成证书，包含正确 IP
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/CN=192.168.1.69" \
  -addext "subjectAltName=IP:192.168.1.69"
```

### Q4: 端口冲突

**检查**：
```bash
netstat -tuln | grep -E "15589|16789|17789|8443|8445|8447"
```

---

## 维护操作

### 查看日志

```bash
# 单个实例
docker-compose logs -f

# 所有实例
for dir in openclaw-work openclaw-test; do
  echo "=== $dir ==="
  (cd $dir && docker-compose logs --tail=20)
done
```

### 重启实例

```bash
# 单个
docker-compose restart

# 所有
bash deploy-all.sh restart
```

### 备份配置

```bash
# 备份所有实例配置
tar czf openclaw-backup-$(date +%Y%m%d).tar.gz openclaw-*/config openclaw-*/workspace
```

### 更新镜像

```bash
# 拉取最新镜像
docker-compose pull
docker-compose up -d
```

---

## 参考

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Nginx WebSocket 代理](https://nginx.org/en/docs/http/websocket.html)

---

*最后更新: 2026-03-17*
