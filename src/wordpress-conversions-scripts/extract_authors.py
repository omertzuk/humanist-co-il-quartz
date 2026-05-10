import xml.etree.ElementTree as ET
import os
import json
from pathlib import Path

# Resolve project root (three levels up from this script)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# File paths based on your README
XML_FILE = PROJECT_ROOT / "archive" / "WordPress.2024-08-07.xml"
OUTPUT_DIR = PROJECT_ROOT / "content" / "כותבים"

# WordPress XML namespaces
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
}

def safe_get_text(element, tag, namespaces, default=""):
    """Helper to safely extract text from an XML element."""
    found = element.find(tag, namespaces)
    return found.text if found is not None and found.text else default

def main():
    print(f"Loading XML file from: {XML_FILE}...")
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        channel = root.find('channel')
    except Exception as e:
        print(f"Error reading XML: {e}")
        return 0

    # ---------------------------------------------------------
    # PHASE 1: Extract Authors Database
    # ---------------------------------------------------------
    authors = {}
    print("Extracting authors...")
    
    for author_elem in channel.findall('wp:author', NAMESPACES):
        login = safe_get_text(author_elem, 'wp:author_login', NAMESPACES)
        if not login:
            continue
            
        authors[login] = {
            'id': safe_get_text(author_elem, 'wp:author_id', NAMESPACES),
            'login': login,
            'email': safe_get_text(author_elem, 'wp:author_email', NAMESPACES),
            'display_name': safe_get_text(author_elem, 'wp:author_display_name', NAMESPACES),
            'first_name': safe_get_text(author_elem, 'wp:author_first_name', NAMESPACES),
            'last_name': safe_get_text(author_elem, 'wp:author_last_name', NAMESPACES),
            'posts': []
        }
    
    print(f"Found {len(authors)} authors.")

    # ---------------------------------------------------------
    # PHASE 2: Extract Posts & Link to Authors
    # ---------------------------------------------------------
    print("Extracting posts and linking to authors...")
    post_count = 0
    
    for item in channel.findall('item'):
        # Only process posts and pages
        post_type = safe_get_text(item, 'wp:post_type', NAMESPACES)
        if post_type not in ['post', 'page']:
            continue
            
        creator = safe_get_text(item, 'dc:creator', NAMESPACES)
        title = item.find('title').text if item.find('title') is not None else "Untitled"
        post_id = safe_get_text(item, 'wp:post_id', NAMESPACES)
        pub_date = safe_get_text(item, 'wp:post_date', NAMESPACES)
        status = safe_get_text(item, 'wp:status', NAMESPACES)
        
        post_data = {
            'id': post_id,
            'title': title,
            'date': pub_date,
            'status': status,
            'type': post_type
        }
        
        if creator in authors:
            authors[creator]['posts'].append(post_data)
            post_count += 1
            
    print(f"Successfully mapped {post_count} posts/pages to their authors.")

    # ---------------------------------------------------------
    # PHASE 3: Generate Markdown Files for Obsidian
    # ---------------------------------------------------------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating markdown files in {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/...")

    for login, data in authors.items():
        # Clean up strings for YAML frontmatter to prevent parsing errors
        display_name = data['display_name'].replace('"', "'")

        # Sort author's posts chronologically (newest first)
        sorted_posts = sorted(data['posts'], key=lambda x: x['date'], reverse=True)

        filepath = OUTPUT_DIR / f"{login}.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write YAML Frontmatter (Quartz-compatible)
            f.write("---\n")
            f.write(f"title: \"{display_name}\"\n")
            f.write("publish: true\n")
            f.write(f"aliases:\n")
            f.write(f"  - {data['login']}\n")
            f.write(f"tags:\n")
            f.write(f"  - author\n")
            f.write("---\n\n")
            
            # Write Markdown Content
            f.write(f"# {display_name}\n\n")
            f.write("## תוכן שפורסם\n\n")
            
            if not sorted_posts:
                f.write("*No posts found for this author in the export.*\n")
            else:
                for post in sorted_posts:
                    # Formats Obsidian wikilinks using the post title
                    # e.g., - [[לא צריך דת ללמד לא תרצח (ולא מתי)]] (2016-08-06) - *publish*
                    raw_title = post.get('title') or post.get('slug') or f"post-{post.get('id', 'unknown')}"
                    clean_title = raw_title.replace('\n', ' ').strip() or f"post-{post.get('id', 'unknown')}"
                    date_short = post['date'][:10] if post['date'] else "Unknown Date"
                    status_flag = f" *(Draft)*" if post['status'] != 'publish' else ""

                    f.write(f"- [[{clean_title}]] ({date_short}){status_flag}\n")

    print("\nExtraction complete! Author directory created.")
    return len(authors)

if __name__ == "__main__":
    main()