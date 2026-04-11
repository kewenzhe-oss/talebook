#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
This script prunes legacy category names that were mistakenly injected as tags into the Calibre database.
It removes tags that match legacy category names configured in BOOK_NAV.
"""

import os
import sys

# Setup environment
path = os.environ.get('CALIBRE_PYTHON_PATH', '/usr/lib/calibre')
if path not in sys.path:
    sys.path.insert(0, path)
sys.path.insert(0, '../')

from webserver import loader
from calibre.db.legacy import LibraryDatabase

CONF = loader.get_settings()

def get_legacy_category_names():
    nav_lines = CONF.get("BOOK_NAV", "").split("\n")
    categories = set()
    for line in nav_lines:
        line = line.strip()
        if not line or "=" not in line:
            continue
        cat_name, _ = line.split("=", 1)
        categories.add(cat_name.strip())
    
    # Optional supplementary list of raw categories
    categories.update(["工作", "交友", "爱", "商业", "人文"])
    return categories

def main(library_path):
    if not os.path.isdir(library_path):
        # Allow passing the db file directly and extract the dir
        if os.path.isfile(library_path):
            library_path = os.path.dirname(library_path)

    print("Connecting to Calibre library at:", library_path)
    db = LibraryDatabase(os.path.expanduser(library_path))
    
    legacy_categories = get_legacy_category_names()
    print("Legacy categories to prune as tags:", legacy_categories)
    
    ids = db.search_getting_ids('', None)
    total = len(ids)
    print(f"Checking {total} books for tag pollution...")
    
    books = db.get_data_as_dict(ids=ids)
    
    count_updated = 0
    for book in books:
        book_id = book['id']
        current_tags = book.get('tags', [])
        if not current_tags:
            continue
            
        new_tags = [t for t in current_tags if t not in legacy_categories]
        
        if len(new_tags) != len(current_tags):
            removed = set(current_tags) - set(new_tags)
            print(f"[Book {book_id}] - '{book['title']}' | Removed tags: {removed}")
            
            # Apply update
            mi = db.get_metadata(book_id, index_is_id=True)
            mi.tags = new_tags
            db.set_metadata(book_id, mi)
            count_updated += 1
            
    print(f"Done! Cleaned tag pollution for {count_updated} books.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <library-path-dir>")
        sys.exit(1)
        
    main(sys.argv[1])
