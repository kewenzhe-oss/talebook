#!/usr/bin/env python3
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "talebook_data" / "books" / "library" / "metadata.db"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "categories_export.json"

CATEGORY_MAP = {
    "哲学与思想": {"id": "philosophy", "icon": "mdi-head-lightbulb"},
    "心理与自我": {"id": "psychology", "icon": "mdi-brain"},
    "关系与家庭": {"id": "relationship", "icon": "mdi-home-heart"},
    "文学与叙事": {"id": "literature", "icon": "mdi-book-open-page-variant"},
    "历史与政治": {"id": "history", "icon": "mdi-bank"},
    "社会与文化": {"id": "society", "icon": "mdi-account-group"},
    "商业与管理": {"id": "business", "icon": "mdi-briefcase"},
    "经济与投资": {"id": "economy", "icon": "mdi-chart-line"},
    "科技与计算": {"id": "technology", "icon": "mdi-desktop-mac"},
    "医疗与生命": {"id": "health", "icon": "mdi-hospital-box"},
    "艺术与审美": {"id": "art", "icon": "mdi-palette"},
    "宗教与灵性": {"id": "religion", "icon": "mdi-yin-yang"},
}

def safe_parse_json(raw):
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except:
        return []

def main():
    # We use string formatting for python 3.9 compatibility
    conn = sqlite3.connect("file:%s?mode=ro" % DB_PATH, uri=True)
    rows = conn.execute("""
        SELECT primary_category, canonical_tags, format_tags, person_tags
        FROM ai_classification_stage
    """).fetchall()

    cat_tag_counters = defaultdict(Counter)

    for r in rows:
        cat = r[0]
        if cat not in CATEGORY_MAP:
            continue
        
        tags = safe_parse_json(r[1]) + safe_parse_json(r[2]) + safe_parse_json(r[3])
        for tag in tags:
            cat_tag_counters[cat][tag] += 1

    categories_config = []
    
    for cat_name, info in CATEGORY_MAP.items():
        counter = cat_tag_counters.get(cat_name, Counter())
        
        # 只保留出现次数大于1的标签，并取前20个
        top_tags = [tag for tag, count in counter.most_common() if count > 1][:20]
        
        categories_config.append({
            "id": info["id"],
            "name": cat_name,
            "icon": info["icon"],
            "enabled": True,
            "match_rules": [
                {
                    "id": "rule_%s_1" % info["id"],
                    "keywords": top_tags,
                    "match_fields": ["tags", "title"],
                    "enabled": True
                }
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(categories_config, f, ensure_ascii=False, indent=2)

    print(json.dumps(categories_config, ensure_ascii=False, indent=2))
    conn.close()

if __name__ == "__main__":
    main()
