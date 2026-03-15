#!/usr/bin/env python3
"""
归档模块
归档旧记忆和维护
"""

import json
import os
import shutil
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# 常量定义
class ArchiveConstants:
    """归档模块常量"""
    # 归档相关
    DEFAULT_RETENTION_DAYS = 7          # 默认保留天数
    INCREMENTAL_CHECK_DAYS = 3          # 增量检查天数（每3天整理）
    ARCHIVE_CHECK_DAYS = 7              # 归档检查天数（每7天归档）
    
    # 备份相关
    DAILY_BACKUP_PREFIX = "daily-"      # 每日备份前缀
    WEEKLY_BACKUP_PREFIX = "weekly-"    # 每周备份前缀
    BACKUP_DATE_FORMAT = "%Y%m%d"       # 备份日期格式
    
    # 文件扩展名
    BACKUP_EXTENSION = ".tar.gz"        # 备份文件扩展名
    META_EXTENSION = ".json"            # 元数据文件扩展名
    
    # 限制
    MAX_KEY_POINTS = 10                 # 最大关键信息条数
    MAX_RECENT_DAYS = 3                 # 最近检查天数


class Archiver:
    """归档管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.paths = config.get('paths', {})
        self.archive_config = config.get('archive', {})
        self.backup_config = config.get('backup', {})
        self.constants = ArchiveConstants()
        self.positions_file = Path(self.paths.get('positions', '')) / 'archive_positions.json'
        self.positions = self._load_positions()
    
    def daily_archive(self, config: Dict, args) -> bool:
        """每日归档"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        today_str = today.strftime('%Y-%m-%d')
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        print(f"📅 今日: {today_str}")
        print(f"📅 昨日: {yesterday_str}")
        print()
        
        # 1. 归档昨天（如果未归档）
        self._archive_yesterday(yesterday_str, today_str, getattr(args, 'force', False))
        
        # 2. 整理今天
        self._organize_today(today_str, yesterday_str)
        
        return True
    
    def _load_positions(self) -> Dict:
        """加载读取位置记录"""
        if self.positions_file.exists():
            try:
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_positions(self):
        """保存读取位置记录"""
        try:
            self.positions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.positions_file, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, indent=2)
        except Exception as e:
            print(f"  ⚠️ 无法保存位置记录: {e}")
    
    def _archive_yesterday(self, yesterday_str: str, today_str: str, force: bool = False):
        """归档昨天（增量归档）"""
        memory_dir = Path(self.paths.get('memory', ''))
        yesterday_file = memory_dir / f"{yesterday_str}.md"
        
        if not yesterday_file.exists():
            print(f"⚠️ 昨天记忆文件不存在: {yesterday_file}")
            return
        
        # 检查是否已归档（今天修改过）
        if not force:
            stat = yesterday_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            mod_date = mod_time.strftime('%Y-%m-%d')
            
            if mod_date == today_str:
                print(f"✅ 昨天记忆文件今天已归档过，跳过")
                return
        
        print(f"📝 归档昨天记忆: {yesterday_str}")
        
        # 增量归档：只读取新增内容
        try:
            file_key = str(yesterday_file)
            last_position = self.positions.get(file_key, 0)
            current_size = yesterday_file.stat().st_size
            
            # 如果文件大小没变且已归档过，跳过
            if last_position >= current_size and not force:
                print(f"  ✅ 文件无新内容，跳过")
                return
            
            # 读取新增内容（从上次位置到文件末尾）
            with open(yesterday_file, 'r', encoding='utf-8') as f:
                if last_position > 0 and not force:
                    f.seek(last_position)
                    new_content = f.read()
                    print(f"  📝 读取新增内容: {len(new_content)} 字符")
                else:
                    new_content = f.read()
                    print(f"  📝 读取全部内容: {len(new_content)} 字符")
            
            # 添加归档标记
            archive_marker = f"\n\n---\n\n*🤖 归档时间: {today_str}*\n*归档脚本: memory-manager*\n"
            
            # 检查是否已有归档标记
            with open(yesterday_file, 'r', encoding='utf-8') as f:
                full_content = f.read()
            
            if archive_marker not in full_content:
                with open(yesterday_file, 'a', encoding='utf-8') as f:
                    f.write(archive_marker)
                print(f"  ✅ 已添加归档标记")
            else:
                print(f"  ✅ 归档标记已存在")
            
            # 更新位置记录
            self.positions[file_key] = yesterday_file.stat().st_size
            self._save_positions()
            print(f"  ✅ 已更新读取位置: {self.positions[file_key]} 字节")
                
        except Exception as e:
            print(f"  ❌ 归档失败: {e}")
    
    def _organize_today(self, today_str: str, yesterday_str: str):
        """整理今天"""
        memory_dir = Path(self.paths.get('memory', ''))
        today_file = memory_dir / f"{today_str}.md"
        yesterday_file = memory_dir / f"{yesterday_str}.md"
        
        # 检查今天文件是否存在
        if today_file.exists():
            print(f"📝 今天记忆文件已存在，追加整理")
            self._append_today(today_file, yesterday_file)
        else:
            print(f"📝 创建今天记忆文件")
            self._create_today(today_file, yesterday_file)
    
    def _create_today(self, today_file: Path, yesterday_file: Path):
        """创建今天记忆文件"""
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        
        # 基础模板
        content = f"""# {today_str} {today.strftime('%A')}

## 今日概要
- **日期**: {today_str}
- **创建时间**: {today.strftime('%H:%M')}
- **星期**: {today.strftime('%A')}

## 对话记录

*（待补充）*

## 关键事件

*（待补充）*

"""
        
        # 继承昨天待办
        if yesterday_file.exists():
            todos = self._extract_todos(yesterday_file)
            if todos:
                content += "## 待办事项（从昨日继承）\n\n"
                for todo in todos:
                    content += f"- [ ] {todo}\n"
                content += "\n"
        
        content += """## 经验总结

*（待补充）*

---

*🤖 自动创建: memory-manager*
"""
        
        try:
            with open(today_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ 创建完成: {today_file}")
        except Exception as e:
            print(f"  ❌ 创建失败: {e}")
    
    def _append_today(self, today_file: Path, yesterday_file: Path):
        """追加今天内容"""
        # 这里可以实现增量归档逻辑
        # 读取日志文件，追加新内容
        print(f"  ✅ 今天文件已存在，保持现状")
    
    def _extract_todos(self, file_path: Path) -> List[str]:
        """提取待办事项"""
        todos = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('- [ ]'):
                        todo = line[5:].strip()
                        todos.append(todo)
        except Exception:
            pass
        
        return todos
    
    def maintenance(self, config: Dict, args) -> bool:
        """记忆维护"""
        today = datetime.now()
        day_of_month = today.day
        
        print(f"🔧 记忆维护检查")
        print(f"📅 日期: {today.strftime('%Y-%m-%d')}")
        print(f"📅 本月第 {day_of_month} 天")
        print()
        
        # 每N天：整理长期记忆
        if day_of_month % self.constants.INCREMENTAL_CHECK_DAYS == 0 or getattr(args, 'force', False):
            print(f"📝 执行长期记忆整理（每{self.constants.INCREMENTAL_CHECK_DAYS}天）")
            self._organize_long_term_memory()
        else:
            print("⏭️ 跳过长期记忆整理（非3的倍数日期）")
        
        print()
        
        # 每N天：归档旧记忆
        if day_of_month % self.constants.ARCHIVE_CHECK_DAYS == 0 or getattr(args, 'force', False):
            print(f"📦 执行旧记忆归档（每{self.constants.ARCHIVE_CHECK_DAYS}天）")
            self._archive_old_memories()
        else:
            print("⏭️ 跳过旧记忆归档（非7的倍数日期）")
        
        return True
    
    def _organize_long_term_memory(self):
        """整理长期记忆 - 智能合并去重"""
        memory_dir = Path(self.paths.get('memory', ''))
        memory_md = Path(self.paths.get('memory_md', ''))
        
        if not memory_md.exists():
            print(f"⚠️ 长期记忆文件不存在: {memory_md}")
            return
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        # 读取现有 MEMORY.md 内容
        try:
            with open(memory_md, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            print(f"  ❌ 无法读取 MEMORY.md: {e}")
            return
        
        # 提取已存在的关键信息（用于去重）
        existing_points = set()
        for line in existing_content.split('\n'):
            line = line.strip()
            if line.startswith('- ['):
                # 提取方括号后的内容作为去重键
                match = line[2:].strip()
                if match:
                    existing_points.add(match)
        
        # 读取最近N天的记忆
        new_key_points = []
        for i in range(self.constants.MAX_RECENT_DAYS):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = memory_dir / f"{date}.md"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取关键信息（简单实现）
                    for line in content.split('\n'):
                        line = line.strip()
                        if any(kw in line for kw in ['重要', '关键', '决定', '偏好']):
                            point_text = line.strip()
                            point_with_date = f"[{date}] {point_text}"
                            # 去重检查
                            if point_with_date not in existing_points:
                                new_key_points.append(point_with_date)
                                existing_points.add(point_with_date)  # 防止本次重复
                except Exception:
                    pass
        
        if new_key_points:
            print(f"  📝 提取到 {len(new_key_points)} 条新关键信息")
            # 追加到 MEMORY.md
            try:
                with open(memory_md, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n### {today_str} 自动整理\n\n")
                    for point in new_key_points[:self.constants.MAX_KEY_POINTS]:  # 最多N条
                        f.write(f"- {point}\n")
                print(f"  ✅ 已更新长期记忆（新增 {len(new_key_points[:self.constants.MAX_KEY_POINTS])} 条）")
            except Exception as e:
                print(f"  ❌ 更新失败: {e}")
        else:
            print(f"  ℹ️ 无新关键信息需要整理")
    
    def _archive_old_memories(self):
        """归档旧记忆"""
        memory_dir = Path(self.paths.get('memory', ''))
        archive_dir = Path(self.paths.get('archive', '')) / 'memory'
        
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        retention_days = self.archive_config.get('retention_days', self.constants.DEFAULT_RETENTION_DAYS)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        archived_count = 0
        
        for file_path in memory_dir.glob('*.md'):
            # 跳过索引文件
            if file_path.name == 'INDEX.md':
                continue
            
            # 获取文件修改时间
            stat = file_path.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            if mod_time < cutoff_date:
                try:
                    # 移动文件
                    shutil.move(str(file_path), str(archive_dir / file_path.name))
                    archived_count += 1
                    print(f"  📦 归档: {file_path.name}")
                except Exception as e:
                    print(f"  ❌ 归档失败 {file_path.name}: {e}")
        
        if archived_count > 0:
            print(f"  ✅ 共归档 {archived_count} 个文件")
            self._update_archive_index(archive_dir)
        else:
            print(f"  ℹ️ 无需要归档的文件")
    
    def _update_archive_index(self, archive_dir: Path):
        """更新归档索引"""
        index_file = archive_dir / 'README.md'
        
        files = list(archive_dir.glob('*.md'))
        
        content = f"""# 记忆归档目录

本目录存放归档的记忆文件。

## 归档规则
- 自动归档 {self.archive_config.get('retention_days', 7)} 天前的记忆文件
- 每周日检查并执行
- 保留原始文件名

## 统计
- 归档文件数: {len(files)}
- 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 恢复方法
如需恢复某个记忆文件，手动复制回 memory/ 目录即可：
```bash
cp archive/memory/YYYY-MM-DD.md memory/
```
"""
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"  ⚠️ 无法更新索引: {e}")
    
    def create_backup(self, config: Dict) -> bool:
        """创建备份"""
        print("💾 创建备份...")
        
        backup_dir = Path(self.paths.get('backup', ''))
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now()
        today_str = today.strftime('%Y%m%d')
        
        # 每日备份
        if self.backup_config.get('daily', True):
            self._create_daily_backup(backup_dir, today_str)
        
        # 每周备份
        if self.backup_config.get('weekly', True) and today.weekday() == self.backup_config.get('weekly_day', 0):
            self._create_weekly_backup(backup_dir, today_str)
        
        # 清理旧备份
        self._cleanup_old_backups(backup_dir)
        
        return True
    
    def _create_daily_backup(self, backup_dir: Path, date_str: str):
        """创建每日增量备份"""
        workspace = Path(self.paths.get('workspace', ''))
        backup_file = backup_dir / f"{self.constants.DAILY_BACKUP_PREFIX}{date_str}{self.constants.BACKUP_EXTENSION}"
        
        # 获取上次备份时间
        last_backup_time = self._get_last_backup_time(backup_dir)
        
        try:
            # 收集需要备份的文件（只备份变更的文件）
            files_to_backup = []
            backup_items = ['memory', 'self-improving', '.learnings', 'MEMORY.md']
            
            for item in backup_items:
                path = workspace / item
                if not path.exists():
                    continue
                
                if path.is_file():
                    # 检查文件是否变更
                    if last_backup_time is None or path.stat().st_mtime > last_backup_time:
                        files_to_backup.append((path, item))
                else:
                    # 目录：递归检查每个文件
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            if last_backup_time is None or file_path.stat().st_mtime > last_backup_time:
                                # 计算相对路径
                                rel_path = file_path.relative_to(workspace)
                                files_to_backup.append((file_path, str(rel_path)))
            
            if not files_to_backup:
                print(f"  ℹ️ 每日备份: 无变更文件，跳过")
                return
            
            # 创建增量备份
            with tarfile.open(backup_file, 'w:gz') as tar:
                for file_path, arcname in files_to_backup:
                    tar.add(file_path, arcname=arcname)
            
            # 保存备份元数据
            self._save_backup_metadata(backup_file, len(files_to_backup), 'incremental')
            
            backup_type = "增量" if last_backup_time else "全量"
            print(f"  ✅ 每日{backup_type}备份: {backup_file.name} ({len(files_to_backup)} 个文件)")
            
        except Exception as e:
            print(f"  ❌ 每日备份失败: {e}")
    
    def _create_weekly_backup(self, backup_dir: Path, date_str: str):
        """创建每周完整备份"""
        workspace = Path(self.paths.get('workspace', ''))
        backup_file = backup_dir / f"{self.constants.WEEKLY_BACKUP_PREFIX}{date_str}{self.constants.BACKUP_EXTENSION}"
        
        try:
            file_count = 0
            with tarfile.open(backup_file, 'w:gz') as tar:
                # 完整备份
                for subdir in ['memory', 'self-improving', '.learnings', 'reports', 'archive']:
                    path = workspace / subdir
                    if path.exists():
                        tar.add(path, arcname=subdir)
                        # 统计文件数
                        if path.is_dir():
                            file_count += len(list(path.rglob('*')))
                
                # 备份配置文件
                memory_md = workspace / 'MEMORY.md'
                if memory_md.exists():
                    tar.add(memory_md, arcname='MEMORY.md')
                    file_count += 1
            
            # 保存备份元数据
            self._save_backup_metadata(backup_file, file_count, 'full')
            
            print(f"  ✅ 每周完整备份: {backup_file.name} ({file_count} 个文件)")
        except Exception as e:
            print(f"  ❌ 每周备份失败: {e}")
    
    def _cleanup_old_backups(self, backup_dir: Path):
        """清理旧备份"""
        # 清理旧每日备份
        daily_retention = self.backup_config.get('retention_daily', self.constants.DEFAULT_RETENTION_DAYS)
        daily_backups = sorted(backup_dir.glob(f'{self.constants.DAILY_BACKUP_PREFIX}*{self.constants.BACKUP_EXTENSION}'), reverse=True)
        
        for old_backup in daily_backups[daily_retention:]:
            try:
                # 同时删除元数据文件
                meta_file = old_backup.with_suffix('.json')
                if meta_file.exists():
                    meta_file.unlink()
                old_backup.unlink()
                print(f"  🗑️ 删除旧每日备份: {old_backup.name}")
            except Exception:
                pass
        
        # 清理旧每周备份
        weekly_retention = self.backup_config.get('retention_weekly', 4)
        weekly_backups = sorted(backup_dir.glob(f'{self.constants.WEEKLY_BACKUP_PREFIX}*{self.constants.BACKUP_EXTENSION}'), reverse=True)
        
        for old_backup in weekly_backups[weekly_retention:]:
            try:
                # 同时删除元数据文件
                meta_file = old_backup.with_suffix('.json')
                if meta_file.exists():
                    meta_file.unlink()
                old_backup.unlink()
                print(f"  🗑️ 删除旧每周备份: {old_backup.name}")
            except Exception:
                pass
    
    def _get_last_backup_time(self, backup_dir: Path) -> Optional[float]:
        """获取上次备份时间"""
        try:
            # 查找最近的每日备份元数据
            backups = sorted(backup_dir.glob(f'{self.constants.DAILY_BACKUP_PREFIX}*{self.constants.BACKUP_EXTENSION}'), reverse=True)
            if backups:
                # 返回最近备份文件的修改时间
                return backups[0].stat().st_mtime
        except Exception:
            pass
        return None
    
    def _save_backup_metadata(self, backup_file: Path, file_count: int, backup_type: str):
        """保存备份元数据"""
        try:
            meta_file = backup_file.with_suffix('.json')
            metadata = {
                'created': datetime.now().isoformat(),
                'type': backup_type,
                'file_count': file_count,
                'size': backup_file.stat().st_size if backup_file.exists() else 0
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"  ⚠️ 无法保存备份元数据: {e}")
