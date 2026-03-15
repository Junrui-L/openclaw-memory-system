# Docker Compose 配置审查

## 当前配置分析

### ✅ 优点
1. **使用自定义网络** `openclaw-net` - 容器间通信更稳定
2. **数据持久化** - config 和 workspace 都挂载了卷
3. **Nginx 反向代理** - 8443 端口映射到 443，有 SSL 准备

### ⚠️ 建议改进

#### 1. 端口映射问题
```yaml
ports:
  - "8443:443"
```
- 外部 8443 → 内部 443，这是正确的反向代理模式
- 但 openclaw-gateway 没有暴露任何端口，Nginx 怎么连它？

**建议**: 给 gateway 添加端口暴露
```yaml
openclaw-gateway:
  # ...
  expose:
    - "3000"  # 或其他 OpenClaw 内部端口
```

#### 2. 缺少健康检查
建议添加健康检查确保服务正常：
```yaml
openclaw-gateway:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

#### 3. 时区设置
建议添加时区，避免日志时间不对：
```yaml
environment:
  - NODE_ENV=production
  - TZ=Asia/Shanghai
```

#### 4. 日志限制
防止日志占满磁盘：
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 优化后的完整配置

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "8443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/ssl:ro
    networks:
      - openclaw-net
    depends_on:
      - openclaw-gateway
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  openclaw-gateway:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw-gateway
    restart: unless-stopped
    expose:
      - "3000"
    networks:
      - openclaw-net
    environment:
      - NODE_ENV=production
      - TZ=Asia/Shanghai
    volumes:
      - ./config:/home/node/.openclaw
      - ./workspace:/home/node/.openclaw/workspace
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  openclaw-net:
    driver: bridge
```

## 需要确认的问题

1. **OpenClaw 内部端口是多少？** 需要确认是 3000 还是其他端口
2. **nginx.conf 配置了吗？** 需要确保 Nginx 正确代理到 openclaw-gateway
3. **SSL 证书准备好了吗？** ./ssl 目录是否有有效证书？
