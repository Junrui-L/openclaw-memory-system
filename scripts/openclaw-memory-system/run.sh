#!/bin/bash
# 记忆管理系统 v3.1 - 统一入口
# 支持：daily, report, health, backup, index, maintenance, status, log

set -e

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULES_DIR="$SCRIPT_DIR/modules"
WORKSPACE_DIR="/home/node/.openclaw/workspace"

# Python 模块路径（支持根目录和 modules 子目录）
PYTHON_MODULE_DIR="$SCRIPT_DIR"
MEMORY_DIR="$WORKSPACE_DIR/memory"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 禁用颜色（用于管道）
if [ -t 1 ]; then
    : # 终端输出，保持颜色
else
    GREEN=''
    YELLOW=''
    RED=''
    BLUE=''
    NC=''
fi

# 日志函数
log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} $1"
}

# 检查 Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到 Python"
        exit 1
    fi
}

# 检查 Python（带版本输出）
check_python_with_info() {
    check_python
    log_info "使用 Python: $($PYTHON_CMD --version 2>&1)"
}

# 显示帮助
show_help() {
    echo "记忆管理系统 v3.1"
    echo ""
    echo "用法: $0 <命令> [选项]"
    echo ""
    echo "命令:"
    echo "  daily              每日归档（创建/更新今天记忆文件）"
    echo "  report             生成晨报"
    echo "  health             系统健康检查"
    echo "  backup             增量备份"
    echo "  index              生成记忆索引"
    echo "  maintenance        清理维护"
    echo "  status             查看系统状态"
    echo "  log                记录当前对话到日记"
    echo "  watch              启动对话监控（自动记录）"
    echo "  session-merge      合并 Sessions 到日记"
    echo "  session-check      检查 Session 覆盖率"
    echo ""
    echo "选项:"
    echo "  --format <type>    session-merge 格式: conversation|structured"
    echo "  --mode <type>      watch 模式: polling|inotify"
    echo ""
    echo "示例:"
    echo "  $0 daily"
    echo "  $0 log"
    echo "  $0 watch --mode polling"
    echo "  $0 session-merge --format conversation"
}

# 执行每日归档
cmd_daily() {
    log_info "执行每日归档..."
    
    cd "$WORKSPACE_DIR"
    
    # 使用 Python 模块（优先检查根目录，再检查 modules 子目录）
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" daily
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" daily
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
    
    log_success "每日归档完成"
}

# 生成报告
cmd_report() {
    log_info "生成记忆晨报..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" report
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" report
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
    
    log_success "晨报生成完成"
}

# 健康检查
cmd_health() {
    log_info "执行健康检查..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" health
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" health
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
}

# 备份
cmd_backup() {
    log_info "执行增量备份..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" backup
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" backup
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
    
    log_success "备份完成"
}

# 生成索引
cmd_index() {
    log_info "生成记忆索引..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" index
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" index
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
    
    log_success "索引生成完成"
}

# 维护
cmd_maintenance() {
    log_info "执行清理维护..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" maintenance
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/memory_manager.py" maintenance
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
    
    log_success "维护完成"
}

# 查看状态
# 用法: run.sh status [--quiet]
# --quiet: 静默模式，减少日志输出（用于 HEARTBEAT 定时任务）
cmd_status() {
    local quiet_mode=false
    
    # 检查是否有 --quiet 参数
    for arg in "$@"; do
        if [ "$arg" = "--quiet" ]; then
            quiet_mode=true
            break
        fi
    done
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$PYTHON_MODULE_DIR/memory_manager.py" ]; then
        if [ "$quiet_mode" = true ]; then
            # 静默模式：只输出到日志文件，不输出到终端
            $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" status --quiet > /dev/null 2>&1
        else
            $PYTHON_CMD "$PYTHON_MODULE_DIR/memory_manager.py" status
        fi
    elif [ -f "$MODULES_DIR/memory_manager.py" ]; then
        if [ "$quiet_mode" = true ]; then
            $PYTHON_CMD "$MODULES_DIR/memory_manager.py" status --quiet > /dev/null 2>&1
        else
            $PYTHON_CMD "$MODULES_DIR/memory_manager.py" status
        fi
    else
        log_error "未找到 memory_manager.py"
        exit 1
    fi
}

# 记录当前对话
cmd_log() {
    log_info "记录当前对话..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$MODULES_DIR/conversation_logger.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/conversation_logger.py" --now
    else
        log_error "未找到 conversation_logger.py"
        exit 1
    fi
}

# 启动对话监控
cmd_watch() {
    local mode="${1:-polling}"
    
    log_info "启动对话监控（模式: $mode）..."
    log_info "按 Ctrl+C 停止"
    echo ""
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$MODULES_DIR/conversation_watcher.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/conversation_watcher.py" --mode "$mode"
    else
        log_error "未找到 conversation_watcher.py"
        exit 1
    fi
}

# Session 合并
cmd_session_merge() {
    local format="${1:-conversation}"
    
    log_info "合并 Sessions（格式: $format）..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$MODULES_DIR/session_extractor_unified.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/session_extractor_unified.py" --auto --format "$format"
    else
        log_error "未找到 session_extractor_unified.py"
        exit 1
    fi
}

# Session 覆盖率检查
cmd_session_check() {
    log_info "检查 Session 覆盖率..."
    
    cd "$WORKSPACE_DIR"
    
    if [ -f "$MODULES_DIR/session_extractor_unified.py" ]; then
        $PYTHON_CMD "$MODULES_DIR/session_extractor_unified.py" --check
    else
        log_error "未找到 session_extractor_unified.py"
        exit 1
    fi
}

# 主入口
main() {
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 解析命令
    # 注意：Python 检查推迟到具体命令中执行（支持静默模式）
    local skip_python_check=false
    if [ "$1" = "status" ] && [[ "$*" == *"--quiet"* ]]; then
        skip_python_check=true
    fi
    
    # 检查 Python（除非静默模式）
    if [ "$skip_python_check" = false ]; then
        check_python_with_info
    else
        check_python
    fi
    
    # 解析命令
    COMMAND="$1"
    shift
    
    case "$COMMAND" in
        daily)
            cmd_daily
            ;;
        report)
            cmd_report
            ;;
        health)
            cmd_health
            ;;
        backup)
            cmd_backup
            ;;
        index)
            cmd_index
            ;;
        maintenance)
            cmd_maintenance
            ;;
        status)
            # 传递所有参数给 cmd_status（支持 --quiet）
            cmd_status "$@"
            ;;
        log)
            cmd_log
            ;;
        watch)
            MODE="polling"
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --mode)
                        MODE="$2"
                        shift 2
                        ;;
                    *)
                        shift
                        ;;
                esac
            done
            cmd_watch "$MODE"
            ;;
        session-merge)
            FORMAT="conversation"
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --format)
                        FORMAT="$2"
                        shift 2
                        ;;
                    *)
                        shift
                        ;;
                esac
            done
            cmd_session_merge "$FORMAT"
            ;;
        session-check)
            cmd_session_check
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
