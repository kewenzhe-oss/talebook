#!/usr/bin/env python3
"""
Step 1: 标签清洗与规范化 — 原始标签提取
==========================================
只读连接 metadata.db，提取所有唯一标签名及引用计数，
导出为 raw_tags.json（结构化）和 raw_tags_summary.txt（可读摘要）。

绝不修改原始数据库。
"""

import json
import sqlite3
import sys
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent / "talebook_data" / "books" / "library" / "metadata.db"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tools" / "tag_data"

def main():
    # 1. 连接（只读模式）
    if not DB_PATH.exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        sys.exit(1)

    uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    print(f"✅ 已连接数据库（只读）: {DB_PATH}")

    # 2. 提取唯一标签 + 引用计数
    query = """
        SELECT
            t.id,
            t.name,
            COUNT(btl.book) AS book_count
        FROM tags t
        LEFT JOIN books_tags_link btl ON btl.tag = t.id
        GROUP BY t.id, t.name
        ORDER BY book_count DESC, t.name COLLATE NOCASE
    """
    rows = conn.execute(query).fetchall()
    conn.close()

    total_tags = len(rows)
    orphan_tags = sum(1 for r in rows if r["book_count"] == 0)

    print(f"📊 共提取 {total_tags} 个唯一标签")
    print(f"📊 其中 {orphan_tags} 个孤儿标签（未关联任何书）")

    # 3. 构建导出数据
    tags_list = [
        {"id": r["id"], "name": r["name"], "book_count": r["book_count"]}
        for r in rows
    ]
    tag_names_only = [r["name"] for r in rows]

    # 4. 导出
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 4a. JSON — 完整结构化数据
    json_path = OUTPUT_DIR / "raw_tags.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "meta": {
                    "total_unique_tags": total_tags,
                    "orphan_tags": orphan_tags,
                    "source": str(DB_PATH),
                },
                "tags": tags_list,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"💾 JSON 已导出: {json_path}")

    # 4b. TXT — 人类可读摘要
    txt_path = OUTPUT_DIR / "raw_tags_summary.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  原始标签清单（按引用数降序）\n")
        f.write(f"  共 {total_tags} 个唯一标签 | {orphan_tags} 个孤儿标签\n")
        f.write("=" * 60 + "\n\n")
        for r in rows:
            f.write(f"  [{r['book_count']:>3}] {r['name']}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("  仅标签名列表（可直接用于 LLM prompt）\n")
        f.write("=" * 60 + "\n\n")
        f.write("\n".join(tag_names_only))
        f.write("\n")
    print(f"💾 TXT 已导出: {txt_path}")

    # 5. 打印前 30 条预览
    print(f"\n{'─' * 50}")
    print(f"  TOP 30 标签预览（引用数 | 标签名）")
    print(f"{'─' * 50}")
    for r in rows[:30]:
        print(f"  [{r['book_count']:>3}] {r['name']}")
    print(f"{'─' * 50}")
    print("✅ Step 1 完成。请检查导出文件后决定下一步。")


if __name__ == "__main__":
    main()
