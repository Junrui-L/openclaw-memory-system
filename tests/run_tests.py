#!/usr/bin/env python3
"""
测试运行器
运行所有单元测试
"""

import sys
import unittest
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 记忆管理系统单元测试")
    print("=" * 60)
    print()
    
    # 加载测试
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    
    # 统计结果
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    
    print(f"📊 测试结果:")
    print(f"  - 总测试数: {total}")
    print(f"  - 通过: {total - failures - errors - skipped}")
    print(f"  - 失败: {failures}")
    print(f"  - 错误: {errors}")
    print(f"  - 跳过: {skipped}")
    
    if result.wasSuccessful():
        print(f"\n✅ 所有测试通过!")
        return 0
    else:
        print(f"\n❌ 测试未通过")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
