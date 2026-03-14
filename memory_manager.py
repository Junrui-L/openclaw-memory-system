#!/usr/bin/env python3
"""
记忆管理系统 - 主入口
作为双记忆系统的自动化工具层
"""

import sys
import argparse
import json
import fcntl
import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# 尝试导入yaml，如果不存在则使用json
try:
    import yaml
    USE_YAML = True
except ImportError:
    USE_YAML = False
    # 静默处理，不输出警告

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    # v3.0 新模块
    from modules.reader_v3 import MemoryReader
    from modules.health_v3 import HealthChecker
    from modules.session_extractor import SessionExtractor
    
    # v2.0 兼容模块
    from modules import analyzer, reporter, archiver
    
    V3_AVAILABLE = True
except ImportError as e:
    print(f"警告: v3.0 模块导入失败: {e}")
    print("使用 v2.0 模块")
    
    # 回退到 v2.0
    from modules import reader, analyzer, reporter, archiver, health
    V3_AVAILABLE = False


def load_config():
    """加载配置文件"""
    # 尝试加载YAML
    config_path = Path(__file__).parent / "config.yaml"
    json_path = Path(__file__).parent / "config.json"
    
    # 如果YAML存在且可用
    if USE_YAML and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"警告: 无法加载YAML配置: {e}")
    
    # 尝试加载JSON
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"错误: 无法加载JSON配置: {e}")
            sys.exit(1)
    
    # 使用默认配置
    print("使用默认配置")
    return get_default_config()


def get_default_config():
    """获取默认配置"""
    return {
        "paths": {
            "workspace": "/home/node/.openclaw/workspace",
            "memory": "/home/node/.openclaw/workspace/memory",
            "self_improving": "/home/node/.openclaw/workspace/self-improving",
            "learnings": "/home/node/.openclaw/workspace/.learnings",
            "memory_md": "/home/node/.openclaw/workspace/MEMORY.md",
            "reports": "/home/node/.openclaw/workspace/reports",
            "archive": "/home/node/.openclaw/workspace/archive",
            "backup": "/home/node/.openclaw/workspace/.backup",
            "positions": "/home/node/.openclaw/workspace/.positions",
            "logs": "/home/node/.openclaw/workspace/logs"
        },
        "archive": {"retention_days": 7, "incremental": True},
        "backup": {"enabled": True, "daily": True, "weekly": True},
        "reports": {"morning": {"enabled": True, "hour": 8}},
        "notification": {"feishu": {"enabled": False}},
        "todo": {"smart_priority": True},
        "disk": {"warning": 80, "critical": 90},
        "logging": {"level": "INFO", "max_bytes": 10485760, "backup_count": 5}
    }


def setup_logging(config: dict) -> logging.Logger:
    """设置日志系统"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    
    # 创建logger
    logger = logging.getLogger('memory_manager')
    logger.setLevel(log_level)
    
    # 清除已有handler
    logger.handlers = []
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件handler（带轮转）
    logs_dir = Path(config.get('paths', {}).get('logs', ''))
    if logs_dir.exists():
        log_file = logs_dir / 'memory_manager.log'
        max_bytes = log_config.get('max_bytes', 10485760)  # 10MB
        backup_count = log_config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def cmd_daily(config, args):
    """每日归档命令"""
    print("📅 执行每日归档...")
    print("=" * 50)
    
    from modules.archiver import Archiver
    archiver = Archiver(config)
    archiver.daily_archive(config, args)
    
    print("=" * 50)
    print("✅ 每日归档完成")


def cmd_maintenance(config, args):
    """维护命令"""
    print("🔧 执行记忆维护...")
    print("=" * 50)
    
    from modules.archiver import Archiver
    archiver = Archiver(config)
    archiver.maintenance(config, args)
    
    print("=" * 50)
    print("✅ 记忆维护完成")


def cmd_report(config, args):
    """生成报告命令"""
    print("📊 生成报告...")
    print("=" * 50)
    
    from modules.reporter import ReportGenerator
    generator = ReportGenerator(config)
    generator.generate_morning_report(config, args)
    
    print("=" * 50)
    print("✅ 报告生成完成")


def cmd_health(config, args):
    """健康检查命令"""
    print("🏥 执行健康检查...")
    print("=" * 50)
    
    # v3.0: 使用新的 HealthChecker
    if V3_AVAILABLE:
        from modules.reader_v3 import MemoryReader
        from modules.health_v3 import HealthChecker
        reader = MemoryReader(config)
        checker = HealthChecker(reader, config)
    else:
        from modules.health import HealthChecker
        checker = HealthChecker(config)
    
    checker.check()
    
    print("=" * 50)
    print("✅ 健康检查完成")
    checker.check(config, args)
    
    print("=" * 50)
    print("✅ 健康检查完成")


def cmd_backup(config, args):
    """备份命令"""
    print("💾 执行备份...")
    print("=" * 50)
    
    from modules.archiver import Archiver
    archiver = Archiver(config)
    archiver.create_backup(config)
    
    print("=" * 50)
    print("✅ 备份完成")


def cmd_index(config, args):
    """生成索引命令"""
    print("📇 生成记忆索引...")
    print("=" * 50)
    
    from modules.analyzer import MemoryAnalyzer
    analyzer = MemoryAnalyzer(config)
    analyzer.generate_index(config)
    
    print("=" * 50)
    print("✅ 索引生成完成")


def cmd_status(config, args):
    """查看状态命令"""
    print("📈 记忆系统状态")
    print("=" * 50)
    
    # v3.0: 使用新的 HealthChecker
    if V3_AVAILABLE:
        from modules.reader_v3 import MemoryReader
        from modules.health_v3 import HealthChecker
        reader = MemoryReader(config)
        checker = HealthChecker(reader, config)
        checker.check()
    else:
        from modules.health import HealthChecker
        checker = HealthChecker(config)
        checker.show_summary(config)


def cmd_session_merge(config, args):
    """Session 合并命令 (v3.0)"""
    print("🔄 Session 合并...")
    print("=" * 50)
    
    if not V3_AVAILABLE:
        print("❌ v3.0 模块不可用")
        return
    
    from modules.session_extractor import SessionExtractor
    extractor = SessionExtractor(config)
    
    if args.date:
        extractor.merge_to_daily_memory(args.date)
    else:
        extractor.auto_extract_and_merge()
    
    print("=" * 50)
    print("✅ Session 合并完成")


def cmd_session_check(config, args):
    """Session 覆盖率检查命令 (v3.0)"""
    print("📊 Session 覆盖率检查...")
    print("=" * 50)
    
    if not V3_AVAILABLE:
        print("❌ v3.0 模块不可用")
        return
    
    from modules.session_extractor import SessionExtractor
    extractor = SessionExtractor(config)
    
    result = extractor.check_session_coverage(days=args.days or 7)
    
    print(f"\n📊 Session 覆盖率报告:")
    print(f"   总 Sessions: {result['total_sessions']}")
    print(f"   已记录: {result['recorded_sessions']}")
    print(f"   覆盖率: {result['coverage_rate']:.1%}")
    print(f"   状态: {result['status']}")
    
    if result.get('missing_dates'):
        print(f"   缺失日期: {', '.join(result['missing_dates'])}")
    
    print("=" * 50)


def cmd_all(config, args):
    """执行全部任务"""
    print("🎯 执行全部任务")
    print("=" * 50)
    
    # 按顺序执行
    cmd_daily(config, args)
    print()
    cmd_maintenance(config, args)
    print()
    cmd_report(config, args)
    
    print("=" * 50)
    print("✅ 全部任务执行完成")


def acquire_lock(lock_file: Path) -> bool:
    """获取文件锁，防止并发执行"""
    try:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True, fd
    except (IOError, OSError):
        return False, None


def release_lock(fd):
    """释放文件锁"""
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except Exception:
        pass


def main():
    # 获取锁文件路径
    lock_file = Path('/tmp/memory_manager.lock')
    
    parser = argparse.ArgumentParser(
        description='记忆管理系统 - 双记忆系统的自动化工具层',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s daily                    # 执行每日归档
  %(prog)s report --send-feishu     # 生成报告并发送到飞书
  %(prog)s health --verbose         # 详细健康检查
  %(prog)s status                   # 查看系统状态
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # daily 命令
    daily_parser = subparsers.add_parser('daily', help='每日归档')
    daily_parser.add_argument('--incremental', action='store_true', 
                             help='启用增量归档')
    daily_parser.add_argument('--force', action='store_true',
                             help='强制归档，忽略重复检查')
    
    # maintenance 命令
    maint_parser = subparsers.add_parser('maintenance', help='记忆维护')
    maint_parser.add_argument('--force', action='store_true',
                             help='强制执行，忽略时间条件')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--send-feishu', action='store_true',
                              help='发送到飞书')
    report_parser.add_argument('--type', choices=['morning', 'health'],
                              default='morning', help='报告类型')
    
    # health 命令
    health_parser = subparsers.add_parser('health', help='健康检查')
    health_parser.add_argument('--verbose', action='store_true',
                              help='详细输出')
    health_parser.add_argument('--send-alert', action='store_true',
                              help='发送告警通知')
    
    # session-merge 命令 (v3.0)
    session_merge_parser = subparsers.add_parser('session-merge', help='合并 Sessions 到记忆 (v3.0)')
    session_merge_parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)，默认今天和昨天')
    
    # session-check 命令 (v3.0)
    session_check_parser = subparsers.add_parser('session-check', help='检查 Session 覆盖率 (v3.0)')
    session_check_parser.add_argument('--days', type=int, default=7,
                                     help='检查天数 (默认 7)')
    
    # backup 命令
    backup_parser = subparsers.add_parser('backup', help='手动备份')
    
    # index 命令
    index_parser = subparsers.add_parser('index', help='生成索引')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='查看状态')
    
    # all 命令
    all_parser = subparsers.add_parser('all', help='执行全部任务')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    logger = setup_logging(config)
    logger.info("记忆管理系统启动")
    
    # 获取文件锁（防止并发执行）
    lock_acquired, lock_fd = acquire_lock(lock_file)
    if not lock_acquired:
        logger.warning("另一个记忆管理任务正在运行，跳过本次执行")
        print("⚠️ 另一个记忆管理任务正在运行，跳过本次执行")
        print(f"   如果确定没有任务在运行，可以手动删除: {lock_file}")
        sys.exit(0)
    
    logger.info(f"开始执行命令: {args.command}")
    
    try:
        # 执行对应命令
        commands = {
            'daily': cmd_daily,
            'maintenance': cmd_maintenance,
            'report': cmd_report,
            'health': cmd_health,
            'backup': cmd_backup,
            'index': cmd_index,
            'status': cmd_status,
            'all': cmd_all,
            'session-merge': cmd_session_merge,
            'session-check': cmd_session_check,
        }
        
        if args.command in commands:
            commands[args.command](config, args)
            logger.info(f"命令 {args.command} 执行完成")
        else:
            logger.error(f"未知命令: {args.command}")
            print(f"未知命令: {args.command}")
            parser.print_help()
    except KeyboardInterrupt:
        logger.info("用户中断")
        print("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行错误: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 释放文件锁
        release_lock(lock_fd)
        logger.info("记忆管理系统结束")


if __name__ == '__main__':
    main()
