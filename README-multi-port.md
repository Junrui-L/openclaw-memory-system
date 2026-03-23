# OpenClaw 多端口独立部署

## 架构

```
openclaw-work/
├── config/          # OpenClaw 配置
├── workspace/       # 工作区文件
└── ssl/             # 独立 SSL 证书
    ├── cert.pem
    └── key.pem

openclaw-test/
├── config/
├── workspace/
└── ssl/
    ├── cert.pem
    └── key.pem

访问地址:
  https://IP:8444  → openclaw-work
  https://IP:8445  → openclaw-test
```

## 快速部署

```bash
# 1. 运行部署脚本
bash deploy-multi-port.sh

# 2. 访问
# https://192.168.1.69:8444  (工作实例)
# https://192.168.1.69:8445  (测试实例)
```

## 管理命令

```bash
# 查看状态
bash deploy-multi-port.sh status

# 查看日志
bash deploy-multi-port.sh logs
bash deploy-multi-port.sh logs openclaw-work

# 重启
bash deploy-multi-port.sh restart

# 停止
bash deploy-multi-port.sh stop

# 重新生成证书
bash deploy-multi-port.sh cert

# 清理所有数据
bash deploy-multi-port.sh clean
```

## 添加新实例

```bash
# 1. 创建目录结构
mkdir -p openclaw-dev/{config,workspace,ssl}

# 2. 生成 SSL 证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout openclaw-dev/ssl/key.pem \
  -out openclaw-dev/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=OpenClaw/CN=192.168.1.69"

# 3. 编辑 docker-compose-multi-port.yml，添加服务

# 4. 启动
docker-compose -f docker-compose-multi-port.yml up -d
```

## SSL 证书说明

每个实例有独立的 SSL 证书：
- `openclaw-work/ssl/` - 工作实例证书
- `openclaw-test/ssl/` - 测试实例证书

证书生成时包含服务器 IP 作为 SAN（Subject Alternative Name）。
