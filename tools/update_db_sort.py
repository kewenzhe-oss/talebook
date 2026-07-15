import sqlite3
import os
import re
import argparse
from pypinyin import pinyin, Style

DEFAULT_DB_PATH = '/Users/grangerfdad/Desktop/running project/talebook-master-original/talebook_data/books/library/metadata.db'

def is_chinese_char(c):
    return '\u4e00' <= c <= '\u9fff'

def convert_sort_field(sort_val):
    if not sort_val:
        return ""
    
    # 1. Strip leading "The ", "A ", "An " (case-insensitive)
    cleaned = re.sub(r'^(the|a|an)\s+', '', sort_val, flags=re.IGNORECASE)
    
    # 2. Check if it contains Chinese characters
    has_chinese = any(is_chinese_char(c) for c in cleaned)
    
    if not has_chinese:
        # Pure English/Non-Chinese title: return cleaned (with leading The/A/An stripped), lowercase
        return cleaned.lower()
    
    # Chinese or mixed: convert Chinese to full pinyin (lowercase) separated by spaces, keeping others
    parts = []
    for char in cleaned:
        if is_chinese_char(char):
            py_list = pinyin(char, style=Style.NORMAL)
            if py_list and py_list[0] and py_list[0][0]:
                parts.append((py_list[0][0].lower(), True))
            else:
                parts.append((char.lower(), False))
        else:
            parts.append((char.lower(), False))
            
    assembled = []
    for idx, (val, is_ch) in enumerate(parts):
        if idx == 0:
            assembled.append(val)
            continue
        
        prev_val, prev_is_ch = parts[idx - 1]
        
        if is_ch:
            if prev_is_ch:
                assembled.append(" " + val)
            else:
                if prev_val.endswith(" ") or prev_val.endswith("\t"):
                    assembled.append(val)
                else:
                    assembled.append(" " + val)
        else:
            if prev_is_ch:
                if val.startswith(" ") or val.startswith("\t"):
                    assembled.append(val)
                else:
                    assembled.append(" " + val)
            else:
                assembled.append(val)
                
    final_str = "".join(assembled)
    final_str = re.sub(r'\s+', ' ', final_str).strip()
    return final_str

def main():
    parser = argparse.ArgumentParser(description="Update Calibre database sort fields.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to metadata.db")
    parser.add_argument("--write", action="store_true", help="Perform the actual write operation to database")
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Error: Database not found at {args.db_path}")
        return

    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()

    # 1. Stats: total books
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    # Stats: books with pubdate
    cursor.execute("SELECT COUNT(*) FROM books WHERE pubdate IS NOT NULL AND pubdate != ''")
    pubdate_count = cursor.fetchone()[0]
    pubdate_ratio = (pubdate_count / total_books) * 100 if total_books > 0 else 0

    print("=" * 60)
    print("DATABASE METRICS:")
    print(f"Total Books: {total_books}")
    print(f"Books with valid pubdate: {pubdate_count} ({pubdate_ratio:.2f}%)")
    print("=" * 60)

    # 2. Fetch all books
    cursor.execute("SELECT id, title, sort FROM books")
    rows = cursor.fetchall()

    changes = []
    for book_id, title, sort_val in rows:
        converted = convert_sort_field(sort_val)
        if sort_val != converted:
            changes.append((book_id, title, sort_val, converted))

    print(f"Total records that need updating: {len(changes)}")

    # Preview first 10 changes (as requested)
    print("\nPreview of first 10 updates:")
    for idx, (book_id, title, original, proposed) in enumerate(changes[:10]):
        print(f"{idx+1}. [ID: {book_id}]")
        print(f"   Title:    {title}")
        print(f"   Original: {original}")
        print(f"   Proposed: '{proposed}'")
        print("-" * 60)

    if not args.write:
        print("\n[DRY RUN] No changes were written. Run with --write to perform the updates.")
        conn.close()
        return

    # 3. Perform write operation
    print("\nWriting updates to database...")
    updated_count = 0
    for book_id, title, original, proposed in changes:
        cursor.execute("UPDATE books SET sort=? WHERE id=?", (proposed, book_id))
        updated_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully updated {updated_count} books in database.")

if __name__ == '__main__':
    main()
