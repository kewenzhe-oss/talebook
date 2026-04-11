#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import datetime
from gettext import gettext as _


class SimpleBookFormatter:
    """格式化calibre book的字段"""

    def __init__(self, calibre_book_item, cdn_url):
        self.cdn_url = cdn_url
        self.book = calibre_book_item

    def get_collector(self):
        collector = self.book.get("collector", None)
        if isinstance(collector, dict):
            collector = collector.get("username", None)
        elif collector:
            collector = collector.username
        return collector

    def val(self, k, default_value=_("Unknown")):
        v = self.book.get(k, None)
        if not v:
            v = default_value
        if isinstance(v, datetime.datetime):
            return f'{v.year:04}-{v.month:02}-{v.day:02}'
        return v

    def format(self):
        b = self.book
        b["ts"] = b["timestamp"].strftime("%s")
        return {
            "id": b["id"],
            "title": b["title"],
            "rating": b["rating"],
            "timestamp": self.val("timestamp"),
            "pubdate": self.val("pubdate"),
            "author": ", ".join(b["authors"]),
            "authors": b["authors"],
            "author_sort": self.val("author_sort"),
            "tag": " / ".join(b["tags"]),
            "tags": b["tags"],
            "publisher": self.val("publisher"),
            "comments": self.val("comments", _(u"暂无简介")),
            "series": self.val("series", None),
            "language": self.val("language", None),
            "isbn": self.val("isbn", None),
            "img": self.cdn_url + "/get/cover/%(id)s.jpg?t=%(ts)s" % b,
            "thumb": self.cdn_url + "/get/thumb_60x80/%(id)s.jpg?t=%(ts)s" % b,
            # 额外填充的字段
            "collector": self.get_collector(),
            "count_visit": self.val("count_visit", 0),
            "count_download": self.val("count_download", 0),
        }


class BookFormatter:
    def __init__(self, tornado_handler, calibre_book_item):
        self.db = tornado_handler.db
        self.book = calibre_book_item
        self.cdn_url = tornado_handler.cdn_url
        self.api_url = tornado_handler.api_url
        self.handler = tornado_handler

    def get_files(self):
        files = []
        book_id = self.book["id"]
        for fmt in self.book.get("available_formats", ""):
            try:
                filesize = self.db.sizeof_format(book_id, fmt, index_is_id=True)
            except:
                continue
            item = {
                "format": fmt,
                "size": filesize,
                "href": self.cdn_url + "/api/book/%s.%s" % (book_id, fmt),
            }
            files.append(item)
        return files

    def get_permissions(self):
        h = self.handler
        user_id = h.user_id()
        return {
            # 图书权限数据
            "is_public": True,
            "is_owner": user_id and (h.is_admin() or h.is_book_owner(self.book["id"], user_id)),
        }

    def format(self, with_files=False, with_perms=False):
        f = SimpleBookFormatter(self.book, self.cdn_url)
        data = f.format()
        data.update(
            {
                "author_url": self.api_url + "/author/" + f.val("author_sort"),
                "publisher_url": self.api_url + "/publisher/" + f.val("publisher"),
            }
        )
        if with_files:
            data["files"] = self.get_files()
        if with_perms:
            data.update(self.get_permissions())
        return data


def compare_books_by_rating_or_id(x, y):
    a = x.get("rating", 0) or 0
    b = y.get("rating", 0) or 0

    if a > b:
        return 1
    elif a < b:
        return -1
    elif x["id"] > y["id"]:
        return 1
    else:
        return -1


def super_strip(s):
    # 删除掉所有不可见的字符
    # issue: https://github.com/talebook/talebook/issues/304
    return ''.join(c for c in s.strip() if c.isprintable())


def check_rule(book_meta, rule):
    """检查单条规则是否命中"""
    keywords = rule.get("keywords", [])
    match_fields = rule.get("match_fields", ["tags"])
    exclude_keywords = rule.get("exclude_keywords", [])
    
    # 构建待匹配文本
    texts = {}
    if "tags" in match_fields:
        texts["tags"] = " ".join(book_meta.get("tags", []))
    # book_meta 从数据库直接读取时是字典，从calibre返回时可能是对象
    title = book_meta.get("title", "") if isinstance(book_meta, dict) else getattr(book_meta, "title", "")
    authors = book_meta.get("authors", []) if isinstance(book_meta, dict) else getattr(book_meta, "authors", [])
    if "title" in match_fields:
        texts["title"] = title
    if "author" in match_fields:
        texts["author"] = " ".join(authors)
    
    combined_text = " ".join(texts.values())
    
    # 排除词检查
    for ex in exclude_keywords:
        if ex and ex in combined_text:
            return None
    
    # 关键词匹配
    for kw in keywords:
        if not kw:
            continue
        for field_name, text in texts.items():
            if kw in text:
                return {"keyword": kw, "field": field_name}
    
    return None

def match_book_to_categories(book_meta, categories_config):
    """
    返回该书命中的所有分类，以及命中原因。
    """
    results = []
    
    for category in categories_config:
        if not category.get("enabled", True):
            continue
        
        hit_parent = False
        for rule in category.get("match_rules", []):
            if not rule.get("enabled", True):
                continue
            
            hit = check_rule(book_meta, rule)
            if hit:
                results.append({
                    "category_id": category["id"],
                    "category_name": category["name"],
                    "matched_keyword": hit["keyword"],
                    "matched_field": hit["field"],
                    "rule_id": rule.get("id"),
                })
                hit_parent = True
                break  # 一个分类只需命中一次
        
        # 检查子分类
        for child in category.get("children", []):
            if not child.get("enabled", True):
                continue
            for rule in child.get("match_rules", []):
                if not rule.get("enabled", True):
                    continue
                hit = check_rule(book_meta, rule)
                if hit:
                    results.append({
                        "category_id": child["id"],
                        "parent_id": category["id"],
                        "category_name": child["name"],
                        "matched_keyword": hit["keyword"],
                        "matched_field": hit["field"],
                        "rule_id": rule.get("id"),
                    })
                    break
    
    return results
