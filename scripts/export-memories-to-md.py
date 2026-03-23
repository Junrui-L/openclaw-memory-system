#!/usr/bin/env python3
"""
Memory-LanceDB-Pro 导出工具
将 memory-lancedb-pro 的记忆导出为 Markdown 格式

用法:
    python3 export-memories-to-md.py [scope] [output-file]

示例:
    python3 export-memories-to-md.py agent:main memories-export.md
    python3 export-memories-to-md.py global memories-global.md
    python3 export-memories-to-md.py  # 默认导出 agent:main 到 memory/memories-lancedb-export-YYYY-MM-DD.md
"""

import json
import subprocess
import sys
import os
from datetime import datetime


def run_export_command(scope, output_json):
    """执行 openclaw memory-pro export 命令"""
    cmd = ['openclaw', 'memory-pro', 'export', '--scope', scope, '--output', output_json]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"❌ 导出失败: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("❌ 导出超时")
        return False
    except Exception as e:
        print(f"❌ 导出出错: {e}")
        return False


def convert_to_markdown(json_path, md_path):
    """将 JSON 转换为 Markdown"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memories = data.get('memories', [])
    if not memories:
        print("⚠️ 没有记忆可导出")
        return False

    # 按类别分组
    categories = {}
    for m in memories:
        cat = m.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)

    # 生成 Markdown
    md_content = f"""# Memory-LanceDB-Pro 导出记录

> **导出时间**: {data.get('exportedAt', datetime.now().isoformat())}  
> **记忆总数**: {data.get('count', len(memories))}  
> **Scope**: {data.get('filters', {}).get('scope', 'N/A')}

---

## 统计概览

| 类别 | 数量 |
|------|------|
"""

    for cat, items in sorted(categories.items()):
        md_content += f"| {cat} | {len(items)} |\n"

    md_content += """
---

## 记忆详情

"""

    # 类别显示顺序
    category_order = ['reflection', 'fact', 'preference', 'decision', 'entity', 'other']

    for cat in category_order:
        if cat not in categories:
            continue

        md_content += f"### {cat.upper()} ({len(categories[cat])}条)\n\n"

        for m in sorted(categories[cat], key=lambda x: x.get('timestamp', 0), reverse=True):
            ts = m.get('timestamp', 0)
            if ts:
                dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M')
            else:
                dt = 'N/A'

            text = m.get('text', '').replace('\n', '\n> ')
            importance = m.get('importance', 0)
            memory_id = m.get('id', 'N/A')

            md_content += f"""**ID**: `{memory_id}`
**时间**: {dt} · **重要性**: {importance} · **类别**: {cat}

> {text}

---

"""

    # 保存 Markdown 文件
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    return True


def main():
    # 参数处理
    if len(sys.argv) >= 2:
        scope = sys.argv[1]
    else:
        scope = 'agent:main'

    if len(sys.argv) >= 3:
        output_md = sys.argv[2]
    else:
        # 默认保存到 memory 目录
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_md = f'/home/node/.openclaw/workspace/memory/memories-lancedb-export-{date_str}.md'

    # 临时 JSON 文件
    temp_json = '/tmp/memories-export-temp.json'

    print(f"🔄 正在导出 scope: {scope} ...")

    # 执行导出
    if not run_export_command(scope, temp_json):
        sys.exit(1)

    print(f"📝 正在转换为 Markdown: {output_md} ...")

    # 转换为 Markdown
    if convert_to_markdown(temp_json, output_md):
        # 获取文件大小
        size = os.path.getsize(output_md)
        print(f"✅ 导出完成!")
        print(f"   文件: {output_md}")
        print(f"   大小: {size / 1024:.1f} KB")
    else:
        print("❌ 转换失败")
        sys.exit(1)

    # 清理临时文件
    if os.path.exists(temp_json):
        os.remove(temp_json)


if __name__ == '__main__':
    main()
