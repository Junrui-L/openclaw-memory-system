#!/bin/bash
# 修复 OpenClaw 端口问题

echo "=============================================="
echo "修复 OpenClaw 端口配置"
echo "=============================================="
echo ""

# 修复：使用 0.0.0.0 而不是 127.0.0.1，允许外部访问
echo "1. 修复端口绑定..."
echo "   将 127.0.0.1 改为 0.0.0.0"

for instance in openclaw-work openclaw-test openclaw-dev; do
    compose_file="$instance/docker-compose.yml"
    if [ -f "$compose_file" ]; then
        # 替换 127.0.0.1 为 0.0.0.0
        sed -i 's/127\.0\.0\.1:/0.0.0.0:/g' "$compose_file"
        echo "   ✓ $instance"
    fi
done

echo ""
echo "2. 重启所有实例..."
for instance in openclaw-work openclaw-test openclaw-dev; do
    echo "   重启 $instance..."
    cd "$instance"
    docker-compose down
    docker-compose up -d
    cd ..
done

echo ""
echo "3. 等待服务启动..."
sleep 5

echo ""
echo "4. 检查端口..."
for port in 15589 16789 17789; do
    echo -n "   端口 $port: "
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✓ 监听中"
    elif ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✓ 监听中"
    else
        echo "✗ 未监听"
    fi
done

echo ""
echo "=============================================="
echo "修复完成"
echo "=============================================="
echo ""
echo "现在可以尝试:"
echo "  ws://服务器IP:16789"
echo "  https://服务器IP:8445"
