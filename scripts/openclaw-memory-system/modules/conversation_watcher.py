#!/usr/bin/env python3
"""
对话实时监控器 v1.0

功能：监控 session 文件变化，自动提取关键信息追加到当天日记
使用 inotify 实现近乎实时的记录

运行方式：
    python3 conversation_watcher.py

或后台运行：
    nohup python3 conversation_watcher.py > logs/conversation-watcher.log 2>&1 &
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Set

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from conversation_logger import ConversationLogger
except ImportError:
    print("❌ 需要 conversation_logger.py 模块")
    sys.exit(1)


class ConversationWatcher:
    """对话文件监控器"""
    
    def __init__(self):
        self.sessions_dir = Path('/home/node/.openclaw/agents/main/sessions')
        self.logger = ConversationLogger()
        self.processed_files: Set[str] = set()
        self.file_mtimes: dict = {}
        
        # 冷却时间（秒）：避免频繁触发
        self.cooldown = 10
        self.last_process_time = 0
    
    def get_current_session(self) -> Path:
        """获取当前正在写入的 session 文件"""
        if not self.sessions_dir.exists():
            return None
        
        # 按修改时间排序，取最新的
        session_files = sorted(
            self.sessions_dir.glob('*.jsonl'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not session_files:
            return None
        
        return session_files[0]
    
    def should_process(self, session_file: Path) -> bool:
        """判断是否应该处理该文件"""
        file_id = str(session_file)
        current_mtime = session_file.stat().st_mtime
        
        # 检查是否在冷却期内
        if time.time() - self.last_process_time < self.cooldown:
            return False
        
        # 检查文件是否已稳定（5秒内无修改）
        if file_id in self.file_mtimes:
            if current_mtime == self.file_mtimes[file_id]:
                # 文件未变化，跳过
                return False
        
        # 更新记录
        self.file_mtimes[file_id] = current_mtime
        return True
    
    def process_session(self, session_file: Path):
        """处理 session 文件"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📝 检测到对话更新: {session_file.name}")
        
        # 等待文件写入完成
        time.sleep(2)
        
        # 提取并记录
        summary = self.logger.extract_conversation_summary(session_file)
        if summary:
            print(f"   用户: {summary['user_intent'][:40]}...")
            self.logger.append_to_daily_memory(summary)
            self.last_process_time = time.time()
        else:
            print("   ⚠️ 无有效内容")
    
    def run_polling(self, interval: int = 5):
        """轮询模式（兼容性更好）"""
        print(f"🔄 对话监控器启动（轮询模式）")
        print(f"   监控目录: {self.sessions_dir}")
        print(f"   轮询间隔: {interval}秒")
        print(f"   冷却时间: {self.cooldown}秒")
        print(f"   按 Ctrl+C 停止\n")
        
        try:
            while True:
                session_file = self.get_current_session()
                if session_file and self.should_process(session_file):
                    self.process_session(session_file)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 监控器已停止")
    
    def run_inotify(self):
        """inotify 模式（更实时，需要 pyinotify）"""
        try:
            import pyinotify
        except ImportError:
            print("⚠️ pyinotify 未安装，使用轮询模式")
            self.run_polling()
            return
        
        print(f"🔄 对话监控器启动（inotify 模式）")
        print(f"   监控目录: {self.sessions_dir}")
        print(f"   按 Ctrl+C 停止\n")
        
        class EventHandler(pyinotify.ProcessEvent):
            def __init__(self, watcher):
                self.watcher = watcher
            
            def process_IN_MODIFY(self, event):
                if event.pathname.endswith('.jsonl'):
                    session_file = Path(event.pathname)
                    if self.watcher.should_process(session_file):
                        self.watcher.process_session(session_file)
        
        wm = pyinotify.WatchManager()
        handler = EventHandler(self)
        notifier = pyinotify.Notifier(wm, handler)
        
        # 监控 sessions 目录
        wm.add_watch(str(self.sessions_dir), pyinotify.IN_MODIFY)
        
        try:
            notifier.loop()
        except KeyboardInterrupt:
            print("\n\n👋 监控器已停止")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='对话实时监控器')
    parser.add_argument('--mode', choices=['polling', 'inotify'], 
                       default='polling', help='监控模式 (默认: polling)')
    parser.add_argument('--interval', type=int, default=5, 
                       help='轮询间隔秒数 (默认: 5)')
    
    args = parser.parse_args()
    
    watcher = ConversationWatcher()
    
    if args.mode == 'inotify':
        watcher.run_inotify()
    else:
        watcher.run_polling(args.interval)


if __name__ == '__main__':
    main()
