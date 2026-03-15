#!/bin/bash
# 记忆管理系统 - Bash入口脚本
# 用法: run.sh <command> [options]

set -e

# 设置路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$(dirname "$SCRIPT_DIR")")"
PYTHON="/usr/bin/python3"

# 锁文件路径
LOCK_FILE="/tmp/memory-manager.lock"
LOCK_TIMEOUT=300  # 5分钟超时

# 获取锁函数
acquire_lock() {
    local lock_fd
    exec {lock_fd}>"$LOCK_FILE" 2>/dev/null || {
        echo "❌ 无法创建锁文件"
        exit 1
    }
    
    # 尝试获取锁（非阻塞）
    if flock -n $lock_fd 2>/dev/null; then
        # 保存 fd 以便后续释放
        export LOCK_FD=$lock_fd
        return 0
    fi
    
    # 检查锁是否超时
    local lock_age=$(stat -c %Y "$LOCK_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local age_diff=$((current_time - lock_age))
    
    if [ $age_diff -gt $LOCK_TIMEOUT ]; then
        echo "⚠️ 检测到超时锁 (${age_diff}s)，强制获取..."
        flock -x $lock_fd 2>/dev/null
        export LOCK_FD=$lock_fd
        return 0
    fi
    
    echo "⏳ 另一个实例正在运行，等待 ${age_diff}s..."
    # 等待锁（阻塞，但有超时）
    if flock -w $LOCK_TIMEOUT $lock_fd 2>/dev/null; then
        export LOCK_FD=$lock_fd
        return 0
    fi
    
    echo "❌ 获取锁超时"
    exit 1
}

# 释放锁函数
release_lock() {
    if [ -n "$LOCK_FD" ]; then
        exec {LOCK_FD}<&- 2>/dev/null || true
        rm -f "$LOCK_FILE" 2>/dev/null || true
    fi
}

# 设置退出时释放锁
trap release_lock EXIT

# 获取锁
acquire_lock

# 颜色输出
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# 日志函数
log_info() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} ⚠️ $1"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} ❌ $1"
}

log_info "========================================"
log_info "🚀 记忆管理系统"
log_info "========================================"
log_info ""

# 检查Python
if ! command -v $PYTHON &> /dev/null; then
    log_error "Python3 未安装"
    exit 1
fi

log_info "✅ Python3 已安装"

# 检查依赖（可选，容器内可能无pip）
if [ ! -f "$SCRIPT_DIR/.deps_installed" ]; then
    if command -v pip3 &> /dev/null; then
        log_info "📦 安装Python依赖..."
        if pip3 install -r "$SCRIPT_DIR/requirements.txt" -q 2>/dev/null; then
            touch "$SCRIPT_DIR/.deps_installed"
            log_info "✅ 依赖安装完成"
        else
            log_warn "依赖安装失败，使用内置功能..."
        fi
    else
        log_info "ℹ️ pip3 不可用，使用内置功能"
    fi
else
    log_info "✅ 依赖已安装"
fi

log_info ""
log_info "▶️ 执行Python程序..."
log_info ""

# 执行Python
cd "$WORKSPACE"
$PYTHON "$SCRIPT_DIR/memory_manager.py" "$@"
