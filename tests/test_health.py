#!/usr/bin/env python3
"""
健康检查模块单元测试
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.health import HealthChecker, HealthConstants


class TestHealthConstants(unittest.TestCase):
    """测试健康检查常量"""
    
    def test_constants_values(self):
        """测试常量值"""
        const = HealthConstants()
        
        self.assertEqual(const.MEMORY_FILE_WARNING_THRESHOLD, 365)
        self.assertEqual(const.PENDING_LEARNINGS_WARNING_THRESHOLD, 10)
        self.assertEqual(const.LOG_SIZE_THRESHOLD_MB, 100)
        self.assertEqual(const.LOG_SIZE_THRESHOLD_BYTES, 100 * 1024 * 1024)
        self.assertEqual(const.CRON_CHECK_HOURS, 24)
        self.assertEqual(const.MIN_PYTHON_VERSION, (3, 8))


class TestHealthChecker(unittest.TestCase):
    """测试 HealthChecker 类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'paths': {
                'workspace': self.temp_dir,
                'memory': str(Path(self.temp_dir) / 'memory'),
                'self_improving': str(Path(self.temp_dir) / 'self-improving'),
                'learnings': str(Path(self.temp_dir) / '.learnings'),
                'logs': str(Path(self.temp_dir) / 'logs'),
                'backup': str(Path(self.temp_dir) / '.backup'),
            },
            'disk': {
                'warning': 80,
                'critical': 90
            }
        }
        
        self.checker = HealthChecker(self.config)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.checker.config)
        self.assertIsNotNone(self.checker.paths)
        self.assertIsNotNone(self.checker.constants)
    
    def test_check_memory_layer_missing(self):
        """测试日记层检查 - 目录不存在"""
        result = self.checker._check_memory_layer()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('不存在', result['message'])
    
    def test_check_memory_layer_ok(self):
        """测试日记层检查 - 正常"""
        # 创建目录和文件
        memory_dir = Path(self.config['paths']['memory'])
        memory_dir.mkdir(parents=True, exist_ok=True)
        (memory_dir / '2026-03-13.md').write_text('test')
        
        result = self.checker._check_memory_layer()
        
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['details']['count'], 1)
    
    def test_check_memory_layer_warning(self):
        """测试日记层检查 - 文件过多告警"""
        memory_dir = Path(self.config['paths']['memory'])
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建超过阈值的文件数
        for i in range(400):
            (memory_dir / f'2026-03-{i:03d}.md').write_text('test')
        
        result = self.checker._check_memory_layer()
        
        self.assertEqual(result['status'], 'warning')
        self.assertIn('过多', result['alert'])
    
    def test_check_config_validity(self):
        """测试配置有效性检查"""
        result = self.checker._check_config_validity()
        
        # 临时目录下路径不存在，应该有错误
        self.assertEqual(result['status'], 'error')
        self.assertGreater(len(result['details']['errors']), 0)
    
    def test_check_permissions(self):
        """测试权限检查"""
        result = self.checker._check_permissions()
        
        # 临时目录可写
        self.assertEqual(result['status'], 'ok')
    
    def test_check_dependencies(self):
        """测试依赖检查"""
        result = self.checker._check_dependencies()
        
        # Python 版本应该满足要求
        self.assertEqual(result['status'], 'ok')


class TestDiskCalculation(unittest.TestCase):
    """测试磁盘计算"""
    
    def test_disk_usage_calculation(self):
        """测试磁盘使用率计算"""
        # 模拟值
        total = 1000
        used = 800
        used_percent = (used / total) * 100
        
        self.assertEqual(used_percent, 80.0)
        
        # 超过警告阈值
        self.assertTrue(used_percent >= 80)
        
        # 超过严重阈值
        used = 950
        used_percent = (used / total) * 100
        self.assertTrue(used_percent >= 90)


if __name__ == '__main__':
    unittest.main()
