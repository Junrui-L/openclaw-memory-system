#!/bin/bash
# OpenClaw 多实例诊断脚本

echo "=============================================="
echo "OpenClaw 多实例诊断"
echo "=============================================="
echo ""

# 检查容器状态
echo "1. 容器状态:"
echo "----------------------------------------------"
for instance in openclaw-work openclaw-test openclaw-dev; do
    echo -n "  $instance: "
    if docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^$instance$"; then
        echo "✓ 运行中"
        docker inspect --format='  端口: {{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{range $conf}}{{.HostIp}}:{{.HostPort}}{{end}}{{end}}' "$instance" 2>/dev/null || echo "  无法获取端口信息"
    else
        echo "✗ 未运行"
    fi
done
echo ""

# 检查端口监听
echo "2. 端口监听:"
echo "----------------------------------------------"
for port in 15589 16789 17789; do
    echo -n "  端口 $port: "
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✓ 监听中"
    elif ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✓ 监听中"
    else
        echo "✗ 未监听"
    fi
done
echo ""

# 检查健康状态
echo "3. 健康检查:"
echo "----------------------------------------------"
for port in 15589 16789 17789; do
    echo -n "  端口 $port: "
    response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port/health 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "✓ 健康 ($response)"
    else
        echo "✗ 异常 (HTTP $response)"
    fi
done
echo ""

# 检查日志
echo "4. 最近日志:"
echo "----------------------------------------------"
for instance in openclaw-work openclaw-test openclaw-dev; do
    echo "  $instance (最近5行):"
    docker logs --tail=5 "$instance" 2>/dev/null | sed 's/^/    /' || echo "    无法获取日志"
    echo ""
done

echo "=============================================="
echo "诊断完成"
echo "=============================================="
