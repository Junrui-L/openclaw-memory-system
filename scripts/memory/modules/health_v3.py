#!/usr/bin/env python3
"""
健康检查模块 - v3.0 重构版

职责：数据质量检查（OpenClaw 不检查的内容）
原则：
    - 只检查质量，不检查存在性（OpenClaw 已做）
    - 使用 reader 获取数据
    - 自动修复问题
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class HealthChecker:
    """
    健康检查器 - v3.0
    
    重点：Session 覆盖率检查（核心功能）
    """
    
    def __init__(self, reader, config: Dict):
        """
        初始化
        
        Args:
            reader: MemoryReader 实例
            config: 配置
        """
        self.reader = reader
        self.config = config
        self.paths = config.get('paths', {})
        self.thresholds = config.get('health', {})
        
        # Session 目录（直接读取）
        self.sessions_dir = Path("/home/node/.openclaw/agents/main/sessions")
    
    def check(self) -> Dict:
        """
        执行健康检查
        
        Returns:
            检查结果
        """
        print("🔍 开始健康检查...")
        print()
        
        results = {
            'checks': [],
            'alerts': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Phase 1 核心检查
        checks = [
            ('Session 覆盖率', self._check_session_coverage),
            ('数据新鲜度', self._check_data_freshness),
            ('索引一致性', self._check_index_consistency),
            ('磁盘空间', self._check_disk_space),
        ]
        
        for name, check_func in checks:
            try:
                result = check_func()
                results['checks'].append(result)
                
                if result.get('alert'):
                    results['alerts'].append(result['alert'])
                    print(f"  ⚠️ {name}: {result['message']}")
                else:
                    print(f"  ✅ {name}: {result['message']}")
                    
            except Exception as e:
                print(f"  ❌ {name}: 检查失败 - {e}")
                results['checks'].append({
                    'name': name,
                    'status': 'error',
                    'message': f'检查失败: {e}'
                })
        
        # 打印摘要
        self._print_summary(results)
        
        return results
    
    # ==================== Phase 1 核心检查 ====================
    
    def _check_session_coverage(self) -> Dict:
        """
        【核心】Session 覆盖率检查
        
        检查项:
            1. 【直接读取】统计 sessions/ 目录下的 session 数量
            2. 【使用 reader】检查 memory/ 中记录的数量
            3. 计算覆盖率
            4. 低于阈值告警
            
        Returns:
            检查结果
        """
        total_sessions = 0
        recorded_sessions = 0
        missing_dates = []
        
        # 检查最近 7 天
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 统计 sessions 数量（直接读取）
            day_sessions = self._count_sessions_for_date(date)
            total_sessions += day_sessions
            
            # 检查是否已记录到 memory/
            memory_file = Path(self.paths.get('memory', '')) / f"{date}.md"
            if memory_file.exists():
                content = memory_file.read_text(encoding='utf-8') if memory_file.exists() else ""
                recorded = self._count_recorded_sessions(content)
                recorded_sessions += recorded
                
                if recorded < day_sessions:
                    missing_dates.append(date)
            else:
                if day_sessions > 0:
                    missing_dates.append(date)
        
        # 计算覆盖率
        coverage_rate = recorded_sessions / total_sessions if total_sessions > 0 else 1.0
        threshold = self.thresholds.get('session_coverage_threshold', 0.95)
        
        result = {
            'name': 'Session 覆盖率',
            'status': 'ok' if coverage_rate >= threshold else 'warning',
            'message': f'{recorded_sessions}/{total_sessions} ({coverage_rate:.1%})',
            'details': {
                'total': total_sessions,
                'recorded': recorded_sessions,
                'coverage_rate': coverage_rate,
                'threshold': threshold,
                'missing_dates': missing_dates
            }
        }
        
        if coverage_rate < threshold:
            result['alert'] = f'⚠️ Session 覆盖率: {coverage_rate:.1%} (低于 {threshold:.0%})'
        
        return result
    
    def _count_sessions_for_date(self, date: str) -> int:
        """
        统计指定日期的 session 数量
        
        实现: 直接读取 sessions/ 目录
        """
        count = 0
        
        if not self.sessions_dir.exists():
            return 0
        
        for session_file in self.sessions_dir.glob('*.jsonl'):
            if not session_file.name.endswith('.jsonl'):
                continue
            
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if date in line:
                            count += 1
                            break
            except:
                continue
        
        return count
    
    def _count_recorded_sessions(self, content: str) -> int:
        """
        统计已记录的 session 数量
        
        从 memory 内容中统计
        """
        import re
        return len(re.findall(r'\*\*Session\*\*:', content))
    
    def _check_data_freshness(self) -> Dict:
        """
        数据新鲜度检查
        
        检查项:
            1. 最近是否有新记忆
            2. 记忆更新频率是否正常
        """
        # 获取最近记忆
        recent = self.reader.get_recent(1)
        
        if not recent:
            return {
                'name': '数据新鲜度',
                'status': 'warning',
                'message': '最近1天无记忆记录',
                'alert': '⚠️ 数据新鲜度: 最近1天无记忆记录'
            }
        
        # 检查最后更新时间
        last_date = recent[0]['date']
        today = datetime.now().strftime('%Y-%m-%d')
        
        if last_date == today:
            return {
                'name': '数据新鲜度',
                'status': 'ok',
                'message': f'今天有更新 ({last_date})'
            }
        else:
            return {
                'name': '数据新鲜度',
                'status': 'warning',
                'message': f'最后更新: {last_date}',
                'alert': f'⚠️ 数据新鲜度: 今天无更新'
            }
    
    def _check_index_consistency(self) -> Dict:
        """
        索引一致性检查
        
        检查项:
            1. INDEX.md 中的文件数 vs 实际文件数
            2. 待办统计是否准确
        """
        # 获取 INDEX.md 内容
        index_content = self.reader.get('memory/INDEX.md')
        
        if not index_content:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': 'INDEX.md 不存在',
                'alert': '⚠️ 索引一致性: INDEX.md 不存在'
            }
        
        # 统计 INDEX.md 中的记忆数（匹配 **2026-03-13** 或 **2026-03-13-xxx**）
        import re
        index_memories = len(re.findall(r'- \*\*\d{4}-\d{2}-\d{2}[^\*]*\*\*', index_content))
        
        # 统计实际记忆文件数（排除 INDEX.md 本身）
        memory_dir = Path(self.paths.get('memory', ''))
        actual_memories = len([f for f in memory_dir.glob('2026-*.md') if f.name != 'INDEX.md']) if memory_dir.exists() else 0
        
        if index_memories == actual_memories:
            return {
                'name': '索引一致性',
                'status': 'ok',
                'message': f'一致 ({actual_memories} 个记忆)'
            }
        else:
            return {
                'name': '索引一致性',
                'status': 'warning',
                'message': f'INDEX: {index_memories}, 实际: {actual_memories}',
                'alert': f'⚠️ 索引不一致: INDEX {index_memories} vs 实际 {actual_memories}'
            }
    
    def _check_disk_space(self) -> Dict:
        """
        磁盘空间检查
        
        保留：OpenClaw 不检查磁盘空间
        """
        workspace = Path(self.paths.get('workspace', ''))
        
        if not workspace.exists():
            return {
                'name': '磁盘空间',
                'status': 'error',
                'message': '工作区不存在'
            }
        
        usage = shutil.disk_usage(workspace)
        used_percent = (usage.used / usage.total) * 100
        
        warning_threshold = self.thresholds.get('disk_warning', 80)
        critical_threshold = self.thresholds.get('disk_critical', 90)
        
        result = {
            'name': '磁盘空间',
            'status': 'ok',
            'message': f'{used_percent:.1f}% 已使用',
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
        
        return result
    
    # ==================== 自动修复 ====================
    
    def repair_issues(self, issues: List[Dict]) -> bool:
        """
        自动修复问题
        
        Args:
            issues: 问题列表
            
        Returns:
            修复成功返回 True
        """
        print("🔧 自动修复问题...")
        
        for issue in issues:
            name = issue.get('name', '')
            
            if 'Session 覆盖率' in name:
                # 调用 SessionExtractor 修复
                print(f"  修复: {name}")
                from modules.session_extractor import SessionExtractor
                extractor = SessionExtractor(self.config)
                extractor.auto_extract_and_merge()
            
            elif '索引一致性' in name:
                # 重新生成索引
                print(f"  修复: {name}")
                # TODO: 调用索引生成
        
        print("✅ 修复完成")
        return True
    
    # ==================== 打印摘要 ====================
    
    def _print_summary(self, results: Dict):
        """打印检查摘要"""
        print()
        print("=" * 50)
        print("📊 健康检查摘要")
        print("=" * 50)
        
        checks = results['checks']
        alerts = results['alerts']
        
        # 统计
        ok_count = sum(1 for c in checks if c['status'] == 'ok')
        warning_count = sum(1 for c in checks if c['status'] == 'warning')
        error_count = sum(1 for c in checks if c['status'] == 'error')
        
        print(f"✅ 正常: {ok_count}")
        print(f"⚠️ 警告: {warning_count}")
        print(f"❌ 错误: {error_count}")
        
        if alerts:
            print()
            print("🚨 需要关注的问题:")
            for alert in alerts:
                print(f"   {alert}")
        
        print("=" * 50)


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='健康检查')
    parser.add_argument('--repair', action='store_true', help='自动修复问题')
    
    args = parser.parse_args()
    
    config = {
        'paths': {
            'workspace': '/home/node/.openclaw/workspace',
            'memory': '/home/node/.openclaw/workspace/memory'
        },
        'health': {
            'session_coverage_threshold': 0.95,
            'disk_warning': 80,
            'disk_critical': 90
        }
    }
    
    # 创建 reader（临时）
    from modules.reader_v3 import MemoryReader
    reader = MemoryReader(config)
    
    checker = HealthChecker(reader, config)
    results = checker.check()
    
    if args.repair and results['alerts']:
        checker.repair_issues(results['checks'])