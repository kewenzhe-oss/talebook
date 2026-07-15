import sqlite3
import os
import re
import argparse
import uuid
from pypinyin import pinyin, Style

DEFAULT_DB_PATH = '/Users/grangerfdad/Desktop/running project/talebook-master-original/talebook_data/books/library/metadata.db'
MAPPING_FILE_PATH = '/Users/grangerfdad/.gemini/antigravity-ide/brain/2e9bd605-92fd-441d-80b0-807e294cc672/scratch/classified_books_12_perfect.txt'

OLD_CATEGORIES = [
    '哲学与思想', '心理与自我', '关系与家庭', '文学与叙事',
    '历史与政治', '社会与文化', '商业与管理', '经济与投资',
    '科技与计算', '医疗与生命', '艺术与审美', '宗教与灵性'
]

def is_chinese_char(c):
    return '\u4e00' <= c <= '\u9fff'

def convert_sort_field(title):
    if not title:
        return ""
    
    # Clean leading/trailing quotes and brackets
    cleaned = title.strip()
    cleaned = re.sub(r'^([《「『【“"（(\s]+)', '', cleaned)
    cleaned = re.sub(r'([》」』】”"）)\s]+)$', '', cleaned)
    
    # 1. Strip leading "The ", "A ", "An " (case-insensitive)
    cleaned = re.sub(r'^(the|a|an)\s+', '', cleaned, flags=re.IGNORECASE)
    
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

def parse_mapping_file(path):
    if not os.path.exists(path):
        print(f"Error: Classification mapping file not found at {path}")
        return []
    
    entries = []
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                try:
                    book_id = int(parts[0])
                    title = parts[1]
                    category = parts[2]
                    entries.append((book_id, title, category))
                except ValueError:
                    print(f"Warning: line {line_num} has invalid book ID: {line}")
            else:
                print(f"Warning: line {line_num} is not in 'ID | Title | Category | Keywords' format: {line}")
    return entries

def run_migration():
    parser = argparse.ArgumentParser(description="Calibre DB Sort & Classification Migration Script.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to metadata.db")
    parser.add_argument("--mapping-path", default=MAPPING_FILE_PATH, help="Path to classification mapping file")
    parser.add_argument("--write", action="store_true", help="Perform the actual write operation to database")
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Error: Database not found at {args.db_path}")
        return

    # Load mapping entries
    mapping_entries = parse_mapping_file(args.mapping_path)
    if not mapping_entries:
        print("Error: No classification entries parsed. Aborting.")
        return

    conn = sqlite3.connect(args.db_path)
    # Register custom functions to avoid errors when SQLite triggers compile/evaluate them
    conn.create_function("title_sort", 1, lambda x: x)
    conn.create_function("uuid4", 0, lambda: str(uuid.uuid4()))
    cursor = conn.cursor()

    # ----------------------------------------------------
    # Task 3: Check pubdate statistics (Dry-run & Write)
    # ----------------------------------------------------
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM books WHERE pubdate IS NOT NULL AND pubdate != ''")
    pubdate_count = cursor.fetchone()[0]
    pubdate_ratio = (pubdate_count / total_books) * 100 if total_books > 0 else 0

    print("=" * 70)
    print("TASK 3: PUBLICATION DATE (pubdate) FILL RATE STATISTICS")
    print(f"Total Books in library: {total_books}")
    print(f"Books with valid pubdate data: {pubdate_count} ({pubdate_ratio:.2f}%)")
    print("=" * 70)

    # ----------------------------------------------------
    # Task 1: Generate sort field changes
    # ----------------------------------------------------
    cursor.execute("SELECT id, title, sort FROM books")
    book_rows = cursor.fetchall()
    
    sort_changes = []
    for book_id, title, sort_val in book_rows:
        converted = convert_sort_field(title) # Using title field now!
        if sort_val != converted:
            sort_changes.append((book_id, title, sort_val, converted))

    print(f"\nTASK 1: SORT FIELD UPDATES PREVIEW")
    print(f"Total book sort fields to update: {len(sort_changes)}")
    print("Preview of first 10 changes:")
    for idx, (book_id, title, original, proposed) in enumerate(sort_changes[:10]):
        print(f"{idx+1}. [ID: {book_id}] '{title}'")
        print(f"   Original: {original}")
        print(f"   Proposed: {proposed}")
        print("-" * 50)
    print("=" * 70)

    # ----------------------------------------------------
    # Task 2: Generate classification changes
    # ----------------------------------------------------
    # We find existing IDs for the 12 old categories to optimize queries
    cursor.execute(
        "SELECT id, name FROM tags WHERE name IN ({})".format(','.join('?' for _ in OLD_CATEGORIES)), 
        OLD_CATEGORIES
    )
    old_category_tag_map = {name: tid for tid, name in cursor.fetchall()}
    old_category_tag_ids = list(old_category_tag_map.values())

    classification_changes = []
    for book_id, title, new_category in mapping_entries:
        # Check current category tags for this book
        if old_category_tag_ids:
            cursor.execute(
                "SELECT T.name FROM tags T JOIN books_tags_link L ON T.id = L.tag "
                "WHERE L.book = ? AND L.tag IN ({})".format(','.join('?' for _ in old_category_tag_ids)),
                [book_id] + old_category_tag_ids
            )
            current_tags = [row[0] for row in cursor.fetchall()]
        else:
            current_tags = []

        old_category_str = ", ".join(current_tags) if current_tags else "None"
        
        # Check if the new category is already the only category linked (to avoid redundant changes)
        if len(current_tags) == 1 and current_tags[0] == new_category:
            continue
            
        classification_changes.append((book_id, title, old_category_str, new_category))

    print(f"\nTASK 2: BOOK CLASSIFICATION UPDATES PREVIEW")
    print(f"Total books to reclassify: {len(classification_changes)}")
    print("Preview of first 10 changes:")
    for idx, (book_id, title, old_cat, new_cat) in enumerate(classification_changes[:10]):
        print(f"{idx+1}. [ID: {book_id}] '{title}'")
        print(f"   Reclassification: {old_cat} -> {new_cat}")
        print("-" * 50)
    print("=" * 70)

    if not args.write:
        print("\n[DRY RUN] No modifications were written to the database.")
        print("Run the script with the '--write' flag to apply these changes.")
        conn.close()
        return

    # ----------------------------------------------------
    # WRITE MODE: Executing writes sequentially
    # ----------------------------------------------------
    print("\n[WRITE MODE] Starting database write transactions...")

    # Write Step 1: Write sort changes
    print("Step 1/3: Writing sort field updates...")
    updated_sort_count = 0
    for book_id, _, _, proposed in sort_changes:
        cursor.execute("UPDATE books SET sort=? WHERE id=?", (proposed, book_id))
        # Mark metadata dirtied
        cursor.execute("INSERT OR IGNORE INTO metadata_dirtied (book) VALUES (?)", (book_id,))
        updated_sort_count += 1
    print(f"-> Successfully updated {updated_sort_count} sort fields.")

    # Write Step 2: Write classification changes
    print("Step 2/3: Writing book classification updates...")
    updated_class_count = 0
    for book_id, _, old_cat, new_category in classification_changes:
        # Delete links to any of the 12 old categories for this book
        if old_category_tag_ids:
            cursor.execute(
                "DELETE FROM books_tags_link WHERE book = ? AND tag IN ({})".format(','.join('?' for _ in old_category_tag_ids)),
                [book_id] + old_category_tag_ids
            )
            
        # Get or create the new category tag
        cursor.execute("SELECT id FROM tags WHERE name = ?", (new_category,))
        tag_row = cursor.fetchone()
        if tag_row:
            new_tag_id = tag_row[0]
        else:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (new_category,))
            new_tag_id = cursor.lastrowid
            
        # Link the book to the new category tag
        cursor.execute("INSERT OR IGNORE INTO books_tags_link (book, tag) VALUES (?, ?)", (book_id, new_tag_id))
        
        # Mark metadata dirtied
        cursor.execute("INSERT OR IGNORE INTO metadata_dirtied (book) VALUES (?)", (book_id,))
        updated_class_count += 1
        
    print(f"-> Successfully reclassified {updated_class_count} books.")

    # Write Step 3: Commit and output confirmation report
    conn.commit()
    conn.close()
    print("\nDatabase transaction committed successfully!")
    print("=" * 70)
    print("MIGRATION COMPLETED:")
    print(f"1. Updated {updated_sort_count} book sort fields to spaced full pinyin.")
    print(f"2. Reclassified {updated_class_count} books into unique main categories.")
    print(f"3. Statistics: {pubdate_count} of {total_books} books have pubdate ({pubdate_ratio:.2f}%).")
    print("=" * 70)

if __name__ == '__main__':
    run_migration()
