#!/bin/bash

# OpenClaw 一键更新脚本
# 用法: ./update-openclaw.sh [docker-compose目录]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测 docker compose 命令（新版 vs 旧版）
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
    echo -e "${GREEN}✅ 使用新版: docker compose${NC}"
elif docker-compose version &>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo -e "${GREEN}✅ 使用旧版: docker-compose${NC}"
else
    echo -e "${RED}❌ 错误: 未找到 docker compose 或 docker-compose 命令${NC}"
    exit 1
fi

# 获取 docker-compose 目录
COMPOSE_DIR="${1:-.}"

echo -e "${YELLOW}🔍 检查目录: $COMPOSE_DIR${NC}"

if [ ! -f "$COMPOSE_DIR/docker-compose.yml" ] && [ ! -f "$COMPOSE_DIR/compose.yml" ]; then
    echo -e "${RED}❌ 错误: 在 $COMPOSE_DIR 找不到 docker-compose.yml 或 compose.yml${NC}"
    echo "用法: $0 [docker-compose目录]"
    exit 1
fi

cd "$COMPOSE_DIR"

echo -e "${YELLOW}📥 检查并拉取最新 OpenClaw 镜像...${NC}"

# 获取当前本地镜像 digest
LOCAL_DIGEST=$(docker images --no-trunc --quiet ghcr.io/openclaw/openclaw:latest 2>/dev/null | cut -d: -f2 || echo "")

# 拉取镜像（不强制）
$DOCKER_COMPOSE pull openclaw-gateway

# 获取更新后的 digest
NEW_DIGEST=$(docker images --no-trunc --quiet ghcr.io/openclaw/openclaw:latest 2>/dev/null | cut -d: -f2 || echo "")

# 检查是否有更新
if [ "$LOCAL_DIGEST" = "$NEW_DIGEST" ] && [ -n "$LOCAL_DIGEST" ]; then
    echo -e "${GREEN}✅ 镜像已是最新版本，无需更新${NC}"
    
    # 检查容器是否运行
    if $DOCKER_COMPOSE ps | grep -q "openclaw-gateway.*Up\|openclaw-gateway.*running"; then
        echo -e "${GREEN}✅ 服务运行正常${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  镜像未变，但容器未运行，重新启动所有服务...${NC}"
        $DOCKER_COMPOSE up -d
    fi
else
    echo -e "${GREEN}🆕 镜像有更新，重启所有服务...${NC}"
    $DOCKER_COMPOSE up -d --force-recreate
fi

echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

echo -e "${YELLOW}📋 查看最近日志...${NC}"
$DOCKER_COMPOSE logs --tail=20 openclaw-gateway

echo -e "${GREEN}✅ OpenClaw 更新完成!${NC}"
echo ""
echo -e "${YELLOW}📊 当前镜像信息:${NC}"
docker images | grep openclaw | head -1
