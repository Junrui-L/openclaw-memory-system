#!/usr/bin/env python3
"""
健康检查模块
检查记忆系统健康状态
"""

import os
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from . import reader


# 常量定义
class HealthConstants:
    """健康检查模块常量"""
    # 阈值
    MEMORY_FILE_WARNING_THRESHOLD = 365     # 记忆文件数量告警阈值
    PENDING_LEARNINGS_WARNING_THRESHOLD = 10  # 待处理学习记录告警阈值
    LOG_SIZE_THRESHOLD_MB = 100             # 日志大小阈值（MB）
    LOG_SIZE_THRESHOLD_BYTES = LOG_SIZE_THRESHOLD_MB * 1024 * 1024
    
    # 时间
    CRON_CHECK_HOURS = 24                   # 定时任务检查时间范围（小时）
    
    # Python 版本要求
    MIN_PYTHON_VERSION = (3, 8)             # 最低Python版本


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.paths = config.get('paths', {})
        self.disk_config = config.get('disk', {})
        self.constants = HealthConstants()
        self.reader = reader.MemoryReader(config)
    
    def check(self, config: Dict, args) -> Dict:
        """执行健康检查"""
        print("🔍 开始健康检查...")
        print()
        
        results = {
            'checks': [],
            'alerts': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. 检查日记层
        result = self._check_memory_layer()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 2. 检查身份层
        result = self._check_identity_layer()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 3. 检查任务层
        result = self._check_task_layer()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 4. 检查磁盘空间
        result = self._check_disk_space()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 5. 检查日志大小
        result = self._check_log_size()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 6. 检查备份
        result = self._check_backup()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 7. 检查定时任务执行状态
        result = self._check_cron_tasks()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 8. 检查配置文件有效性
        result = self._check_config_validity()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 9. 检查权限
        result = self._check_permissions()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 10. 检查依赖服务
        result = self._check_dependencies()
        results['checks'].append(result)
        if result.get('alert'):
            results['alerts'].append(result['alert'])
        
        # 生成报告
        self._print_summary(results)
        
        # 保存报告
        report_content = self.generate_report_text(results)
        self._save_report(report_content)
        
        # 发送告警（如果有）
        if results['alerts'] and getattr(args, 'send_alert', False):
            self._send_alerts(results['alerts'])
        
        return results
    
    def _check_memory_layer(self) -> Dict:
        """检查日记层"""
        memory_dir = Path(self.paths.get('memory', ''))
        
        if not memory_dir.exists():
            return {
                'name': '日记层',
                'status': 'error',
                'message': '记忆目录不存在',
                'alert': '❌ 日记层: 记忆目录不存在'
            }
        
        files = list(memory_dir.glob('*.md'))
        file_count = len(files)
        
        result = {
            'name': '日记层',
            'status': 'ok',
            'message': f'记忆文件: {file_count} 个',
            'details': {'count': file_count}
        }
        
        # 告警：文件过多
        if file_count > self.constants.MEMORY_FILE_WARNING_THRESHOLD:
            result['status'] = 'warning'
            result['alert'] = f'⚠️ 日记层: 记忆文件过多 ({file_count} 个)，建议归档'
        
        print(f"  ✅ 日记层: {file_count} 个记忆文件")
        return result
    
    def _check_identity_layer(self) -> Dict:
        """检查身份层"""
        si_dir = Path(self.paths.get('self_improving', ''))
        
        if not si_dir.exists():
            return {
                'name': '身份层',
                'status': 'warning',
                'message': '身份层目录不存在',
                'alert': '⚠️ 身份层: 目录不存在'
            }
        
        hot_file = si_dir / 'memory.md'
        hot_exists = hot_file.exists()
        
        result = {
            'name': '身份层',
            'status': 'ok' if hot_exists else 'warning',
            'message': f'HOT记忆: {"存在" if hot_exists else "不存在"}',
            'details': {'hot_exists': hot_exists}
        }
        
        if not hot_exists:
            result['alert'] = '⚠️ 身份层: HOT记忆文件不存在'
        
        print(f"  ✅ 身份层: HOT记忆{'存在' if hot_exists else '不存在'}")
        return result
    
    def _check_task_layer(self) -> Dict:
        """检查任务层"""
        learnings_dir = Path(self.paths.get('learnings', ''))
        
        if not learnings_dir.exists():
            return {
                'name': '任务层',
                'status': 'warning',
                'message': '学习目录不存在',
                'alert': '⚠️ 任务层: 目录不存在'
            }
        
        stats = self.reader.get_learning_stats()
        
        result = {
            'name': '任务层',
            'status': 'ok',
            'message': f'学习记录: {stats.get("total_learnings", 0)} 条',
            'details': stats
        }
        
        # 告警：待处理学习过多
        if stats.get('pending_learnings', 0) > self.constants.PENDING_LEARNINGS_WARNING_THRESHOLD:
            result['status'] = 'warning'
            result['alert'] = f'⚠️ 任务层: 有 {stats["pending_learnings"]} 条待处理学习记录'
        
        total_learnings = stats.get('total_learnings', 0)
        print(f"  ✅ 任务层: {total_learnings} 条学习记录")
        return result
    
    def _check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        workspace = Path(self.paths.get('workspace', ''))
        
        if not workspace.exists():
            return {
                'name': '磁盘空间',
                'status': 'error',
                'message': '工作区不存在',
                'alert': '❌ 磁盘空间: 工作区不存在'
            }
        
        usage = shutil.disk_usage(workspace)
        used_percent = (usage.used / usage.total) * 100
        
        warning_threshold = self.disk_config.get('warning', 80)
        critical_threshold = self.disk_config.get('critical', 90)
        
        result = {
            'name': '磁盘空间',
            'status': 'ok',
            'message': f'使用率: {used_percent:.1f}%',
            'details': {
                'used_percent': used_percent,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free
            }
        }
        
        if used_percent > critical_threshold:
            result['status'] = 'critical'
            result['alert'] = f'🔴 磁盘空间: 严重不足 ({used_percent:.1f}%)'
        elif used_percent > warning_threshold:
            result['status'] = 'warning'
            result['alert'] = f'⚠️ 磁盘空间: 使用率过高 ({used_percent:.1f}%)'
        
        print(f"  ✅ 磁盘空间: {used_percent:.1f}% 已使用")
        return result
    
    def _check_log_size(self) -> Dict:
        """检查日志大小"""
        logs_dir = Path(self.paths.get('logs', ''))
        
        if not logs_dir.exists():
            return {
                'name': '日志大小',
                'status': 'ok',
                'message': '日志目录不存在'
            }
        
        large_logs = []
        threshold = self.constants.LOG_SIZE_THRESHOLD_BYTES
        
        for log_file in logs_dir.glob('*.log'):
            size = log_file.stat().st_size
            if size > threshold:
                large_logs.append({
                    'file': log_file.name,
                    'size': size
                })
        
        result = {
            'name': '日志大小',
            'status': 'ok' if not large_logs else 'warning',
            'message': f'大日志文件: {len(large_logs)} 个',
            'details': {'large_logs': large_logs}
        }
        
        if large_logs:
            result['alert'] = f'⚠️ 日志大小: {len(large_logs)} 个日志文件超过{self.constants.LOG_SIZE_THRESHOLD_MB}MB'
        
        print(f"  ✅ 日志大小: {len(large_logs)} 个大日志文件")
        return result
    
    def _check_backup(self) -> Dict:
        """检查备份"""
        backup_dir = Path(self.paths.get('backup', ''))
        
        if not backup_dir.exists():
            return {
                'name': '备份',
                'status': 'warning',
                'message': '备份目录不存在',
                'alert': '⚠️ 备份: 目录不存在，建议配置自动备份'
            }
        
        backups = list(backup_dir.glob('*.tar.gz'))
        
        result = {
            'name': '备份',
            'status': 'ok',
            'message': f'备份文件: {len(backups)} 个',
            'details': {'count': len(backups)}
        }
        
        print(f"  ✅ 备份: {len(backups)} 个备份文件")
        return result
    
    def _check_cron_tasks(self) -> Dict:
        """检查定时任务执行状态"""
        try:
            # 检查最近的定时任务日志
            logs_dir = Path(self.paths.get('logs', ''))
            cron_logs = list(logs_dir.glob('cron-*.log')) if logs_dir.exists() else []
            
            # 检查最近24小时是否有任务执行
            recent_tasks = 0
            last_task_time = None
            
            for log_file in cron_logs:
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if datetime.now() - mtime < timedelta(hours=24):
                        recent_tasks += 1
                        if last_task_time is None or mtime > last_task_time:
                            last_task_time = mtime
                except Exception:
                    pass
            
            result = {
                'name': '定时任务',
                'status': 'ok',
                'message': f'最近24小时执行: {recent_tasks} 个任务',
                'details': {'recent_tasks': recent_tasks, 'last_task': last_task_time}
            }
            
            if recent_tasks == 0:
                result['status'] = 'warning'
                result['alert'] = '⚠️ 定时任务: 最近24小时无任务执行记录'
            
            print(f"  ✅ 定时任务: {recent_tasks} 个任务最近24小时执行")
            return result
            
        except Exception as e:
            return {
                'name': '定时任务',
                'status': 'warning',
                'message': f'检查失败: {e}',
                'alert': f'⚠️ 定时任务: 检查失败 ({e})'
            }
    
    def _check_config_validity(self) -> Dict:
        """检查配置文件有效性"""
        errors = []
        
        # 检查必要路径
        required_paths = ['workspace', 'memory', 'self_improving', 'learnings']
        for path_key in required_paths:
            path = Path(self.paths.get(path_key, ''))
            if not path.exists():
                errors.append(f"路径不存在: {path_key}")
        
        # 检查配置值
        retention_days = self.config.get('archive', {}).get('retention_days', 0)
        if retention_days <= 0:
            errors.append(f"归档保留天数无效: {retention_days}")
        
        result = {
            'name': '配置文件',
            'status': 'ok' if not errors else 'error',
            'message': '配置有效' if not errors else f'{len(errors)} 个错误',
            'details': {'errors': errors}
        }
        
        if errors:
            result['alert'] = f'❌ 配置文件: {"; ".join(errors)}'
        
        print(f"  ✅ 配置文件: {'有效' if not errors else f'{len(errors)} 个错误'}")
        return result
    
    def _check_permissions(self) -> Dict:
        """检查权限"""
        workspace = Path(self.paths.get('workspace', ''))
        issues = []
        
        # 检查工作区是否可写
        if workspace.exists():
            test_file = workspace / '.write_test'
            try:
                test_file.write_text('test')
                test_file.unlink()
            except Exception:
                issues.append('工作区不可写')
        
        # 检查关键目录权限
        for path_key in ['memory', 'self_improving', 'learnings']:
            path = Path(self.paths.get(path_key, ''))
            if path.exists():
                try:
                    # 尝试列出目录
                    list(path.iterdir())
                except Exception as e:
                    issues.append(f'{path_key} 无读取权限: {e}')
        
        result = {
            'name': '权限检查',
            'status': 'ok' if not issues else 'warning',
            'message': '权限正常' if not issues else f'{len(issues)} 个问题',
            'details': {'issues': issues}
        }
        
        if issues:
            result['alert'] = f'⚠️ 权限检查: {"; ".join(issues)}'
        
        print(f"  ✅ 权限检查: {'正常' if not issues else f'{len(issues)} 个问题'}")
        return result
    
    def _check_dependencies(self) -> Dict:
        """检查依赖服务"""
        issues = []
        
        # 检查 Python 版本
        import sys
        if sys.version_info < self.constants.MIN_PYTHON_VERSION:
            issues.append(f"Python版本过低: {sys.version} (需要 >= {'.'.join(map(str, self.constants.MIN_PYTHON_VERSION))})")
        
        # 检查关键模块
        try:
            import fcntl
        except ImportError:
            issues.append("缺少 fcntl 模块（文件锁）")
        
        # 检查 OpenClaw 命令（可选）
        try:
            result = subprocess.run(['which', 'openclaw'], capture_output=True, timeout=5)
            if result.returncode != 0:
                issues.append("openclaw 命令不可用（飞书发送将失败）")
        except Exception:
            issues.append("无法检查 openclaw 命令")
        
        result = {
            'name': '依赖服务',
            'status': 'ok' if not issues else 'warning',
            'message': '依赖正常' if not issues else f'{len(issues)} 个问题',
            'details': {'issues': issues}
        }
        
        if issues:
            result['alert'] = f'⚠️ 依赖服务: {"; ".join(issues)}'
        
        print(f"  ✅ 依赖服务: {'正常' if not issues else f'{len(issues)} 个问题'}")
        return result
    
    def _print_summary(self, results: Dict):
        """打印摘要"""
        print()
        print("=" * 50)
        print("📊 健康检查摘要")
        print("=" * 50)
        
        for check in results['checks']:
            status_icon = '✅' if check['status'] == 'ok' else '⚠️' if check['status'] == 'warning' else '❌'
            print(f"{status_icon} {check['name']}: {check['message']}")
        
        print()
        
        if results['alerts']:
            print(f"⚠️ 发现 {len(results['alerts'])} 个告警:")
            for alert in results['alerts']:
                print(f"  - {alert}")
        else:
            print("✅ 所有检查通过，系统健康！")
        
        print("=" * 50)
    
    def generate_report_text(self, results: Dict) -> str:
        """生成报告文本"""
        lines = [
            f"# 🏥 记忆系统健康报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"---",
            f"",
            f"## 📋 检查结果",
            f"",
        ]
        
        for check in results['checks']:
            status = check['status']
            icon = '✅' if status == 'ok' else '⚠️' if status == 'warning' else '❌'
            lines.append(f"{icon} **{check['name']}**: {check['message']}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        if results['alerts']:
            lines.append(f"## ⚠️ 告警 ({len(results['alerts'])} 项)")
            lines.append("")
            for alert in results['alerts']:
                lines.append(f"- {alert}")
        else:
            lines.append("✅ **系统健康，无告警**")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"*报告生成时间: {datetime.now().strftime('%H:%M')}*")
        
        return '\n'.join(lines)
    
    def _save_report(self, content: str):
        """保存报告"""
        reports_dir = Path(self.paths.get('reports', '')) / 'daily'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y-%m-%d')
        report_path = reports_dir / f"{today}-health.md"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 健康报告已保存: {report_path}")
        except Exception as e:
            print(f"⚠️ 无法保存报告: {e}")
    
    def _send_alerts(self, alerts: List[str]):
        """发送告警"""
        print()
        print("📱 发送告警通知...")
        for alert in alerts:
            print(f"  - {alert}")
        print("✅ 告警通知已发送（模拟）")
    
    def show_summary(self, config: Dict):
        """显示状态摘要"""
        stats = self.reader.get_all_stats()
        
        print("📈 记忆系统统计")
        print("-" * 40)
        print(f"记忆文件: {stats['memory']['count']} 个")
        print(f"学习记录: {stats['learnings']['total_learnings']} 条")
        print(f"待处理学习: {stats['learnings']['pending_learnings']} 条")
        print(f"错误记录: {stats['learnings']['total_errors']} 条")
        print("-" * 40)
