#!/bin/bash
# OpenClaw 混合部署脚本
# 方案：Nginx + 多端口后端

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose-hybrid.yml"

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
    
    # 创建 SSL 目录
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
            -subj "/C=CN/ST=State/L=City/O=OpenClaw/CN=localhost"
        
        log_success "自签名证书已生成"
        log_warn "注意：生产环境请使用真实 SSL 证书"
    else
        log_success "SSL 证书已存在"
    fi
}

# 复制现有配置（如果存在）
copy_existing_config() {
    log_info "检查现有配置..."
    
    # 检查是否有现有 OpenClaw 配置
    if [ -d "/home/node/.openclaw" ] && [ ! -f "$SCRIPT_DIR/instances/main/config/.initialized" ]; then
        log_info "发现现有 OpenClaw 配置，复制到 main 实例..."
        
        # 复制配置（排除 workspace，因为可能很大）
        if [ -d "/home/node/.openclaw/.openclaw" ]; then
            cp -r /home/node/.openclaw/.openclaw/* "$SCRIPT_DIR/instances/main/config/" 2>/dev/null || true
        fi
        
        # 复制 workspace（可选）
        if [ -d "/home/node/.openclaw/workspace" ]; then
            log_info "复制 workspace（这可能需要一些时间）..."
            cp -r /home/node/.openclaw/workspace/* "$SCRIPT_DIR/instances/main/workspace/" 2>/dev/null || true
        fi
        
        # 标记已初始化
        touch "$SCRIPT_DIR/instances/main/config/.initialized"
        log_success "现有配置已复制到 main 实例"
    fi
}

# 启动服务
start_services() {
    log_info "启动 OpenClaw 多实例服务..."
    
    cd "$SCRIPT_DIR"
    
    # 拉取最新镜像
    log_info "拉取最新镜像..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # 启动服务
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
    for port in 18789 18790 18791; do
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
    log_success "OpenClaw 多实例部署完成！"
    echo "=============================================="
    echo ""
    echo "访问地址:"
    echo "  主实例: https://your-server:8443/"
    echo "  工作实例: https://your-server:8443/work/"
    echo "  测试实例: https://your-server:8443/test/"
    echo ""
    echo "管理命令:"
    echo "  查看日志: docker-compose -f docker-compose-hybrid.yml logs -f"
    echo "  重启服务: docker-compose -f docker-compose-hybrid.yml restart"
    echo "  停止服务: docker-compose -f docker-compose-hybrid.yml down"
    echo ""
    echo "实例目录:"
    echo "  main:  $SCRIPT_DIR/instances/main/"
    echo "  work:  $SCRIPT_DIR/instances/work/"
    echo "  test:  $SCRIPT_DIR/instances/test/"
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

# 主函数
main() {
    case "${1:-deploy}" in
        deploy|start)
            check_dependencies
            setup_directories
            check_ssl
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
        clean)
            log_warn "这将删除所有实例数据！"
            read -p "确定要继续吗？(yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                docker-compose -f "$COMPOSE_FILE" down -v
                rm -rf "$SCRIPT_DIR/instances"
                log_success "已清理所有数据"
            else
                log_info "已取消"
            fi
            ;;
        help|--help|-h)
            echo "OpenClaw 混合部署脚本"
            echo ""
            echo "用法: $0 [命令]"
            echo ""
            echo "命令:"
            echo "  deploy|start   部署并启动服务（默认）"
            echo "  stop           停止服务"
            echo "  restart        重启服务"
            echo "  status         查看状态"
            echo "  logs [服务名]   查看日志"
            echo "  clean          清理所有数据（危险）"
            echo "  help           显示帮助"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
