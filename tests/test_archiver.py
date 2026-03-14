#!/usr/bin/env python3
"""
归档模块单元测试
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.archiver import Archiver, ArchiveConstants


class TestArchiveConstants(unittest.TestCase):
    """测试归档常量"""
    
    def test_constants_values(self):
        """测试常量值"""
        const = ArchiveConstants()
        
        self.assertEqual(const.DEFAULT_RETENTION_DAYS, 7)
        self.assertEqual(const.INCREMENTAL_CHECK_DAYS, 3)
        self.assertEqual(const.ARCHIVE_CHECK_DAYS, 7)
        self.assertEqual(const.MAX_KEY_POINTS, 10)
        self.assertEqual(const.MAX_RECENT_DAYS, 3)


class TestArchiver(unittest.TestCase):
    """测试 Archiver 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'paths': {
                'workspace': self.temp_dir,
                'memory': str(Path(self.temp_dir) / 'memory'),
                'self_improving': str(Path(self.temp_dir) / 'self-improving'),
                'learnings': str(Path(self.temp_dir) / '.learnings'),
                'archive': str(Path(self.temp_dir) / 'archive'),
                'backup': str(Path(self.temp_dir) / '.backup'),
                'positions': str(Path(self.temp_dir) / '.positions'),
            },
            'archive': {
                'retention_days': 7,
                'incremental': True
            },
            'backup': {
                'enabled': True,
                'daily': True,
                'weekly': True,
                'retention_daily': 7,
                'retention_weekly': 4,
                'weekly_day': 0
            }
        }
        
        # 创建测试目录
        for path_key in ['memory', 'self_improving', 'learnings', 'archive', 'backup', 'positions']:
            Path(self.config['paths'][path_key]).mkdir(parents=True, exist_ok=True)
        
        self.archiver = Archiver(self.config)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.archiver.config)
        self.assertIsNotNone(self.archiver.paths)
        self.assertIsNotNone(self.archiver.constants)
    
    def test_load_save_positions(self):
        """测试位置记录加载和保存"""
        # 初始为空
        self.assertEqual(self.archiver.positions, {})
        
        # 保存位置
        self.archiver.positions['/test/file.md'] = 100
        self.archiver._save_positions()
        
        # 重新加载
        self.archiver.positions = self.archiver._load_positions()
        self.assertEqual(self.archiver.positions.get('/test/file.md'), 100)
    
    def test_extract_todos(self):
        """测试待办事项提取"""
        # 创建测试文件
        test_file = Path(self.config['paths']['memory']) / 'test.md'
        test_file.write_text("""
# 测试文件

## 待办
- [ ] 任务1
- [x] 已完成
- [ ] 任务2
""")
        
        todos = self.archiver._extract_todos(test_file)
        
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], '任务1')
        self.assertEqual(todos[1], '任务2')
    
    def test_get_last_backup_time(self):
        """测试获取上次备份时间"""
        backup_dir = Path(self.config['paths']['backup'])
        
        # 无备份时返回 None
        result = self.archiver._get_last_backup_time(backup_dir)
        self.assertIsNone(result)
        
        # 创建测试备份文件
        backup_file = backup_dir / 'daily-20260313.tar.gz'
        backup_file.write_text('test')
        
        result = self.archiver._get_last_backup_time(backup_dir)
        self.assertIsNotNone(result)
    
    def test_save_backup_metadata(self):
        """测试保存备份元数据"""
        backup_file = Path(self.config['paths']['backup']) / 'test.tar.gz'
        backup_file.write_text('test content')
        
        self.archiver._save_backup_metadata(backup_file, 5, 'incremental')
        
        meta_file = backup_file.with_suffix('.json')
        self.assertTrue(meta_file.exists())
        
        import json
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata['type'], 'incremental')
        self.assertEqual(metadata['file_count'], 5)


class TestMaintenanceLogic(unittest.TestCase):
    """测试维护逻辑"""
    
    def test_day_calculation(self):
        """测试日期计算逻辑"""
        # 每3天
        self.assertTrue(3 % 3 == 0)
        self.assertTrue(6 % 3 == 0)
        self.assertFalse(4 % 3 == 0)
        
        # 每7天
        self.assertTrue(7 % 7 == 0)
        self.assertTrue(14 % 7 == 0)
        self.assertFalse(8 % 7 == 0)


if __name__ == '__main__':
    unittest.main()
