import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "talebook_data" / "books" / "library" / "metadata.db"

def safe_parse_json(raw):
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except:
        return []

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Read cleaned data
    rows = cur.execute("""
        SELECT book_id, canonical_tags, format_tags, person_tags
        FROM ai_classification_stage
    """).fetchall()

    for row in rows:
        book_id, can_tags, fmt_tags, p_tags = row
        
        # 2. Merge arrays and deduplicate while preserving order mostly
        tags_list = safe_parse_json(can_tags) + safe_parse_json(fmt_tags) + safe_parse_json(p_tags)
        clean_tags = list(dict.fromkeys(tags_list))
        
        # 3. Clear old tags for this book
        cur.execute("DELETE FROM books_tags_link WHERE book = ?", (book_id,))
        
        # 4. Insert new tags
        for tag_name in clean_tags:
            if not tag_name.strip():
                continue
            
            # Check if tag exists
            cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_row = cur.fetchone()
            
            if tag_row:
                tag_id = tag_row[0]
            else:
                cur.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                tag_id = cur.lastrowid
                
            cur.execute("INSERT INTO books_tags_link (book, tag) VALUES (?, ?)", (book_id, tag_id))

    conn.commit()
    conn.close()
    
    print("成功覆写所有书籍的底层标签，旧的脏标签已被完全清除！")

if __name__ == '__main__':
    main()
