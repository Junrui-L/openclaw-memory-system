#!/bin/bash
# OpenClaw 子域名部署脚本
# 方案：每个实例独立子域名

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-subdomain.yml"

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
    
    for instance in main work test; do
        mkdir -p "$SCRIPT_DIR/instances/$instance/config"
        mkdir -p "$SCRIPT_DIR/instances/$instance/workspace"
        log_info "  ✓ instances/$instance"
    done
    
    mkdir -p "$SCRIPT_DIR/ssl"
    
    log_success "目录结构创建完成"
}

# 检查 SSL 证书
check_ssl() {
    log_info "检查 SSL 证书..."
    
    if [ ! -f "$SCRIPT_DIR/ssl/cert.pem" ] || [ ! -f "$SCRIPT_DIR/ssl/key.pem" ]; then
        log_warn "SSL 证书不存在，生成自签名证书..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SCRIPT_DIR/ssl/key.pem" \
            -out "$SCRIPT_DIR/ssl/cert.pem" \
            -subj "/C=CN/ST=State/L=City/O=OpenClaw/CN=openclaw.local"
        
        log_success "自签名证书已生成"
        log_warn "注意：生产环境请使用真实 SSL 证书"
        log_warn "      可以使用 Let's Encrypt: certbot --nginx"
    else
        log_success "SSL 证书已存在"
    fi
}

# 配置 hosts（本地测试）
setup_hosts() {
    log_info "配置本地 hosts（可选）..."
    
    if grep -q "openclaw.local" /etc/hosts 2>/dev/null; then
        log_info "hosts 已配置"
    else
        echo ""
        log_warn "请在 /etc/hosts 中添加以下配置（本地测试）："
        echo ""
        echo "# OpenClaw 多实例"
        echo "127.0.0.1  openclaw.local"
        echo "127.0.0.1  work.openclaw.local"
        echo "127.0.0.1  test.openclaw.local"
        echo ""
        log_info "或者使用真实域名，配置 DNS 指向服务器 IP"
    fi
}

# 复制现有配置
copy_existing_config() {
    log_info "检查现有配置..."
    
    if [ -d "/home/node/.openclaw" ] && [ ! -f "$SCRIPT_DIR/instances/main/config/.initialized" ]; then
        log_info "复制现有配置到 main 实例..."
        
        if [ -d "/home/node/.openclaw/.openclaw" ]; then
            cp -r /home/node/.openclaw/.openclaw/* "$SCRIPT_DIR/instances/main/config/" 2>/dev/null || true
        fi
        
        if [ -d "/home/node/.openclaw/workspace" ]; then
            log_info "复制 workspace..."
            cp -r /home/node/.openclaw/workspace/* "$SCRIPT_DIR/instances/main/workspace/" 2>/dev/null || true
        fi
        
        touch "$SCRIPT_DIR/instances/main/config/.initialized"
        log_success "配置已复制"
    fi
}

# 启动服务
start_services() {
    log_info "启动 OpenClaw 子域名服务..."
    
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
    
    # 检查健康状态
    log_info "健康检查:"
    for instance in openclaw-main openclaw-work openclaw-test; do
        if docker inspect --format='{{.State.Health.Status}}' "$instance" 2>/dev/null | grep -q "healthy"; then
            log_success "  ✓ $instance: healthy"
        else
            log_warn "  ✗ $instance: 检查中..."
        fi
    done
}

# 显示访问信息
show_access_info() {
    local domain="${DOMAIN:-openclaw.local}"
    
    echo ""
    echo "=============================================="
    log_success "OpenClaw 子域名部署完成！"
    echo "=============================================="
    echo ""
    echo "访问地址:"
    echo "  主实例:  https://openclaw.$domain"
    echo "  工作实例: https://work.$domain"
    echo "  测试实例: https://test.$domain"
    echo ""
    echo "本地测试配置（/etc/hosts）:"
    echo "  127.0.0.1  openclaw.$domain"
    echo "  127.0.0.1  work.$domain"
    echo "  127.0.0.1  test.$domain"
    echo ""
    echo "生产环境配置:"
    echo "  1. 购买/配置域名"
    echo "  2. 添加 DNS A 记录指向服务器 IP"
    echo "  3. 使用 Let's Encrypt 证书"
    echo ""
    echo "管理命令:"
    echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  重启:     docker-compose -f $COMPOSE_FILE restart"
    echo "  停止:     docker-compose -f $COMPOSE_FILE down"
    echo "=============================================="
}

# 生成 Let's Encrypt 证书（生产环境）
generate_letsencrypt() {
    log_info "生成 Let's Encrypt 证书..."
    
    local domain="$1"
    if [ -z "$domain" ]; then
        log_error "请指定域名: $0 letsencrypt your-domain.com"
        exit 1
    fi
    
    if ! command -v certbot &> /dev/null; then
        log_info "安装 certbot..."
        apt-get update && apt-get install -y certbot
    fi
    
    # 停止 Nginx
    docker-compose -f "$COMPOSE_FILE" stop nginx
    
    # 生成证书
    certbot certonly --standalone -d "openclaw.$domain" -d "work.$domain" -d "test.$domain"
    
    # 复制证书
    cp "/etc/letsencrypt/live/openclaw.$domain/fullchain.pem" "$SCRIPT_DIR/ssl/cert.pem"
    cp "/etc/letsencrypt/live/openclaw.$domain/privkey.pem" "$SCRIPT_DIR/ssl/key.pem"
    
    # 启动 Nginx
    docker-compose -f "$COMPOSE_FILE" start nginx
    
    log_success "Let's Encrypt 证书已生成"
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

# 主函数
main() {
    case "${1:-deploy}" in
        deploy|start)
            check_dependencies
            setup_directories
            check_ssl
            setup_hosts
            copy_existing_config
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
        letsencrypt)
            generate_letsencrypt "$2"
            ;;
        clean)
            log_warn "这将删除所有实例数据！"
            read -p "确定要继续吗？(yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                docker-compose -f "$COMPOSE_FILE" down -v
                rm -rf "$SCRIPT_DIR/instances"
                log_success "已清理"
            fi
            ;;
        help|--help|-h)
            echo "OpenClaw 子域名部署脚本"
            echo ""
            echo "用法: $0 [命令] [参数]"
            echo ""
            echo "命令:"
            echo "  deploy|start          部署并启动服务"
            echo "  stop                  停止服务"
            echo "  restart               重启服务"
            echo "  status                查看状态"
            echo "  logs [服务名]          查看日志"
            echo "  letsencrypt <domain>  生成 Let's Encrypt 证书"
            echo "  clean                 清理所有数据（危险）"
            echo "  help                  显示帮助"
            echo ""
            echo "示例:"
            echo "  $0 deploy"
            echo "  $0 letsencrypt your-domain.com"
            ;;
        *)
            log_error "未知命令: $1"
            exit 1
            ;;
    esac
}

main "$@"
