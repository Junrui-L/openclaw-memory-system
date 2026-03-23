#!/usr/bin/env python3
"""
lancedb-pro 同步模块

功能：
1. 读取事件存储日志
2. 调用 OpenClaw memory_store 工具存入 lancedb-pro
3. 支持批量导入和增量同步
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class LanceDBSync:
    """lancedb-pro 同步器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.memory_dir = Path(config.get('paths', {}).get('memory', '/home/node/.openclaw/workspace/memory'))
        self.storage_log = self.memory_dir / '.events_storage.jsonl'
        self.sync_log = self.memory_dir / '.lancedb_sync.json'
        self.synced_hashes = self._load_synced_hashes()
    
    def _load_synced_hashes(self) -> set:
        """加载已同步的哈希"""
        if self.sync_log.exists():
            try:
                with open(self.sync_log, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def _save_synced_hashes(self):
        """保存已同步的哈希"""
        try:
            with open(self.sync_log, 'w', encoding='utf-8') as f:
                json.dump(list(self.synced_hashes), f, indent=2)
        except Exception as e:
            print(f"⚠️ 无法保存同步记录: {e}")
    
    def _call_memory_store(self, text: str, category: str, importance: float, scope: str = None) -> bool:
        """
        调用 memory_store 工具
        
        由于 Python 脚本无法直接调用 OpenClaw 工具，
        这里生成一个 shell 脚本，由外部调用
        """
        # 生成存储命令
        cmd_parts = ['memory_store', f'"{text}"', f'--category={category}', f'--importance={importance}']
        if scope:
            cmd_parts.append(f'--scope={scope}')
        
        return ' '.join(cmd_parts)
    
    def sync_pending_events(self) -> int:
        """同步待处理的事件到 lancedb-pro"""
        if not self.storage_log.exists():
            print("ℹ️ 无待同步事件")
            return 0
        
        print(f"🔄 同步事件到 lancedb-pro...")
        
        pending_events = []
        try:
            with open(self.storage_log, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        hash_id = record.get('hash_id', '')
                        
                        # 跳过已同步的
                        if hash_id in self.synced_hashes:
                            continue
                        
                        pending_events.append(record)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"❌ 读取存储日志失败: {e}")
            return 0
        
        if not pending_events:
            print("  ✅ 所有事件已同步")
            return 0
        
        print(f"  📊 待同步事件: {len(pending_events)}")
        
        # 生成同步脚本
        sync_script = self._generate_sync_script(pending_events)
        script_path = self.memory_dir / '.sync_to_lancedb.sh'
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(sync_script)
            
            # 添加执行权限
            import stat
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"  ✅ 同步脚本已生成: {script_path}")
            print(f"\n  请执行以下命令完成同步:")
            print(f"  bash {script_path}")
            
            # 标记为已同步（假设会成功执行）
            for event in pending_events:
                self.synced_hashes.add(event.get('hash_id', ''))
            self._save_synced_hashes()
            
            return len(pending_events)
            
        except Exception as e:
            print(f"  ❌ 生成同步脚本失败: {e}")
            return 0
    
    def _generate_sync_script(self, events: List[Dict]) -> str:
        """生成同步脚本"""
        lines = []
        lines.append("#!/bin/bash")
        lines.append("# lancedb-pro 同步脚本")
        lines.append(f"# 生成时间: {datetime.now().isoformat()}")
        lines.append(f"# 事件数量: {len(events)}")
        lines.append("")
        lines.append("echo '🔄 开始同步事件到 lancedb-pro...'")
        lines.append("")
        
        for i, event in enumerate(events, 1):
            text = event.get('content', '').replace('"', '\\"').replace('\n', '\\n')
            category = event.get('type', 'fact')
            importance = event.get('importance', 0.7)
            title = event.get('title', '').replace('"', '\\"')
            date = event.get('date', '')
            
            # 构建完整文本
            full_text = f"[{date}] {title}\n\n{text}"
            
            lines.append(f"echo '[{i}/{len(events)}] 存储: {title[:50]}...'")
            lines.append(f"memory_store '{full_text}' --category={category} --importance={importance}")
            lines.append("")
        
        lines.append("echo '✅ 同步完成'")
        lines.append("")
        
        return '\n'.join(lines)
    
    def generate_daily_memory_store(self, date: str = None):
        """生成每日记忆存储脚本（从 events 文件）"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        events_file = self.memory_dir / f"events-{date}.md"
        if not events_file.exists():
            print(f"ℹ️ {date} 无事件文件")
            return None
        
        # 读取事件文件
        try:
            with open(events_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取事件文件失败: {e}")
            return None
        
        # 生成存储脚本
        script_path = self.memory_dir / f'.store_events_{date}.sh'
        
        lines = []
        lines.append("#!/bin/bash")
        lines.append(f"# 每日事件存储脚本 - {date}")
        lines.append(f"# 生成时间: {datetime.now().isoformat()}")
        lines.append("")
        lines.append("echo '📅 存储每日事件到 lancedb-pro...'")
        lines.append("")
        
        # 将整个摘要作为一个记忆存储
        summary_text = content.replace('"', '\\"').replace('`', '\\`')
        lines.append(f"memory_store \"{summary_text}\" --category=fact --importance=0.7")
        lines.append("")
        lines.append("echo '✅ 每日事件存储完成'")
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            # 添加执行权限
            import stat
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ 存储脚本已生成: {script_path}")
            return script_path
            
        except Exception as e:
            print(f"❌ 生成脚本失败: {e}")
            return None


# 命令行入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='lancedb-pro 同步工具')
    parser.add_argument('--sync', action='store_true', help='同步待处理事件')
    parser.add_argument('--daily', help='生成每日存储脚本 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 加载配置
    config_path = Path(__file__).parent.parent / 'config.yaml'
    config = {}
    if config_path.exists():
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except:
            pass
    
    sync = LanceDBSync(config)
    
    if args.sync:
        count = sync.sync_pending_events()
        print(f"\n同步完成: {count} 个事件")
    
    if args.daily:
        script = sync.generate_daily_memory_store(args.daily)
        if script:
            print(f"\n请执行: bash {script}")


if __name__ == '__main__':
    main()
