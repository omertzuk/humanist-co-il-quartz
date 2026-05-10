import xml.etree.ElementTree as ET
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote

try:
    from markdownify import markdownify as md
except ImportError:
    print("Please install markdownify first: pip install markdownify")
    exit(1)

# Resolve project root (three levels up from this script)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# File paths
XML_FILE = PROJECT_ROOT / "archive" / "WordPress.2024-08-07.xml"
AUTHORS_DIR = PROJECT_ROOT / "content" / "כותבים"
POSTS_DIR = PROJECT_ROOT / "content" / "מאמרים"
IMAGES_DIR = PROJECT_ROOT / "content" / "assets" / "images"
BACKUP_IMAGES_BASE = PROJECT_ROOT / "archive" / "uploads"

# WordPress XML namespaces
NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/'
}

# Category mapping for folder structure
CATEGORY_MAPPING = {
    "הגות": "הגות",
    "חברה": "חברה",
    "דעות": "דעות",
    "תרבות": "תרבות",
    "אקטואליה": "אקטואליה",
    "יצירה מקורית": "יצירה-מקורית",
    "מדע": "מדע",
    "מהומת אלוהים": "סדרות",
    "ללא קטגוריה": "כללי"
}

CONTENT_TYPE_TERMS = {
    "לקרוא": "לקרוא",
    "לשמוע": "לשמוע",
    "לראות": "לראות",
}

def safe_get_text(element, tag, namespaces, default=""):
    """Helper to safely extract text from an XML element."""
    found = element.find(tag, namespaces)
    return found.text if found is not None and found.text else default

def sanitize_filename(filename):
    """Removes illegal characters from filenames."""
    # Keep Hebrew characters, English letters, numbers, spaces, and basic punctuation
    clean = re.sub(r'[\\/*?:"<>|]', "", filename)
    clean = clean.replace('\n', ' ').replace('\r', '').strip()
    return clean if clean else "Untitled"

def get_primary_category(categories):
    """
    Determine the primary category folder name from WordPress categories.
    Returns the mapped folder name and the original Hebrew category name.
    """
    # Use first category that is not "ללא קטגוריה"
    primary_cat_hebrew = None
    for cat in categories:
        if cat != "ללא קטגוריה":
            primary_cat_hebrew = cat
            break

    # If no valid category found, use default
    if not primary_cat_hebrew:
        return "כללי", "כללי"

    # Map to folder name
    if primary_cat_hebrew in CATEGORY_MAPPING:
        folder_name = CATEGORY_MAPPING[primary_cat_hebrew]
        return folder_name, primary_cat_hebrew
    else:
        print(f"Warning: Unknown category '{primary_cat_hebrew}', using 'כללי'")
        return "כללי", "כללי"

def normalize_tag(tag):
    """
    Normalize a tag: strip whitespace, replace spaces with hyphens,
    lowercase Latin characters, preserve Hebrew as-is.
    """
    # Strip whitespace
    tag = tag.strip()
    # Replace spaces with hyphens
    tag = tag.replace(' ', '-')
    # Lowercase only ASCII characters, preserve Hebrew
    normalized = ""
    for char in tag:
        if 'A' <= char <= 'Z':
            normalized += char.lower()
        else:
            normalized += char
    return normalized

def infer_post_type(raw_html, taxonomy_terms):
    """
    Determine whether a post is read, listened to, or watched.
    Explicit taxonomy terms win; otherwise infer from embeds and fall back to לקרוא.
    """
    for term in taxonomy_terms:
        if term in CONTENT_TYPE_TERMS:
            return CONTENT_TYPE_TERMS[term]

    if not raw_html:
        return "לקרוא"

    html = raw_html.lower()
    if any(marker in html for marker in ["youtube.com/embed", "youtu.be", "vimeo.com", "video"]):
        return "לראות"
    if any(marker in html for marker in ["soundcloud", "audio", "podcast", "spotify.com"]):
        return "לשמוע"

    return "לקרוא"

def extract_youtube_embeds(html_content):
    """
    Extract YouTube iframes and convert to markdown-compatible format.
    Returns modified HTML with iframes replaced by markdown links.
    """
    if not html_content:
        return html_content
    
    # Pattern to find YouTube iframe embeds
    iframe_pattern = r'<iframe[^>]*src=["\']?https://www\.youtube\.com/embed/([a-zA-Z0-9_-]+)[^>]*></iframe>'
    
    def replace_youtube_iframe(match):
        video_id = match.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        # Return HTML that will convert to markdown properly
        return f'<a href="{youtube_url}"><img src="{thumbnail_url}" alt="YouTube Video" style="max-width:100%;"/></a>'
    
    return re.sub(iframe_pattern, replace_youtube_iframe, html_content, flags=re.IGNORECASE)

def extract_images_from_html(html_content):
    """
    Extract image URLs from HTML content.
    Returns list of image URLs found in img src attributes.
    """
    if not html_content:
        return []
    
    # Find all img tags and extract src attributes
    img_pattern = r'<img[^>]+src=["\']?([^"\'>\s]+)["\']?[^>]*>'
    matches = re.findall(img_pattern, html_content, re.IGNORECASE)
    return matches

def copy_image_from_backup(image_url, year, month):
    """
    Locate image in backup directory and copy to local images folder.
    Returns the local relative path if successful, None otherwise.
    """
    if not image_url:
        return None

    # Parse the image URL to extract filename
    # URL might be: https://humanist.co.il/wp-content/uploads/2016/04/image.jpg
    # or: /wp-content/uploads/2016/04/image.jpg

    try:
        parsed = urlparse(image_url)
        path_part = unquote(parsed.path)  # Decode URL-encoded characters

        # Extract the part after 'uploads/'
        if 'uploads/' in path_part:
            filename = path_part.split('uploads/')[-1]
        elif 'uploads/' in image_url:
            filename = image_url.split('uploads/')[-1]
        else:
            return None

        # Try to find file in backup directory with year/month structure
        # First try the year/month from post date
        backup_path = BACKUP_IMAGES_BASE / year / month / filename

        if backup_path.exists():
            # Create local image folder structure
            local_image_folder = IMAGES_DIR / year / month
            local_image_folder.mkdir(parents=True, exist_ok=True)

            # Copy file to local directory
            local_image_path = local_image_folder / Path(filename).name
            shutil.copy2(backup_path, local_image_path)

            # Return absolute path for markdown (Quartz uses /assets/ as root)
            return f"/assets/images/{year}/{month}/{Path(filename).name}"

        # If not found in year/month, try searching broader backup structure
        # Look for the filename in all year directories
        if BACKUP_IMAGES_BASE.exists():
            for year_dir in BACKUP_IMAGES_BASE.iterdir():
                if not year_dir.is_dir():
                    continue

                # Search recursively in the year directory
                for root, dirs, files in os.walk(year_dir):
                    if Path(filename).name in files:
                        backup_path = Path(root) / Path(filename).name

                        # Create local image folder structure
                        local_image_folder = IMAGES_DIR / year / month
                        local_image_folder.mkdir(parents=True, exist_ok=True)

                        # Copy file to local directory
                        local_image_path = local_image_folder / Path(filename).name
                        shutil.copy2(backup_path, local_image_path)

                        return f"/assets/images/{year}/{month}/{Path(filename).name}"

    except Exception as e:
        print(f"Error processing image {image_url}: {e}")

    return None

def rewrite_image_urls_in_markdown(markdown_content, image_mapping):
    """
    Replace image URLs in markdown with local paths.
    image_mapping: dict of {original_url: local_path}
    """
    if not markdown_content or not image_mapping:
        return markdown_content
    
    for original_url, local_path in image_mapping.items():
        # Escape the original URL for regex
        escaped_url = re.escape(original_url)
        # Replace in markdown ![alt](url) format
        markdown_content = re.sub(
            f'(!\\[([^\\]]*?)\\]\\(){escaped_url}(\\))',
            f'![\\2]({local_path})',
            markdown_content
        )
    
    return markdown_content

def main():
    print(f"Loading XML file from: {XML_FILE}...")
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        channel = root.find('channel')
    except Exception as e:
        print(f"Error reading XML: {e}")
        return 0

    # 1. Get a list of valid authors from our existing folder
    print("Scanning authors directory...")
    valid_authors = []
    if AUTHORS_DIR.exists():
        for filepath in AUTHORS_DIR.glob('*.md'):
            valid_authors.append(filepath.stem)

    if not valid_authors:
        print(f"No author files found in {AUTHORS_DIR.relative_to(PROJECT_ROOT)}/. Did you run the author script first?")
        return 0

    # 2. Extract and process posts
    print("Extracting posts...")
    post_count = 0
    
    for item in channel.findall('item'):
        post_type = safe_get_text(item, 'wp:post_type', NAMESPACES)
        
        # We only want posts and pages, not attachments or nav menus
        if post_type not in ['post', 'page']:
            continue
            
        creator = safe_get_text(item, 'dc:creator', NAMESPACES)
        
        # Only process if we have an author file for them
        if creator not in valid_authors:
            continue

        # Extract basic metadata
        title_elem = item.find('title')
        title = (title_elem.text if title_elem is not None and title_elem.text else None) or "Untitled"
        post_id = safe_get_text(item, 'wp:post_id', NAMESPACES)
        pub_date = safe_get_text(item, 'wp:post_date', NAMESPACES)
        status = safe_get_text(item, 'wp:status', NAMESPACES)
        
        # Parse Date for Folder Structure (YYYY/MM) - MUST BE BEFORE IMAGE PROCESSING
        year, month = "Unknown_Year", "Unknown_Month"
        if pub_date and len(pub_date) >= 10 and not pub_date.startswith("0000"):
            year = pub_date[0:4]
            month = pub_date[5:7]
        
        # Extract content and convert to markdown
        raw_html = safe_get_text(item, 'content:encoded', NAMESPACES)
        
        # Process YouTube embeds BEFORE markdownify to convert iframes to clickable thumbnails
        if raw_html:
            raw_html = extract_youtube_embeds(raw_html)
        
        # Extract images from raw HTML
        image_urls = extract_images_from_html(raw_html) if raw_html else []
        image_mapping = {}
        
        # Copy images from backup and create mapping
        for image_url in image_urls:
            local_path = copy_image_from_backup(image_url, year, month)
            if local_path:
                image_mapping[image_url] = local_path
        
        # Convert HTML to markdown
        markdown_content = md(raw_html, heading_style="ATX") if raw_html else ""
        
        # Rewrite image URLs in markdown to point to local copies
        markdown_content = rewrite_image_urls_in_markdown(markdown_content, image_mapping)
        
        # Remove WordPress/Fusion Builder shortcodes
        # Matches patterns like [fullwidth ...], [fusion_text], [/fullwidth], etc.
        markdown_content = re.sub(r'\[/?[a-zA-Z_-]+[^\]]*\]', '', markdown_content)
        # Clean up multiple consecutive newlines that result from shortcode removal
        markdown_content = re.sub(r'\n\n+', '\n\n', markdown_content)
        markdown_content = markdown_content.strip()

        # Extract categories, tags, and content type
        categories = []
        tags = []
        content_type_candidates = []
        for cat in item.findall('category'):
            domain = cat.get('domain')
            cat_text = cat.text
            if not cat_text:
                continue
            if domain == 'category':
                if cat_text in CONTENT_TYPE_TERMS:
                    content_type_candidates.append(cat_text)
                else:
                    categories.append(cat_text)
            elif domain == 'post_tag':
                # Normalize tags
                tag_normalized = normalize_tag(cat_text)
                tags.append(tag_normalized)

        content_type = infer_post_type(raw_html, content_type_candidates)

        # Determine primary category for folder structure
        primary_category_folder, primary_category_hebrew = get_primary_category(categories)

        # Put any secondary topical categories into tags for discoverability
        secondary_categories = [cat for cat in categories if cat != primary_category_hebrew]
        for cat in secondary_categories:
            tags.append(normalize_tag(cat))

        # 3. Create Folder Structure
        folder_path = POSTS_DIR / primary_category_folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # 4. Generate File Path and Handle Collisions
        safe_title = sanitize_filename(title)
        filepath = folder_path / f"{safe_title}.md"

        # If a file with this name already exists, append the post ID to make it unique
        if filepath.exists():
            filepath = folder_path / f"{safe_title} - {post_id}.md"

        # 5. Write the Markdown File
        with open(filepath, 'w', encoding='utf-8') as f:
            # YAML Frontmatter (Quartz-compatible)
            f.write("---\n")
            # Replace quotes in title to prevent YAML parsing errors
            yaml_title = title.replace('"', "'").replace('\n', ' ').strip()
            f.write(f"title: \"{yaml_title}\"\n")
            f.write("publish: true\n")
            f.write(f"date: {pub_date}\n")

            # Author reference - use wikilink so Quartz can resolve to author page
            f.write(f"author: [[{creator}]]\n")

            # Primary category
            f.write(f"category: {primary_category_hebrew}\n")

            # Content type (reading / listening / watching)
            f.write(f"type: {content_type}\n")

            # Year as integer
            if year and year != "Unknown_Year":
                f.write(f"year: {year}\n")

            # Tags (normalized)
            if tags:
                f.write("tags:\n")
                for t in sorted(set(tags)):
                    f.write(f"  - {t}\n")

            f.write("---\n\n")
            
            # Post Content
            f.write(f"# {title}\n\n")
            f.write(markdown_content)
            
        post_count += 1

    print(f"\nSuccess! Extracted {post_count} posts into '{POSTS_DIR.relative_to(PROJECT_ROOT)}' directory.")
    return post_count

if __name__ == "__main__":
    main()