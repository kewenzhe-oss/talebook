#!/usr/bin/env python3
"""
分类数据质量审核脚本 - 只读查询 ai_classification_stage 表，
输出结构化诊断报告。
"""

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "talebook_data" / "books" / "library" / "metadata.db"

VALID_CATEGORIES = [
    "哲学与思想", "心理与自我", "关系与家庭", "文学与叙事",
    "历史与政治", "社会与文化", "商业与管理", "经济与投资",
    "科技与计算", "医疗与生命", "艺术与审美", "宗教与灵性",
    "待整理",
]

LITERARY_KEYWORDS = {"小说", "科幻", "文学", "散文", "诗歌", "戏剧", "寓言", "童话", "杂文", "随笔", "纪实文学", "传记文学"}


def load_all(conn):
    rows = conn.execute("""
        SELECT s.book_id, s.title, s.primary_category,
               s.secondary_categories, s.canonical_tags,
               s.format_tags, s.person_tags, s.reason
        FROM ai_classification_stage s
    """).fetchall()
    books = []
    for r in rows:
        books.append({
            "book_id": r[0], "title": r[1], "primary_category": r[2],
            "secondary_categories_raw": r[3], "canonical_tags_raw": r[4],
            "format_tags_raw": r[5], "person_tags_raw": r[6], "reason": r[7],
        })
    return books


def safe_parse_json(raw, field_name, book_id):
    if not raw or raw.strip() == "":
        return [], None
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return [], "book_id=%d %s: not a list, got %s" % (book_id, field_name, type(data).__name__)
        return data, None
    except json.JSONDecodeError as e:
        return [], "book_id=%d %s: JSON parse error: %s" % (book_id, field_name, e)


def main():
    conn = sqlite3.connect("file:%s?mode=ro" % DB_PATH, uri=True)
    books = load_all(conn)
    total = len(books)
    print("loaded %d records\n" % total)

    # ══════════════════════════════════════════════════════
    # 1. Structure & Formatting
    # ══════════════════════════════════════════════════════
    invalid_category = []
    json_errors = []
    category_in_tags = []
    parsed_books = []

    cat_set = set(VALID_CATEGORIES) - {"待整理"}

    for b in books:
        if b["primary_category"] not in VALID_CATEGORIES:
            invalid_category.append(b)

        errors = []
        parsed = {"book_id": b["book_id"], "title": b["title"], "primary_category": b["primary_category"]}
        for field in ["secondary_categories", "canonical_tags", "format_tags", "person_tags"]:
            arr, err = safe_parse_json(b["%s_raw" % field], field, b["book_id"])
            parsed[field] = arr
            if err:
                errors.append(err)
        if errors:
            json_errors.extend(errors)

        for field in ["canonical_tags", "format_tags", "person_tags"]:
            for tag in parsed[field]:
                if tag in cat_set:
                    category_in_tags.append({
                        "book_id": b["book_id"], "title": b["title"],
                        "field": field, "offending_tag": tag,
                    })

        parsed_books.append(parsed)

    print("=" * 60)
    print("  1. STRUCTURE & FORMATTING")
    print("=" * 60)
    print("  Total records: %d" % total)
    print("  Invalid primary_category: %d" % len(invalid_category))
    for b in invalid_category:
        print("     - [%d] %s -> '%s'" % (b["book_id"], b["title"], b["primary_category"]))
    print("  JSON parse failures: %d" % len(json_errors))
    for e in json_errors[:5]:
        print("     - %s" % e)
    print("  Category name leaked into tags: %d" % len(category_in_tags))
    for c in category_in_tags[:10]:
        print("     - [%d] %s -> %s contains '%s'" % (c["book_id"], c["title"], c["field"], c["offending_tag"]))

    # ══════════════════════════════════════════════════════
    # 2. Boundary Anomalies
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  2. BOUNDARY ANOMALIES")
    print("=" * 60)

    # 2a. Literary content in non-literary categories
    non_literary_cats = [c for c in VALID_CATEGORIES if c not in ("文学与叙事", "待整理")]
    literary_suspects = []
    for b in parsed_books:
        if b["primary_category"] in non_literary_cats:
            all_tags = b["format_tags"] + b["canonical_tags"]
            found_words = [w for w in LITERARY_KEYWORDS if any(w in t for t in all_tags)]
            if found_words:
                literary_suspects.append({
                    "book_id": b["book_id"], "title": b["title"],
                    "category": b["primary_category"],
                    "found": ", ".join(found_words),
                    "format_tags": b["format_tags"],
                    "canonical_tags": b["canonical_tags"],
                })
    print("\n  Suspected literary works in non-literary categories: %d" % len(literary_suspects))
    for s in literary_suspects:
        print("     - [%d] %s (cat: %s, detected: %s, format: %s)" % (
            s["book_id"], s["title"], s["category"], s["found"], s["format_tags"]))

    # 2b. Orphan long tags
    tag_counter = Counter()
    for b in parsed_books:
        for t in b["canonical_tags"]:
            tag_counter[t] += 1
    orphan_long = [(tag, cnt) for tag, cnt in tag_counter.items()
                   if cnt == 1 and len(tag) > 8]
    orphan_long.sort(key=lambda x: len(x[0]), reverse=True)
    print("\n  Orphan tags (count=1, length>8): %d total" % len(orphan_long))
    print("  Top 10 longest:")
    for tag, _ in orphan_long[:10]:
        print("     - [%d chars] %s" % (len(tag), tag))

    # 2c. Unresolved
    unresolved = [b for b in parsed_books if b["primary_category"] == "待整理"]
    print("\n  Unresolved (primary=pending): %d" % len(unresolved))
    for b in unresolved:
        print("     - [%d] %s tags: %s" % (b["book_id"], b["title"], b["canonical_tags"]))

    # ══════════════════════════════════════════════════════
    # 3. Top Tags per Category
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  3. TOP CANONICAL TAGS PER CATEGORY")
    print("=" * 60)

    cat_tag_counters = defaultdict(Counter)
    cat_counts = Counter()
    for b in parsed_books:
        cat = b["primary_category"]
        cat_counts[cat] += 1
        for t in b["canonical_tags"]:
            cat_tag_counters[cat][t] += 1

    for cat in VALID_CATEGORIES:
        if cat not in cat_tag_counters:
            continue
        n = cat_counts[cat]
        top = cat_tag_counters[cat].most_common(10)
        top_str = ", ".join("%s(%d)" % (t, c) for t, c in top)
        print("\n  [%s] (%d books)" % (cat, n))
        print("     %s" % top_str)

    # ══════════════════════════════════════════════════════
    # 4. Additional Stats
    # ══════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  4. ADDITIONAL STATS")
    print("=" * 60)

    unique_canonical = len(tag_counter)
    singleton_tags = sum(1 for c in tag_counter.values() if c == 1)
    print("  Unique canonical_tags: %d" % unique_canonical)
    print("  Singletons (count=1): %d (%.1f%%)" % (singleton_tags, singleton_tags / unique_canonical * 100))

    # format_tags
    fmt_counter = Counter()
    for b in parsed_books:
        for t in b["format_tags"]:
            fmt_counter[t] += 1
    print("\n  format_tags distribution (Top 15):")
    for t, c in fmt_counter.most_common(15):
        print("     %s: %d" % (t, c))

    # person_tags
    per_counter = Counter()
    for b in parsed_books:
        for t in b["person_tags"]:
            per_counter[t] += 1
    print("\n  person_tags distribution (Top 15):")
    for t, c in per_counter.most_common(15):
        print("     %s: %d" % (t, c))

    # secondary_categories usage
    sec_usage = sum(1 for b in parsed_books if b["secondary_categories"])
    print("\n  Books with secondary_categories: %d/%d (%.1f%%)" % (sec_usage, total, sec_usage / total * 100))

    conn.close()
    print("\n" + "=" * 60)
    print("  AUDIT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
