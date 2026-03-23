#!/bin/bash
# OpenClaw 多实例统一部署脚本
# 每个实例独立目录，独立 nginx.conf

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# 生成 SSL 证书
generate_ssl_cert() {
    local instance="$1"
    local ssl_dir="$SCRIPT_DIR/$instance/ssl"
    
    log_info "生成 $instance 的 SSL 证书..."
    
    mkdir -p "$ssl_dir"
    
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

# 部署单个实例
deploy_instance() {
    local instance="$1"
    local port="$2"
    
    log_info "部署 $instance (端口: $port)..."
    
    cd "$SCRIPT_DIR/$instance"
    
    # 生成 SSL 证书
    generate_ssl_cert "$instance"
    
    # 启动服务
    docker-compose up -d
    
    log_success "  $instance 部署完成"
}

# 启动所有实例
deploy_all() {
    log_info "开始部署所有 OpenClaw 实例..."
    
    check_dependencies
    
    # 部署 work 实例
    deploy_instance "openclaw-work" "8444"
    
    # 部署 test 实例
    deploy_instance "openclaw-test" "8445"
    
    log_success "所有实例部署完成！"
}

# 检查状态
check_status() {
    log_info "检查服务状态..."
    
    echo ""
    echo "=============================================="
    echo "OpenClaw 多实例状态"
    echo "=============================================="
    echo ""
    
    for instance in openclaw-work openclaw-test; do
        local port=$(grep -oP '\d{4}' "$SCRIPT_DIR/$instance/docker-compose.yml" | head -1)
        echo -n "  $instance (端口: $port): "
        
        if docker ps --format "{{.Names}}" | grep -q "^$instance$"; then
            echo -e "${GREEN}运行中${NC}"
        else
            echo -e "${RED}未运行${NC}"
        fi
    done
    
    echo ""
    echo "访问地址:"
    echo "  https://$SERVER_IP:8444  - openclaw-work"
    echo "  https://$SERVER_IP:8445  - openclaw-test"
    echo "=============================================="
}

# 停止所有
stop_all() {
    log_info "停止所有实例..."
    
    for instance in openclaw-work openclaw-test; do
        log_info "  停止 $instance..."
        cd "$SCRIPT_DIR/$instance"
        docker-compose down
    done
    
    log_success "所有实例已停止"
}

# 重启所有
restart_all() {
    log_info "重启所有实例..."
    
    for instance in openclaw-work openclaw-test; do
        log_info "  重启 $instance..."
        cd "$SCRIPT_DIR/$instance"
        docker-compose restart
    done
    
    log_success "所有实例已重启"
}

# 查看日志
show_logs() {
    local instance="$1"
    
    if [ -n "$instance" ]; then
        cd "$SCRIPT_DIR/$instance"
        docker-compose logs -f
    else
        # 显示所有实例日志
        for inst in openclaw-work openclaw-test; do
            echo "=== $inst ==="
            cd "$SCRIPT_DIR/$inst"
            docker-compose logs --tail=20
            echo ""
        done
    fi
}

# 主函数
main() {
    case "${1:-deploy}" in
        deploy|start)
            deploy_all
            sleep 3
            check_status
            ;;
        stop)
            stop_all
            ;;
        restart)
            restart_all
            check_status
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs "$2"
            ;;
        cert)
            # 重新生成所有证书
            for instance in openclaw-work openclaw-test; do
                rm -f "$SCRIPT_DIR/$instance/ssl"/*.pem
                generate_ssl_cert "$instance"
            done
            log_success "所有证书已重新生成"
            ;;
        clean)
            log_warn "这将删除所有实例数据！"
            read -p "确定要继续吗？(yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                for instance in openclaw-work openclaw-test; do
                    cd "$SCRIPT_DIR/$instance"
                    docker-compose down -v
                done
                rm -rf "$SCRIPT_DIR"/openclaw-*/config/* "$SCRIPT_DIR"/openclaw-*/workspace/*
                log_success "已清理"
            fi
            ;;
        help|--help|-h)
            echo "OpenClaw 多实例统一部署脚本"
            echo ""
            echo "用法: $0 [命令] [参数]"
            echo ""
            echo "命令:"
            echo "  deploy|start   部署并启动所有实例（默认）"
            echo "  stop           停止所有实例"
            echo "  restart        重启所有实例"
            echo "  status         查看状态"
            echo "  logs [实例名]   查看日志"
            echo "  cert           重新生成所有 SSL 证书"
            echo "  clean          清理所有数据（危险）"
            echo "  help           显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 deploy"
            echo "  $0 logs openclaw-work"
            ;;
        *)
            log_error "未知命令: $1"
            exit 1
            ;;
    esac
}

main "$@"
