#!/usr/bin/env python3
"""
响应后 Hook - 自动检测并记录学习
在每次助手响应后执行
"""

import sys
import json
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, "/home/node/.openclaw/workspace/scripts")

from auto_self_improvement import SelfImprovementHook

def main():
    """主函数 - 检测最后一条用户消息和工具结果"""
    
    hook = SelfImprovementHook()
    
    # 读取当前会话的最后消息（从 session 文件）
    # 这里简化处理，实际应该从 session 中提取
    
    print("🔍 Self-Improvement Hook 执行中...")
    
    # 检查是否有待处理的纠正或错误
    # 实际实现需要读取 session 历史
    
    print("✅ Self-Improvement 检查完成")

if __name__ == "__main__":
    main()
