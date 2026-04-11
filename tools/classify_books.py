#!/usr/bin/env python3
"""
全自动书籍分类脚本 — 调用 Gemini API 将 353 本书归入 12 个一级分类。
只读原始数据，结果写入 ai_classification_stage 表。
"""

import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

# ── 配置 ──────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent / "talebook_data" / "books" / "library" / "metadata.db"
MODEL = "gemini-2.0-flash"     # 快速、便宜、中文好
BATCH_SIZE = 10                # Gemini context 大，每批 10 本
MAX_RETRIES = 3
RETRY_DELAY = 5                # 秒

VALID_CATEGORIES = [
    "哲学与思想", "心理与自我", "关系与家庭", "文学与叙事",
    "历史与政治", "社会与文化", "商业与管理", "经济与投资",
    "科技与计算", "医疗与生命", "艺术与审美", "宗教与灵性",
    "待整理",
]

SYSTEM_PROMPT = """你是一个专业的图书分类引擎。你的任务是根据书名、作者、已有标签和简介，对每本书做标准化分类。

## 规则（严格执行）

### 1. 主分类 (primary_category)
只能从以下 12 个选 1 个，不确定就填"待整理"：
哲学与思想, 心理与自我, 关系与家庭, 文学与叙事, 历史与政治, 社会与文化, 商业与管理, 经济与投资, 科技与计算, 医疗与生命, 艺术与审美, 宗教与灵性

### 2. 副分类 (secondary_categories)
如果一本书确实跨领域，最多再选 1-2 个副分类（同样从上面 12 个中选）。不跨领域就留空数组。

### 3. 规范标签 (canonical_tags)
从书的内容提取 3-5 个核心主题标签。要求：
- 简体中文
- 概括性强，不要过于细碎（如"颜色现象学"应归纳为"美学"）
- 近义词统一（如"个人成长"和"自我成长"统一为"自我成长"）

### 4. 体裁/版本标签 (format_tags)
将体裁或版本相关的信息分离出来，如：短篇小说、长篇小说、散文、套装全集、经典名著、诺贝尔文学奖等。没有就留空数组。

### 5. 人物标签 (person_tags)
将人名/人物相关的标签分离出来，如：毛泽东、尼采、张爱玲、弗洛姆等。没有就留空数组。

### 6. 分类理由 (reason)
用一句话解释你选择此主分类的原因。

## 输出格式
对输入的每本书，返回严格的 JSON 数组，每个元素格式：
{
  "book_id": <int>,
  "primary_category": "<string>",
  "secondary_categories": ["<string>", ...],
  "canonical_tags": ["<string>", ...],
  "format_tags": ["<string>", ...],
  "person_tags": ["<string>", ...],
  "reason": "<string>"
}

只返回 JSON 数组，不要返回任何其他文字、markdown 标记或解释。"""


def load_env(env_path):
    """从 .env 文件加载配置"""
    config = {}
    if env_path.exists():
        for line in env_path.read_text().strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config


def load_books(conn):
    """读取所有书籍的 id, title, authors, description, raw_tags"""
    rows = conn.execute("""
        SELECT b.id, b.title,
               GROUP_CONCAT(DISTINCT a.name) AS authors,
               c.text AS description,
               GROUP_CONCAT(DISTINCT t.name) AS tags
        FROM books b
        LEFT JOIN books_authors_link bal ON bal.book = b.id
        LEFT JOIN authors a ON a.id = bal.author
        LEFT JOIN comments c ON c.book = b.id
        LEFT JOIN books_tags_link btl ON btl.book = b.id
        LEFT JOIN tags t ON t.id = btl.tag
        GROUP BY b.id
        ORDER BY b.id
    """).fetchall()
    books = []
    for r in rows:
        desc = r[3] or ""
        desc = re.sub(r"<[^>]+>", "", desc)
        if len(desc) > 300:
            desc = desc[:300] + "…"
        books.append({
            "book_id": r[0],
            "title": r[1],
            "authors": r[2] or "",
            "description": desc,
            "raw_tags": r[4] or "",
        })
    return books


def get_already_classified(conn):
    """获取已经分类过的 book_id 集合（断点续传）"""
    try:
        rows = conn.execute("SELECT book_id FROM ai_classification_stage").fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


def build_user_prompt(batch):
    """构造 user prompt"""
    items = []
    for b in batch:
        items.append(
            f"book_id: {b['book_id']}\n"
            f"title: {b['title']}\n"
            f"authors: {b['authors']}\n"
            f"tags: {b['raw_tags']}\n"
            f"description: {b['description']}"
        )
    return "请对以下书籍进行分类：\n\n" + "\n\n---\n\n".join(items)


def call_gemini(client, batch):
    """调用 Gemini API 并解析返回的 JSON"""
    user_prompt = build_user_prompt(batch)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                ),
            )
            raw = response.text.strip()
            data = json.loads(raw)
            # Handle wrapped responses
            if isinstance(data, dict):
                for key in ("books", "results", "data", "classifications"):
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                else:
                    if "book_id" in data:
                        data = [data]
                    else:
                        raise ValueError(f"Unexpected JSON structure: {list(data.keys())}")
            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data)}")
            return data
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)   # exponential backoff
            else:
                raise


def save_results(conn, results):
    """将一批分类结果写入 staging 表"""
    for r in results:
        pc = r.get("primary_category", "待整理")
        if pc not in VALID_CATEGORIES:
            pc = "待整理"
        conn.execute("""
            INSERT OR REPLACE INTO ai_classification_stage
            (book_id, title, primary_category, secondary_categories,
             canonical_tags, format_tags, person_tags, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r["book_id"],
            None,
            pc,
            json.dumps(r.get("secondary_categories", []), ensure_ascii=False),
            json.dumps(r.get("canonical_tags", []), ensure_ascii=False),
            json.dumps(r.get("format_tags", []), ensure_ascii=False),
            json.dumps(r.get("person_tags", []), ensure_ascii=False),
            r.get("reason", ""),
        ))
    conn.commit()


def backfill_titles(conn):
    """回填 title 字段"""
    conn.execute("""
        UPDATE ai_classification_stage
        SET title = (SELECT b.title FROM books b WHERE b.id = ai_classification_stage.book_id)
        WHERE title IS NULL
    """)
    conn.commit()


def main():
    # ── API Key（从 tools/.env 文件读取）──
    env_path = Path(__file__).resolve().parent / ".env"
    config = load_env(env_path)
    api_key = os.environ.get("GEMINI_API_KEY") or config.get("GEMINI_API_KEY", "")

    if not api_key or "粘贴" in api_key:
        print(f"❌ 请先在 {env_path} 文件中填入你的 Gemini API Key，然后重新运行。")
        print(f"   获取地址: https://aistudio.google.com/apikey")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    print(f"🔑 Gemini API Key 已加载 (...{api_key[-4:]})")

    # ── 连接数据库 ──
    conn = sqlite3.connect(str(DB_PATH))
    print(f"✅ 已连接数据库: {DB_PATH}")

    # ── 确保 staging 表存在 ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_classification_stage (
            book_id       INTEGER PRIMARY KEY,
            title         TEXT,
            primary_category   TEXT,
            secondary_categories TEXT,
            canonical_tags TEXT,
            format_tags    TEXT,
            person_tags    TEXT,
            reason         TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # ── 加载书籍 ──
    books = load_books(conn)
    total = len(books)
    print(f"📚 共 {total} 本书待处理")

    # ── 断点续传 ──
    done_ids = get_already_classified(conn)
    remaining = [b for b in books if b["book_id"] not in done_ids]
    if done_ids:
        print(f"⏩ 已跳过 {len(done_ids)} 本已分类的书（断点续传）")
    print(f"🚀 本次需要处理 {len(remaining)} 本书\n")

    if not remaining:
        print("🎉 所有书籍已分类完毕！")
    else:
        # ── 分批处理 ──
        batches = [remaining[i:i+BATCH_SIZE] for i in range(0, len(remaining), BATCH_SIZE)]
        processed = len(done_ids)
        failed_books = []

        for batch_idx, batch in enumerate(batches, 1):
            ids_str = ", ".join(str(b["book_id"]) for b in batch)
            print(f"[Batch {batch_idx}/{len(batches)}] book_id: {ids_str}")

            try:
                results = call_gemini(client, batch)
                save_results(conn, results)
                processed += len(batch)
                pct = processed / total * 100
                filled = int(30 * processed / total)
                bar = "█" * filled + "░" * (30 - filled)
                print(f"  ✅ |{bar}| {processed}/{total} ({pct:.1f}%)")
            except Exception as e:
                print(f"  ❌ 批次失败: {e}")
                failed_books.extend(b["book_id"] for b in batch)
                continue

            # Gemini Free tier: 15 RPM → 每批间隔 4 秒确保不超限
            if batch_idx < len(batches):
                time.sleep(4)

        if failed_books:
            print(f"\n⚠️  {len(failed_books)} 本书分类失败: {failed_books}")

    # ── 回填 title ──
    backfill_titles(conn)

    # ── 最终统计 ──
    total_classified = conn.execute("SELECT COUNT(*) FROM ai_classification_stage").fetchone()[0]
    print(f"\n{'═' * 50}")
    print(f"  🎉 分类完成！共 {total_classified}/{total} 本书已入库")
    print(f"{'═' * 50}")

    # ── 分类分布 ──
    print("\n📊 分类分布:")
    dist = conn.execute("""
        SELECT primary_category, COUNT(*) AS cnt
        FROM ai_classification_stage
        GROUP BY primary_category
        ORDER BY cnt DESC
    """).fetchall()
    for cat, cnt in dist:
        bar = "█" * cnt
        print(f"  {cat:<10} {cnt:>3}  {bar}")

    conn.close()


if __name__ == "__main__":
    main()
