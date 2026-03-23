#!/bin/bash
# OpenClaw 多端口独立部署脚本
# 每个实例完全独立，包括 SSL 证书

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-multi-port.yml"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取服务器 IP
get_server_ip() {
    local ip=$(hostname -I | awk '{print $1}')
    if [ -z "$ip" ]; then
        ip="127.0.0.1"
    fi
    echo "$ip"
}

SERVER_IP="${SERVER_IP:-$(get_server_ip)}"

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建目录结构
setup_directories() {
    log_info "创建目录结构..."
    
    for instance in openclaw-work openclaw-test; do
        mkdir -p "$SCRIPT_DIR/$instance/config"
        mkdir -p "$SCRIPT_DIR/$instance/workspace"
        mkdir -p "$SCRIPT_DIR/$instance/ssl"
        log_info "  ✓ $instance/"
    done
    
    log_success "目录结构创建完成"
}

# 生成自签名 SSL 证书
generate_ssl_cert() {
    local instance="$1"
    local ssl_dir="$SCRIPT_DIR/$instance/ssl"
    
    log_info "生成 $instance 的 SSL 证书..."
    
    if [ -f "$ssl_dir/cert.pem" ] && [ -f "$ssl_dir/key.pem" ]; then
        log_info "  $instance SSL 证书已存在，跳过"
        return
    fi
    
    # 生成证书，包含 IP 地址
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$ssl_dir/key.pem" \
        -out "$ssl_dir/cert.pem" \
        -subj "/C=CN/ST=State/L=City/O=OpenClaw/CN=$SERVER_IP" \
        -addext "subjectAltName=IP:$SERVER_IP,DNS:localhost"
    
    log_success "  $instance SSL 证书已生成"
}

# 配置 OpenClaw 启用 HTTPS
configure_openclaw_https() {
    local instance="$1"
    local port="$2"
    local config_dir="$SCRIPT_DIR/$instance/config/.openclaw"
    
    log_info "配置 $instance 的 HTTPS..."
    
    mkdir -p "$config_dir"
    
    # 创建或更新配置
    cat > "$config_dir/config.json" << EOF
{
  "server": {
    "port": 18789,
    "https": {
      "enabled": true,
      "cert": "/home/node/.openclaw/ssl/cert.pem",
      "key": "/home/node/.openclaw/ssl/key.pem"
    }
  },
  "instance": "$instance"
}
EOF
    
    log_success "  $instance HTTPS 配置完成"
}

# 复制现有配置（可选）
copy_existing_config() {
    local instance="$1"
    local target_dir="$SCRIPT_DIR/$instance"
    
    log_info "检查 $instance 的现有配置..."
    
    # 检查是否有现有 OpenClaw 配置可以复制
    if [ "$instance" = "openclaw-work" ] && [ -d "/home/node/.openclaw" ] && [ ! -f "$target_dir/config/.initialized" ]; then
        log_info "  复制现有配置到 $instance..."
        
        if [ -d "/home/node/.openclaw/.openclaw" ]; then
            cp -r /home/node/.openclaw/.openclaw/* "$target_dir/config/" 2>/dev/null || true
        fi
        
        if [ -d "/home/node/.openclaw/workspace" ]; then
            cp -r /home/node/.openclaw/workspace/* "$target_dir/workspace/" 2>/dev/null || true
        fi
        
        touch "$target_dir/config/.initialized"
        log_success "  配置已复制"
    fi
}

# 启动服务
start_services() {
    log_info "启动 OpenClaw 多端口服务..."
    
    cd "$SCRIPT_DIR"
    
    log_info "拉取最新镜像..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    log_info "启动容器..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "服务已启动"
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    sleep 3
    
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    
    # 检查端口
    log_info "端口检查:"
    for port in 8444 8445; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_success "  ✓ 端口 $port 已监听"
        else
            log_warn "  ✗ 端口 $port 未监听"
        fi
    done
}

# 显示访问信息
show_access_info() {
    echo ""
    echo "=============================================="
    log_success "OpenClaw 多端口部署完成！"
    echo "=============================================="
    echo ""
    echo "服务器 IP: $SERVER_IP"
    echo ""
    echo "访问地址:"
    echo "  工作实例: https://$SERVER_IP:8444"
    echo "  测试实例: https://$SERVER_IP:8445"
    echo ""
    echo "目录结构:"
    echo "  openclaw-work/"
    echo "    ├── config/     # 配置文件"
    echo "    ├── workspace/  # 工作区"
    echo "    └── ssl/        # SSL 证书"
    echo "  openclaw-test/"
    echo "    ├── config/"
    echo "    ├── workspace/"
    echo "    └── ssl/"
    echo ""
    echo "管理命令:"
    echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  重启:     docker-compose -f $COMPOSE_FILE restart"
    echo "  停止:     docker-compose -f $COMPOSE_FILE down"
    echo ""
    echo "⚠️  注意：自签名证书需要浏览器信任"
    echo "=============================================="
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose -f "$COMPOSE_FILE" restart
    log_success "服务已重启"
}

# 查看日志
show_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    else
        docker-compose -f "$COMPOSE_FILE" logs -f
    fi
}

# 添加新实例
add_instance() {
    local name="$1"
    local port="$2"
    
    if [ -z "$name" ] || [ -z "$port" ]; then
        log_error "用法: $0 add <实例名> <端口>"
        echo "  例如: $0 add openclaw-dev 8446"
        exit 1
    fi
    
    log_info "添加新实例: $name (端口: $port)"
    
    # 创建目录
    mkdir -p "$SCRIPT_DIR/$name"/{config,workspace,ssl}
    
    # 生成 SSL 证书
    generate_ssl_cert "$name"
    
    log_success "实例 $name 已创建"
    log_warn "请手动编辑 $COMPOSE_FILE 添加服务配置"
}

# 主函数
main() {
    case "${1:-deploy}" in
        deploy|start)
            check_dependencies
            setup_directories
            
            # 为每个实例生成证书和配置
            generate_ssl_cert "openclaw-work"
            generate_ssl_cert "openclaw-test"
            
            copy_existing_config "openclaw-work"
            copy_existing_config "openclaw-test"
            
            start_services
            check_status
            show_access_info
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            check_status
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs "$2"
            ;;
        add)
            add_instance "$2" "$3"
            ;;
        cert|ssl)
            # 重新生成证书
            generate_ssl_cert "openclaw-work"
            generate_ssl_cert "openclaw-test"
            log_success "证书已重新生成"
            ;;
        clean)
            log_warn "这将删除所有实例数据！"
            read -p "确定要继续吗？(yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                docker-compose -f "$COMPOSE_FILE" down -v
                rm -rf "$SCRIPT_DIR/openclaw-work" "$SCRIPT_DIR/openclaw-test"
                log_success "已清理"
            fi
            ;;
        help|--help|-h)
            echo "OpenClaw 多端口独立部署脚本"
            echo ""
            echo "用法: $0 [命令] [参数]"
            echo ""
            echo "命令:"
            echo "  deploy|start     部署并启动服务（默认）"
            echo "  stop             停止服务"
            echo