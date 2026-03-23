#!/bin/bash
# 日志查询工具 - 方便查看和管理记忆管理系统日志

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="/home/node/.openclaw/workspace/logs"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo "日志查询工具"
    echo ""
    echo "用法: $0 <命令> [选项]"
    echo ""
    echo "命令:"
    echo "  today                    查看今天的日志"
    echo "  yesterday                查看昨天的日志"
    echo "  date <YYYY-MM-DD>        查看指定日期的日志"
    echo "  task <task-name>         查看指定任务的日志"
    echo "  tasks                    列出所有任务日志"
    echo "  latest [n]               查看最新 n 条日志 (默认 20)"
    echo "  search <keyword>         搜索日志关键词"
    echo "  summary                  日志统计摘要"
    echo "  clean                    清理旧日志文件"
    echo ""
    echo "示例:"
    echo "  $0 today"
    echo "  $0 date 2026-03-17"
    echo "  $0 task report"
    echo "  $0 latest 50"
    echo "  $0 search '晨报生成'"
}

# 查看今天的日志
cmd_today() {
    local today=$(date +%Y-%m-%d)
    local log_file="$LOGS_DIR/daily/$today.log"
    
    if [ -f "$log_file" ]; then
        echo -e "${GREEN}📅 今日日志 ($today):${NC}"
        echo "================================"
        cat "$log_file"
    else
        echo -e "${YELLOW}⚠️ 今日日志不存在: $log_file${NC}"
        # 尝试从主日志中提取今日记录
        if [ -f "$LOGS_DIR/memory_manager.log" ]; then
            echo -e "${BLUE}ℹ️ 从主日志提取今日记录:${NC}"
            grep "^\[$today" "$LOGS_DIR/memory_manager.log" 2>/dev/null || echo "无今日记录"
        fi
    fi
}

# 查看昨天的日志
cmd_yesterday() {
    local yesterday=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
    local log_file="$LOGS_DIR/daily/$yesterday.log"
    
    if [ -f "$log_file" ]; then
        echo -e "${GREEN}📅 昨日日志 ($yesterday):${NC}"
        echo "================================"
        cat "$log_file"
    else
        echo -e "${YELLOW}⚠️ 昨日日志不存在${NC}"
    fi
}

# 查看指定日期的日志
cmd_date() {
    local date_str="$1"
    if [ -z "$date_str" ]; then
        echo -e "${YELLOW}⚠️ 请指定日期，格式: YYYY-MM-DD${NC}"
        exit 1
    fi
    
    local log_file="$LOGS_DIR/daily/$date_str.log"
    
    if [ -f "$log_file" ]; then
        echo -e "${GREEN}📅 $date_str 的日志:${NC}"
        echo "================================"
        cat "$log_file"
    else
        echo -e "${YELLOW}⚠️ 该日期日志不存在: $log_file${NC}"
    fi
}

# 查看指定任务的日志
cmd_task() {
    local task_name="$1"
    if [ -z "$task_name" ]; then
        echo -e "${YELLOW}⚠️ 请指定任务名${NC}"
        echo "可用任务:"
        cmd_tasks
        exit 1
    fi
    
    local log_file="$LOGS_DIR/tasks/$task_name.log"
    
    if [ -f "$log_file" ]; then
        echo -e "${GREEN}📋 任务 '$task_name' 的日志:${NC}"
        echo "================================"
        cat "$log_file"
    else
        echo -e "${YELLOW}⚠️ 该任务日志不存在: $log_file${NC}"
    fi
}

# 列出所有任务日志
cmd_tasks() {
    echo -e "${GREEN}📋 可用任务日志:${NC}"
    echo "================================"
    
    if [ -d "$LOGS_DIR/tasks" ]; then
        for f in "$LOGS_DIR/tasks"/*.log; do
            if [ -f "$f" ]; then
                local task_name=$(basename "$f" .log)
                local size=$(du -h "$f" | cut -f1)
                local lines=$(wc -l < "$f")
                echo -e "  ${BLUE}$task_name${NC} (${size}, ${lines} 行)"
            fi
        done
    else
        echo "  暂无任务日志"
    fi
}

# 查看最新日志
cmd_latest() {
    local n="${1:-20}"
    echo -e "${GREEN}📄 最新 $n 条日志:${NC}"
    echo "================================"
    
    if [ -f "$LOGS_DIR/memory_manager.log" ]; then
        tail -n "$n" "$LOGS_DIR/memory_manager.log"
    else
        echo -e "${YELLOW}⚠️ 主日志文件不存在${NC}"
    fi
}

# 搜索日志
cmd_search() {
    local keyword="$1"
    if [ -z "$keyword" ]; then
        echo -e "${YELLOW}⚠️ 请指定搜索关键词${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🔍 搜索 '$keyword':${NC}"
    echo "================================"
    
    # 搜索所有日志文件
    if [ -d "$LOGS_DIR/daily" ]; then
        grep -r "$keyword" "$LOGS_DIR/daily" 2>/dev/null | head -50
    fi
    
    if [ -d "$LOGS_DIR/tasks" ]; then
        grep -r "$keyword" "$LOGS_DIR/tasks" 2>/dev/null | head -50
    fi
    
    grep "$keyword" "$LOGS_DIR/memory_manager.log" 2>/dev/null | tail -20
}

# 日志统计摘要
cmd_summary() {
    echo -e "${GREEN}📊 日志统计摘要:${NC}"
    echo "================================"
    echo ""
    
    # 主日志
    if [ -f "$LOGS_DIR/memory_manager.log" ]; then
        local main_size=$(du -h "$LOGS_DIR/memory_manager.log" | cut -f1)
        local main_lines=$(wc -l < "$LOGS_DIR/memory_manager.log")
        echo -e "主日志文件:"
        echo -e "  ${BLUE}memory_manager.log${NC} - ${main_size}, ${main_lines} 行"
        echo ""
    fi
    
    # 每日日志
    if [ -d "$LOGS_DIR/daily" ]; then
        local daily_count=$(ls -1 "$LOGS_DIR/daily"/*.log 2>/dev/null | wc -l)
        local daily_size=$(du -sh "$LOGS_DIR/daily" 2>/dev/null | cut -f1)
        echo -e "每日日志:"
        echo -e "  文件数: ${BLUE}$daily_count${NC}"
        echo -e "  总大小: ${BLUE}$daily_size${NC}"
        echo ""
    fi
    
    # 任务日志
    if [ -d "$LOGS_DIR/tasks" ]; then
        local task_count=$(ls -1 "$LOGS_DIR/tasks"/*.log 2>/dev/null | wc -l)
        local task_size=$(du -sh "$LOGS_DIR/tasks" 2>/dev/null | cut -f1)
        echo -e "任务日志:"
        echo -e "  文件数: ${BLUE}$task_count${NC}"
        echo -e "  总大小: ${BLUE}$task_size${NC}"
        echo ""
    fi
    
    # 最近7天活动统计
    echo -e "最近7天活动统计:"
    for i in {0..6}; do
        local d=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d)
        local log_file="$LOGS_DIR/daily/$d.log"
        if [ -f "$log_file" ]; then
            local count=$(grep -c "命令.*执行完成" "$log_file" 2>/dev/null || echo "0")
            echo -e "  ${BLUE}$d${NC}: $count 个任务"
        fi
    done
}

# 清理旧日志
cmd_clean() {
    echo -e "${GREEN}🧹 清理旧日志:${NC}"
    echo "================================"
    
    # 清理7天前的每日日志
    local deleted=0
    if [ -d "$LOGS_DIR/daily" ]; then
        for f in "$LOGS_DIR/daily"/*.log; do
            if [ -f "$f" ]; then
                local filename=$(basename "$f" .log)
                # 检查是否为7天前的日期
                local file_date=$(date -d "$filename" +%s 2>/dev/null || echo "0")
                local week_ago=$(date -d "7 days ago" +%s 2>/dev/null || date -v-7d +%s)
                
                if [ "$file_date" != "0" ] && [ "$file_date" -lt "$week_ago" ]; then
                    rm "$f"
                    echo "  已删除: $filename.log"
                    ((deleted++))
                fi
            fi
        done
    fi
    
    if [ $deleted -eq 0 ]; then
        echo "  没有需要清理的旧日志"
    else
        echo "  共清理 $deleted 个文件"
    fi
}

# 主入口
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    COMMAND="$1"
    shift
    
    case "$COMMAND" in
        today)
            cmd_today
            ;;
        yesterday)
            cmd_yesterday
            ;;
        date)
            cmd_date "$1"
            ;;
        task)
            cmd_task "$1"
            ;;
        tasks)
            cmd_tasks
            ;;
        latest)
            cmd_latest "$1"
            ;;
        search)
            cmd_search "$1"
            ;;
        summary)
            cmd_summary
            ;;
        clean)
            cmd_clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${YELLOW}⚠️ 未知命令: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
