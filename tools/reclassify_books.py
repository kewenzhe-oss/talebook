#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sqlite3
import os
import json
import sys

# Paths
DB_PATH = '/Users/grangerfdad/Desktop/running project/talebook-master-original/talebook_data/books/library/metadata.db'
AUTO_PY_PATH = '/Users/grangerfdad/Desktop/running project/talebook-master-original/talebook_data/books/settings/auto.py'

OLD_CATEGORIES = [
    '哲学与思想', '心理与自我', '关系与家庭', '文学与叙事',
    '历史与政治', '社会与文化', '商业与管理', '经济与投资',
    '科技与计算', '医疗与生命', '艺术与审美', '宗教与灵性'
]

# Map category ID to display name
CAT_NAMES = {
    "philosophy": "哲学与思想",
    "psychology": "心理与自我",
    "relationship": "关系与家庭",
    "literature": "文学与叙事",
    "history": "历史与政治",
    "society": "社会与文化",
    "business": "商业与管理",
    "economy": "经济与投资",
    "technology": "科技与计算",
    "health": "医疗与生命",
    "art": "艺术与审美",
    "religion": "宗教与灵性"
}

def load_categories_config():
    if not os.path.exists(AUTO_PY_PATH):
        print(f"Error: settings auto.py not found at {AUTO_PY_PATH}")
        sys.exit(1)
        
    # Read auto.py content and extract settings dict
    settings = {}
    with open(AUTO_PY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Execute auto.py in a local context to load settings
    local_vars = {}
    try:
        exec(content, {}, local_vars)
        settings = local_vars.get('settings', {})
    except Exception as e:
        print(f"Error executing auto.py: {e}")
        sys.exit(1)
        
    cat_str = settings.get('BOOK_CATEGORIES', '[]')
    try:
        return json.loads(cat_str)
    except Exception as e:
        print(f"Error parsing BOOK_CATEGORIES JSON: {e}")
        sys.exit(1)

def classify_book(title, tags, categories_config):
    # Filter out the 12 old main categories from the tags we use for matching
    clean_tags = [t for t in tags if t not in OLD_CATEGORIES]
    
    scores = {}
    reasons = {}
    
    for cat in categories_config:
        cat_id = cat["id"]
        scores[cat_id] = 0
        reasons[cat_id] = []
        
        # Get keywords for this category
        keywords = []
        for rule in cat.get("match_rules", []):
            if rule.get("enabled", True):
                keywords.extend(rule.get("keywords", []))
                
        # Match title
        for kw in keywords:
            if not kw:
                continue
            # Exact word or substring match in title
            if kw in title:
                # Higher weight for exact match or longer match
                weight = 5 if kw == title else (3 if len(kw) > 2 else 2)
                scores[cat_id] += weight
                reasons[cat_id].append(f"title_match:{kw}(+{weight})")
                
        # Match tags
        for tag in clean_tags:
            for kw in keywords:
                if not kw:
                    continue
                if kw == tag:
                    scores[cat_id] += 8
                    reasons[cat_id].append(f"tag_exact:{kw}(+8)")
                elif kw in tag:
                    scores[cat_id] += 4
                    reasons[cat_id].append(f"tag_sub:{kw} in {tag}(+4)")
                    
    # Find the category with the highest score
    best_cat_id = None
    max_score = 0
    
    for cat_id, score in scores.items():
        if score > max_score:
            max_score = score
            best_cat_id = cat_id
            
    if max_score > 0:
        return best_cat_id, reasons[best_cat_id], max_score
        
    # FALLBACK RULES when score is 0
    # 1. Check literature indicators in title/tags
    lit_indicators = ["小说", "随笔", "散文", "诗歌", "选集", "文集", "故事", "传记", "回忆录", "名著", "文学"]
    if any(ind in title for ind in lit_indicators) or any(any(ind in tag for ind in lit_indicators) for tag in clean_tags):
        return "literature", ["fallback_literature"], 0
        
    # 2. Check tech indicators
    tech_indicators = ["开发", "编程", "计算机", "安全", "网络", "系统", "算法", "科普", "科学"]
    if any(ind in title for ind in tech_indicators) or any(any(ind in tag for ind in tech_indicators) for tag in clean_tags):
        return "technology", ["fallback_technology"], 0
        
    # 3. Default catch-all
    return "society", ["fallback_default_society"], 0

def main():
    write_mode = "--write" in sys.argv
    
    print("=" * 80)
    print("TALEBOOK DYNAMIC BOOK RE-CLASSIFICATION TOOL")
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'WRITE' if write_mode else 'DRY-RUN'}")
    print("=" * 80)
    
    categories_config = load_categories_config()
    print(f"Loaded {len(categories_config)} category configurations.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all books
    cursor.execute("SELECT id, title FROM books")
    books = cursor.fetchall()
    print(f"Found {len(books)} books in database.")
    
    # Get tags for all books
    cursor.execute(
        "SELECT L.book, T.name FROM books_tags_link L JOIN tags T ON L.tag = T.id"
    )
    tag_rows = cursor.fetchall()
    
    book_tags_map = {}
    for book_id, tag_name in tag_rows:
        if book_id not in book_tags_map:
            book_tags_map[book_id] = []
        book_tags_map[book_id].append(tag_name)
        
    classification_results = []
    
    for book_id, title in books:
        tags = book_tags_map.get(book_id, [])
        cat_id, reason, score = classify_book(title, tags, categories_config)
        new_category_name = CAT_NAMES[cat_id]
        
        # Check current category tag linked
        cursor.execute(
            "SELECT T.name FROM tags T JOIN books_tags_link L ON T.id = L.tag "
            "WHERE L.book = ? AND T.name IN ({})".format(','.join('?' for _ in OLD_CATEGORIES)),
            [book_id] + OLD_CATEGORIES
        )
        current_cat_tags = [r[0] for r in cursor.fetchall()]
        current_cat_name = current_cat_tags[0] if current_cat_tags else "None"
        
        classification_results.append({
            "book_id": book_id,
            "title": title,
            "old_cat": current_cat_name,
            "new_cat": new_category_name,
            "new_cat_id": cat_id,
            "score": score,
            "reason": reason
        })
        
    # Preview and statistics
    print("\nCLASSIFICATION PREVIEW:")
    changed_count = 0
    cat_counts = {}
    
    for res in classification_results:
        cat_counts[res["new_cat"]] = cat_counts.get(res["new_cat"], 0) + 1
        if res["old_cat"] != res["new_cat"]:
            changed_count += 1
            if changed_count <= 20: # Show first 20 changes
                print(f"- [ID: {res['book_id']}] '{res['title']}'")
                print(f"  Mapping: {res['old_cat']} -> {res['new_cat']} (Score: {res['score']}, Reason: {', '.join(res['reason'][:3])})")
                
    print("\nCategory distribution after re-classification:")
    for cat_name, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat_name}: {count} books")
        
    print(f"\nSummary: {changed_count} books will be reclassified.")
    
    if not write_mode:
        print("\n[DRY RUN] No writes were committed. Run with '--write' to execute.")
        conn.close()
        return
        
    print("\n[WRITE MODE] Starting database update...")
    
    # Get tag IDs for the 12 main categories in metadata.db
    # (Create them if they don't exist)
    tag_ids_map = {}
    for cat_id, name in CAT_NAMES.items():
        cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            tag_ids_map[name] = row[0]
        else:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (name,))
            tag_ids_map[name] = cursor.lastrowid
            
    old_category_tag_ids = list(tag_ids_map.values())
    
    # Apply changes
    applied_count = 0
    for res in classification_results:
        book_id = res["book_id"]
        new_cat_name = res["new_cat"]
        new_tag_id = tag_ids_map[new_cat_name]
        
        # 1. Delete any existing links to the 12 old categories for this book
        cursor.execute(
            "DELETE FROM books_tags_link WHERE book = ? AND tag IN ({})".format(','.join('?' for _ in old_category_tag_ids)),
            [book_id] + old_category_tag_ids
        )
        
        # 2. Insert link to the new category
        cursor.execute(
            "INSERT OR IGNORE INTO books_tags_link (book, tag) VALUES (?, ?)",
            (book_id, new_tag_id)
        )
        
        # 3. Mark as dirtied for Calibre
        cursor.execute("INSERT OR IGNORE INTO metadata_dirtied (book) VALUES (?)", (book_id,))
        applied_count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully reclassified and saved {applied_count} books in database!")
    print("=" * 80)

if __name__ == '__main__':
    main()
