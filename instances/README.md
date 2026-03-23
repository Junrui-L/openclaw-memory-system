# OpenClaw 多实例部署

## 方案对比

| 方案 | 文件 | 特点 | 适用场景 |
|------|------|------|----------|
| **子域名** | `docker-compose-subdomain.yml` | 独立域名，无冲突 | 生产环境，多用户 |
| **路径代理** | `docker-compose-hybrid.yml` | 单域名，路径区分 | 简单部署，测试 |
| **多端口** | - | 直接端口访问 | 本地开发，快速测试 |

## 推荐：子域名方案

### 目录结构

```
instances/
├── main/                 # 主实例（个人日常使用）
│   ├── config/          # OpenClaw 配置
│   └── workspace/       # 工作区文件
├── work/                # 工作实例（工作相关）
│   ├── config/
│   └── workspace/
└── test/                # 测试实例（实验性功能）
    ├── config/
    └── workspace/
```

### 访问方式（子域名方案）

| 实例 | 域名 | 用途 |
|------|------|------|
| main | `openclaw.your-domain.com` | 主实例，日常使用 |
| work | `work.your-domain.com` | 工作相关任务 |
| test | `test.your-domain.com` | 测试新功能 |

### 快速启动（子域名方案）

```bash
# 1. 运行部署脚本
bash deploy-subdomain.sh

# 2. 配置 hosts（本地测试）
echo "127.0.0.1 openclaw.local work.openclaw.local test.openclaw.local" | sudo tee -a /etc/hosts

# 3. 访问
# https://openclaw.local
# https://work.openclaw.local
# https://test.openclaw.local
```

### 生产环境配置

```bash
# 1. 配置 DNS
# openclaw.your-domain.com → 服务器IP
# work.your-domain.com     → 服务器IP
# test.your-domain.com     → 服务器IP

# 2. 生成 Let's Encrypt 证书
bash deploy-subdomain.sh letsencrypt your-domain.com

# 3. 启动
bash deploy-subdomain.sh deploy
```

## 管理命令

```bash
# 查看日志
bash deploy-subdomain.sh logs
bash deploy-subdomain.sh logs openclaw-main

# 重启
bash deploy-subdomain.sh restart

# 停止
bash deploy-subdomain.sh stop

# 状态
bash deploy-subdomain.sh status
```

## 添加新实例

1. 创建目录：
```bash
mkdir -p instances/new-instance/{config,workspace}
```

2. 在 `docker-compose-subdomain.yml` 中添加服务

3. 在 `nginx-subdomain.conf` 中添加 server 块

4. 重启：
```bash
docker-compose -f docker-compose-subdomain.yml up -d
```
