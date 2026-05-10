#!/usr/bin/env python3
"""
Extract a specific page from WordPress.2024-08-07.xml and convert to Quartz markdown.
Usage: python3 extract_specific_page.py "אודות"
"""

import xml.etree.ElementTree as ET
import os
import re
import sys
from pathlib import Path

try:
    from markdownify import markdownify as md
except ImportError:
    print("Please install markdownify first: pip install markdownify")
    sys.exit(1)

# Resolve project root (three levels up from this script)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# File paths
XML_FILE = PROJECT_ROOT / "archive" / "WordPress.2024-08-07.xml"
PAGES_DIR = PROJECT_ROOT / "content" / "עמודים"

# WordPress XML namespaces
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

def safe_get_text(element, tag, namespaces, default=""):
    """Helper to safely extract text from an XML element."""
    found = element.find(tag, namespaces)
    return found.text if found is not None and found.text else default

def sanitize_filename(filename):
    """Removes illegal characters from filenames."""
    clean = re.sub(r'[\\/*?:"<>|]', "", filename)
    clean = clean.replace('\n', ' ').replace('\r', '').strip()
    return clean if clean else "Untitled"

def remove_shortcodes(text):
    """Remove WordPress and Fusion Builder shortcodes from text."""
    if not text:
        return text
    # Match patterns like [fullwidth ...], [fusion_text], [/fullwidth], etc.
    text = re.sub(r'\[/?[a-zA-Z_-]+[^\]]*\]', '', text)
    # Clean up multiple consecutive newlines
    text = re.sub(r'\n\n+', '\n\n', text)
    return text.strip()

def main(page_title=None):
    """
    Extract pages from XML and convert to markdown.
    If page_title is provided, extract only that specific page.
    If page_title is None, extract all pages.
    Returns the count of pages extracted.
    """
    print(f"Loading XML file from: {XML_FILE}...")
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        channel = root.find('channel')
    except Exception as e:
        print(f"Error reading XML: {e}")
        return 0

    # Build author lookup dictionary
    authors_by_login = {}
    for author_elem in channel.findall('wp:author', NAMESPACES):
        login = safe_get_text(author_elem, 'wp:author_login', NAMESPACES)
        if login:
            authors_by_login[login] = {
                'display_name': safe_get_text(author_elem, 'wp:author_display_name', NAMESPACES),
                'email': safe_get_text(author_elem, 'wp:author_email', NAMESPACES)
            }

    # Create pages directory
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    # If page_title is specified, search for that specific page
    if page_title is not None:
        print(f"Searching for page: {page_title}...")
    else:
        print("Extracting all pages...")

    pages_written = 0

    for item in channel.findall('item'):
        # Only process pages
        post_type = safe_get_text(item, 'wp:post_type', NAMESPACES)
        if post_type != 'page':
            continue

        title_elem = item.find('title')
        title = (title_elem.text if title_elem is not None and title_elem.text else None) or "Untitled"

        # If looking for specific page, check if this is the one
        if page_title is not None and title.strip() != page_title.strip():
            continue

        # Extract metadata
        creator = safe_get_text(item, 'dc:creator', NAMESPACES)
        post_id = safe_get_text(item, 'wp:post_id', NAMESPACES)
        pub_date = safe_get_text(item, 'wp:post_date', NAMESPACES)
        status = safe_get_text(item, 'wp:status', NAMESPACES)

        # Get author display name
        author_display_name = ""
        if creator in authors_by_login:
            author_display_name = authors_by_login[creator]['display_name']

        # Extract content and convert to markdown
        raw_html = safe_get_text(item, 'content:encoded', NAMESPACES)

        # Convert HTML to markdown
        markdown_content = md(raw_html, heading_style="ATX") if raw_html else ""

        # Remove shortcodes
        markdown_content = remove_shortcodes(markdown_content)

        # Generate file path
        safe_title = sanitize_filename(title)
        filepath = PAGES_DIR / f"{safe_title}.md"

        # Handle collisions
        if filepath.exists():
            filepath = PAGES_DIR / f"{safe_title} - {post_id}.md"

        # Write the markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            # YAML Frontmatter
            f.write("---\n")
            yaml_title = title.replace('"', "'").replace('\n', ' ').strip()
            f.write(f"title: \"{yaml_title}\"\n")
            f.write("publish: true\n")
            f.write(f"date: {pub_date}\n")

            # Author reference
            f.write(f"author: [[{creator}]]\n")

            f.write("---\n\n")

            # Page content
            f.write(f"# {title}\n\n")
            f.write(markdown_content)

        if page_title is not None:
            print(f"\n✓ Successfully created: {filepath}")
            print(f"  - Title: {title}")
            print(f"  - Author: {creator} ({author_display_name})")
            print(f"  - Date: {pub_date}")
            print(f"  - Status: {status}")

        pages_written += 1

        # If extracting a specific page, we're done
        if page_title is not None:
            break

    if page_title is not None and pages_written == 0:
        print(f"✗ Page '{page_title}' not found in XML.")
    elif page_title is None:
        print(f"\n✓ Successfully extracted {pages_written} pages.")

    # If we're running a full extraction, ensure the site index exists.
    if page_title is None:
        INDEX_PATH = PROJECT_ROOT / "content" / "index.md"
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

        index_content = '''---
title: "הומניסט"
publish: true
description: "ארכיון הומניסט — גן רעיונות"
socialImage: "https://humanist-co-il-quartz.vercel.app/assets/branding/Humanist_banner.png"
---

![באנר הומניסט](/assets/branding/Humanist_banner.png)

ברוכים הבאים לארכיון **הומניסט** — מיזם קהילתי שפעל בין 2016 ל-2022
ליצירת מגזין מקוון לקהילה ההומניסטית-חילונית בישראל.

האתר כלל מאמרים, דעות ורעיונות בתחומי פוליטיקה, מדע, תרבות, הגות
ופובליציסטיקה מנקודת ראות של הומניזם חילוני וליברלי.

ארכיון זה שומר את התכנים שפורסמו באתר המקורי כגן רעיונות — עיינו לפי [[כותבים|כותבים]], לפי תגיות,
או חפשו חופשי בארכיון.

[[עמודים/אודות|← אודות הפרויקט]]

'''

        try:
            with open(INDEX_PATH, 'w', encoding='utf-8') as idxf:
                idxf.write(index_content)
            print(f"\n✓ Ensured site index written to: {INDEX_PATH.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"Failed to write index file {INDEX_PATH}: {e}")

    return pages_written

def extract_and_convert_page(page_title):
    """Extract a specific page from XML and convert to markdown. (Legacy wrapper)"""
    result = main(page_title)
    return result > 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_specific_page.py \"Page Title\"")
        print("Example: python3 extract_specific_page.py \"אודות\"")
        sys.exit(1)

    page_title = sys.argv[1]
    count = main(page_title)
    sys.exit(0 if count > 0 else 1)
