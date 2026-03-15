#!/usr/bin/env python3
"""
报告生成模块
生成各类报告
"""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from . import reader, analyzer


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.paths = config.get('paths', {})
        self.reader = reader.MemoryReader(config)
        self.analyzer = analyzer.MemoryAnalyzer(config)
    
    def generate_morning_report(self, config: Dict, args) -> str:
        """生成晨报"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        today_str = today.strftime('%Y-%m-%d')
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        print(f"📅 日期: {today_str}")
        print(f"📅 昨日: {yesterday_str}")
        print()
        
        # 读取昨日日记
        yesterday_content = self.reader.read_daily_memory(yesterday_str)
        yesterday_analysis = {}
        if yesterday_content:
            yesterday_analysis = {
                'todos': self.analyzer.extract_todos(yesterday_content),
                'events': self.analyzer.extract_key_events(yesterday_content),
                'lessons': self.analyzer.extract_lessons(yesterday_content),
            }
        
        # 获取学习统计
        learning_stats = self.reader.get_learning_stats()
        
        # 获取记忆统计
        memory_stats = self.reader.get_memory_stats()
        
        # 生成报告
        report_lines = [
            f"# 🌅 早上好！今日记忆日报",
            f"",
            f"📅 **日期**: {today_str} ({today.strftime('%A')})",
            f"⏰ **报告时间**: {today.strftime('%H:%M')}",
            f"",
            f"---",
            f"",
        ]
        
        # 问候语
        hour = today.hour
        if hour < 9:
            report_lines.append("☀️ **早安！新的一天开始了**")
        elif hour < 12:
            report_lines.append("🌤️ **上午好！**")
        else:
            report_lines.append("🌞 **下午好！**")
        report_lines.append("")
        
        # 昨日回顾
        report_lines.extend([
            f"## 📊 昨日回顾 ({yesterday_str})",
            f"",
        ])
        
        if yesterday_content:
            report_lines.append(f"✅ 昨日有记忆记录")
            report_lines.append(f"- 📝 关键事件: {len(yesterday_analysis.get('events', []))} 项")
            report_lines.append(f"- ⏰ 待办事项: {len(yesterday_analysis.get('todos', []))} 项")
            report_lines.append(f"- 💡 经验教训: {len(yesterday_analysis.get('lessons', []))} 条")
        else:
            report_lines.append(f"⚠️ 昨日无记忆记录")
        
        report_lines.append("")
        
        # 学习统计
        report_lines.extend([
            f"## 📈 学习统计",
            f"",
            f"- 📚 学习记录: {learning_stats.get('total_learnings', 0)} 条",
            f"  - 待处理: {learning_stats.get('pending_learnings', 0)} 条",
            f"  - 已解决: {learning_stats.get('resolved_learnings', 0)} 条",
            f"- ❌ 错误记录: {learning_stats.get('total_errors', 0)} 条",
            f"",
        ])
        
        # 待办提醒
        report_lines.extend([
            f"## ⏰ 待办提醒",
            f"",
        ])
        
        pending_todos = yesterday_analysis.get('todos', [])
        if pending_todos:
            report_lines.append(f"**共 {len(pending_todos)} 项待办（从昨日继承）:**")
            report_lines.append("")
            
            # 按优先级分组
            high = [t for t in pending_todos if t.get('priority') == 'high']
            medium = [t for t in pending_todos if t.get('priority') == 'medium']
            low = [t for t in pending_todos if t.get('priority') in ['low', 'normal']]
            
            if high:
                report_lines.append("🔴 **高优先级:**")
                for todo in high[:3]:
                    report_lines.append(f"- {todo.get('text', '')}")
                report_lines.append("")
            
            if medium:
                report_lines.append("🟡 **中优先级:**")
                for todo in medium[:3]:
                    report_lines.append(f"- {todo.get('text', '')}")
                report_lines.append("")
            
            if low:
                report_lines.append("🟢 **低优先级:**")
                for todo in low[:2]:
                    report_lines.append(f"- {todo.get('text', '')}")
                report_lines.append("")
        else:
            report_lines.append("✨ **无待办事项，轻松的一天！**")
        
        report_lines.append("")
        
        # 今日建议
        report_lines.extend([
            f"## 🎯 今日建议",
            f"",
        ])
        
        suggestions = []
        if len(pending_todos) > 5:
            suggestions.append("- 待办较多，建议优先处理高优先级事项")
        elif len(pending_todos) > 0:
            suggestions.append("- 有少量待办，可以从容处理")
        else:
            suggestions.append("- 没有待办，可以专注于新任务")
        
        if learning_stats.get('pending_learnings', 0) > 3:
            suggestions.append("- 有未处理的学习记录，建议回顾")
        
        if memory_stats.get('count', 0) > 30:
            suggestions.append("- 记忆文件较多，建议定期归档")
        
        report_lines.extend(suggestions)
        report_lines.append("")
        
        # 结尾
        report_lines.extend([
            f"---",
            f"",
            f"💪 **祝你今天工作顺利！**",
            f"",
            f"*报告生成时间: {today.strftime('%H:%M')}*",
            f"*记忆文件数: {memory_stats.get('count', 0)}*",
        ])
        
        report_content = '\n'.join(report_lines)
        
        # 保存报告
        reports_dir = Path(self.paths.get('reports', '')) / 'daily'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / f"{today_str}-morning.md"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ 报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 无法保存报告: {e}")
        
        # 发送到飞书（如果启用）
        if getattr(args, 'send_feishu', False) or self.config.get('notification', {}).get('feishu', {}).get('morning_report', False):
            self._send_to_feishu(report_content)
        
        return report_content
    
    def _send_to_feishu(self, content: str):
        """发送到飞书"""
        print()
        print("📱 发送到飞书...")
        
        # 获取飞书配置
        feishu_config = self.config.get('notification', {}).get('feishu', {})
        target = feishu_config.get('target', 'oc_f55bc4b692dd99d18ba8b46d73e902cb')  # 默认发送到记忆管理群组
        
        try:
            # 使用 OpenClaw 的 message 工具发送
            # 截取前 2000 字符（飞书消息长度限制）
            message_text = content[:2000] if len(content) > 2000 else content
            
            # 构建命令
            cmd = [
                'message', 'send',
                '--channel', 'feishu',
                '--target', target,
                '--message', message_text
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ 飞书通知已发送到: {target}")
            else:
                print(f"⚠️ 飞书发送失败: {result.stderr}")
                # 降级到打印模式
                self._print_report_preview(content)
                
        except subprocess.TimeoutExpired:
            print("⚠️ 飞书发送超时")
            self._print_report_preview(content)
        except Exception as e:
            print(f"⚠️ 飞书发送异常: {e}")
            self._print_report_preview(content)
    
    def _print_report_preview(self, content: str):
        """打印报告预览（降级方案）"""
        print()
        print("报告内容预览:")
        print("-" * 40)
        preview = content[:500] + "..." if len(content) > 500 else content
        print(preview)
        print("-" * 40)
    
    def generate_health_report(self, config: Dict, args) -> str:
        """生成健康报告"""
        from . import health
        
        health_checker = health.HealthChecker(config)
        return health_checker.generate_report(args)
