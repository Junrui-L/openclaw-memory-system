#!/usr/bin/env python3
"""
Self-Improvement 自动化 Hook
自动检测并记录学习、错误和纠正
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

class SelfImprovementHook:
    """自动化自我改进钩子"""
    
    def __init__(self, workspace_dir: str = "/home/node/.openclaw/workspace"):
        self.workspace = Path(workspace_dir)
        self.learnings_dir = self.workspace / ".learnings"
        self.self_improving_dir = self.workspace / "self-improving"
        
        # 确保目录存在
        self.learnings_dir.mkdir(exist_ok=True)
        self.self_improving_dir.mkdir(exist_ok=True)
        
        # 文件路径
        self.learnings_file = self.learnings_dir / "LEARNINGS.md"
        self.errors_file = self.learnings_dir / "ERRORS.md"
        self.features_file = self.learnings_dir / "FEATURE_REQUESTS.md"
        self.corrections_file = self.self_improving_dir / "corrections.md"
        self.reflections_file = self.self_improving_dir / "reflections.md"
    
    def generate_id(self, prefix: str) -> str:
        """生成 ID: TYPE-YYYYMMDD-XXX"""
        date_str = datetime.now().strftime("%Y%m%d")
        # 简单序号
        return f"{prefix}-{date_str}-001"
    
    def get_timestamp(self) -> str:
        """获取 ISO 格式时间戳"""
        return datetime.now().isoformat()
    
    def append_to_file(self, filepath: Path, content: str):
        """追加内容到文件"""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content + "\n\n---\n\n")
    
    # ==================== 检测方法 ====================
    
    def detect_correction(self, user_message: str) -> Optional[Dict]:
        """检测用户纠正"""
        correction_patterns = [
            r"不对",
            r"错了",
            r"不是这样",
            r"actually[,.]?\s*(that'?s?\s*(not|wrong)|no[,.])",
            r"no[,.'\s]+that'?s?\s*(not|wrong)",
            r"你理解错了",
            r"搞反了",
            r"方向错了",
        ]
        
        for pattern in correction_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                return {
                    "type": "correction",
                    "trigger": re.search(pattern, user_message, re.IGNORECASE).group(),
                    "message": user_message
                }
        return None
    
    def detect_feature_request(self, user_message: str) -> Optional[Dict]:
        """检测功能请求"""
        feature_patterns = [
            r"能(不能|否).*吗",
            r"可以.*吗",
            r"希望.*可以",
            r"想要.*功能",
            r"i wish you could",
            r"can you (also|also make)",
            r"is there a way to",
            r"why can't you",
        ]
        
        for pattern in feature_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                return {
                    "type": "feature_request",
                    "trigger": re.search(pattern, user_message, re.IGNORECASE).group(),
                    "message": user_message
                }
        return None
    
    def detect_error(self, tool_result: Dict) -> Optional[Dict]:
        """检测工具执行错误"""
        # 检查 exec 命令的错误
        if tool_result.get("tool") == "exec":
            exit_code = tool_result.get("exit_code", 0)
            stderr = tool_result.get("stderr", "")
            
            if exit_code != 0 or stderr:
                return {
                    "type": "error",
                    "command": tool_result.get("command", ""),
                    "exit_code": exit_code,
                    "stderr": stderr[:500],  # 限制长度
                    "stdout": tool_result.get("stdout", "")[:500]
                }
        
        # 检查其他工具的错误
        if "error" in tool_result:
            return {
                "type": "error",
                "tool": tool_result.get("tool"),
                "error": str(tool_result.get("error", ""))[:500]
            }
        
        return None
    
    # ==================== 记录方法 ====================
    
    def log_correction(self, correction_info: Dict, context: str = ""):
        """记录用户纠正"""
        entry = f"""## {self.generate_id("LRN")} correction

**Logged**: {self.get_timestamp()}
**Priority**: high
**Status**: pending
**Area**: general

### Summary
用户纠正：{correction_info['trigger']}

### Details
**用户原话**: {correction_info['message'][:200]}
**上下文**: {context[:300] if context else '无'}

### Suggested Action
- 确认理解正确
- 修正错误
- 记录正确做法

### Metadata
- Source: user_feedback
- Related Files: 
- Tags: correction

---
"""
        self.append_to_file(self.learnings_file, entry)
        
        # 同时记录到快速纠正文件
        quick_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {correction_info['message'][:100]}"
        with open(self.corrections_file, "a", encoding="utf-8") as f:
            f.write(quick_entry + "\n")
        
        return True
    
    def log_error(self, error_info: Dict, context: str = ""):
        """记录错误"""
        entry = f"""## {self.generate_id("ERR")} {error_info.get('tool', 'command')}

**Logged**: {self.get_timestamp()}
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
命令/工具执行失败

### Error
```
{error_info.get('stderr', error_info.get('error', 'Unknown error'))}
```

### Context
- Command: {error_info.get('command', 'N/A')}
- Exit Code: {error_info.get('exit_code', 'N/A')}

### Suggested Fix
- 检查命令语法
- 检查环境配置
- 查看错误日志

### Metadata
- Reproducible: unknown
- Related Files: 

---
"""
        self.append_to_file(self.errors_file, entry)
        return True
    
    def log_feature_request(self, feature_info: Dict, context: str = ""):
        """记录功能请求"""
        entry = f"""## {self.generate_id("FEAT")} feature_request

**Logged**: {self.get_timestamp()}
**Priority**: medium
**Status**: pending
**Area**: general

### Requested Capability
{feature_info['message'][:200]}

### User Context
用户希望实现某个功能

### Complexity Estimate
medium

### Suggested Implementation
- 分析需求
- 设计方案
- 实现功能

### Metadata
- Frequency: first_time
- Related Features: 

---
"""
        self.append_to_file(self.features_file, entry)
        return True
    
    def log_reflection(self, task_summary: str, lessons_learned: str):
        """记录任务反思"""
        entry = f"""### {datetime.now().strftime('%Y-%m-%d %H:%M')} - {task_summary[:50]}

**CONTEXT**: {task_summary}
**REFLECTION**: {lessons_learned}
**LESSON**: 下次改进方向

---
"""
        with open(self.reflections_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        return True
    
    # ==================== 主检测方法 ====================
    
    def check_and_log(self, user_message: str = "", tool_results: List[Dict] = None, context: str = ""):
        """
        主检测入口
        
        Args:
            user_message: 用户最新消息
            tool_results: 工具执行结果列表
            context: 上下文信息
        """
        logs_created = []
        
        # 1. 检测用户纠正
        if user_message:
            correction = self.detect_correction(user_message)
            if correction:
                self.log_correction(correction, context)
                logs_created.append("correction")
            
            # 2. 检测功能请求
            feature = self.detect_feature_request(user_message)
            if feature:
                self.log_feature_request(feature, context)
                logs_created.append("feature_request")
        
        # 3. 检测工具错误
        if tool_results:
            for result in tool_results:
                error = self.detect_error(result)
                if error:
                    self.log_error(error, context)
                    logs_created.append("error")
        
        return logs_created


# ==================== 便捷函数 ====================

def check_and_log(user_message: str = "", tool_results: List[Dict] = None, context: str = "") -> List[str]:
    """便捷函数：检测并记录"""
    hook = SelfImprovementHook()
    return hook.check_and_log(user_message, tool_results, context)

def log_correction(message: str, context: str = ""):
    """便捷函数：记录纠正"""
    hook = SelfImprovementHook()
    info = {"type": "correction", "trigger": "manual", "message": message}
    return hook.log_correction(info, context)

def log_error(command: str, stderr: str, exit_code: int = 1):
    """便捷函数：记录错误"""
    hook = SelfImprovementHook()
    info = {
        "type": "error",
        "tool": "exec",
        "command": command,
        "stderr": stderr,
        "exit_code": exit_code
    }
    return hook.log_error(info)

def log_reflection(task_summary: str, lessons_learned: str):
    """便捷函数：记录反思"""
    hook = SelfImprovementHook()
    return hook.log_reflection(task_summary, lessons_learned)


if __name__ == "__main__":
    # 测试
    print("Self-Improvement Hook 测试")
    
    hook = SelfImprovementHook()
    
    # 测试纠正检测
    test_msg = "不对，你理解错了，应该是这样"
    result = hook.detect_correction(test_msg)
    print(f"纠正检测: {result}")
    
    # 测试功能请求检测
    test_msg2 = "能不能添加一个自动备份功能？"
    result2 = hook.detect_feature_request(test_msg2)
    print(f"功能请求检测: {result2}")
