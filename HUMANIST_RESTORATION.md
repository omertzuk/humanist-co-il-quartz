# Humanist Website Conversion Project

## Overview

This project converts the **humanist.co.il** WordPress site into a static, markdown-based archive. The source site was a Hebrew-language humanist magazine and opinion platform, and the conversion preserves the editorial structure of the original publication: posts, pages, authors, tags, categories, and media.

The archive is not just a dump of text. Each post is linked back to its author, each author has a dedicated page listing their publications, and the site keeps the original publication hierarchy by year and month. Images are copied out of the WordPress backup and stored locally so the archive remains self-contained.

---

## Project Structure

```
HumanistCoIl/
├── README.md                           # This file
├── archive_humanist_backup_files/      # Original WordPress export and backups
│   ├── WordPress.2024-08-07.xml        # Complete WordPress export (146,896 lines)
│   └── hgtransfer/
│       └── S-2500312/
│           └── BackupNow/
│               └── homedir/www/wp-content/uploads/
│                   ├── 2016/           # Images from 2016
│                   ├── 2017/           # Images from 2017
│                   ├── 2018/           # Images from 2018
│                   ├── 2019/           # Images from 2019
│                   ├── 2020/           # Images from 2020
│                   └── [year]/         # Additional years...
├── images/                             # Local copies of extracted media
│   ├── 2016/
│   ├── 2017/
│   ├── 2018/
│   ├── 2019/
│   └── 2020/
├── posts/                              # Converted blog post markdown files
│   ├── _drafts/                        # Draft posts
│   │   ├── 2016/
│   │   ├── 2017/
│   │   ├── 2018/
│   │   ├── 2022/
│   │   └── [by-id]/                    # Posts indexed by post ID
│   ├── 2016/                           # Published posts by year
│   ├── 2017/
│   ├── 2018/
│   ├── 2019/
│   ├── 2020/
│   ├── 2022/
│   └── [by-id]/                        # Posts indexed by post ID
├── pages/                              # Converted page markdown files
│   ├── _drafts/
│   ├── 2016/
│   ├── 2017/
│   ├── 2018/
│   └── [supporting pages]/
└── custom/                             # WordPress custom post types
    ├── tribe_events/                   # Event calendar entries
    ├── tribe_organizer/                # Event organizers
    ├── tribe_venue/                    # Event venues
    └── wpcf7_contact_form/             # Contact forms

```

The layout is designed so the content can be consumed either as a markdown archive or as the source for a static-site generator.

---

## Source Files

### Primary Resource: WordPress Export File

**Location:** `archive_humanist_backup_files/WordPress.2024-08-07.xml`

**File Details:**
- **Format:** WordPress eXtended RSS (WXR) v1.2
- **Size:** ~146,900 lines of XML
- **Created:** 2024-08-07 06:12:57 UTC
- **WordPress Version:** 5.3.18
- **Site URL:** https://humanist.co.il
- **Language:** Hebrew (he-IL)

**Contents:**
- Complete author database (about 100 registered users)
- All posts (blog articles, status=publish/draft/pending)
- All pages (static pages)
- All attachments (media, images)
- Comments on posts
- Categories and tags
- Post metadata (SEO, theme settings, custom fields)

### Image/Media Backup

**Location:** `archive_humanist_backup_files/hgtransfer/S-2500312/BackupNow/homedir/www/wp-content/uploads/`

**Structure:** Images organized by year:
- `2016/` — 2016 images (April-December)
- `2017/` — 2017 images (January-December)
- `2018/` — 2018 images (January-December)
- `2019/` — 2019 images (January-December)
- `2020/` — 2020 images (January-December)

**Content Types:**
- Featured images for posts
- Inline images in post/page content
- Author profile images
- Artwork and reference images (e.g., Michelangelo paintings)
- Photographs for interviews and articles

During extraction, matching files are copied from this backup tree into the local [images](images) directory, preserving a year/month structure so post content can point to local assets instead of the original WordPress URLs.

**Naming Convention:** Files typically follow WordPress upload patterns with dimensions appended (e.g., `image-300x200.jpg`, `image-1024x768.jpg`)

---

## WordPress XML Export Structure

### 1. File Organization

The XML file is structured as RSS 2.0 with WordPress-specific namespaces:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
  xmlns:excerpt="..."
  xmlns:content="..."
  xmlns:dc="..."
  xmlns:wp="..."
>
  <channel>
    <!-- Site Metadata -->
    <title>הומניסט</title>
    <link>https://humanist.co.il</link>
    <language>he-IL</language>
    
    <!-- Author Database (about 100 authors) -->
    <wp:author>...</wp:author>
    <wp:author>...</wp:author>
    ...
    
    <!-- Content Items (posts, pages, attachments) -->
    <item>...</item>
    <item>...</item>
    ...
  </channel>
</rss>
```

### 2. Author Database

**Location in XML:** Lines 39-1055 (approximately)

**Entry Count:** About 100 unique authors in the export

**Author Element Structure:**

```xml
<wp:author>
  <wp:author_id>12</wp:author_id>
  <wp:author_login><![CDATA[n75tal]]></wp:author_login>
  <wp:author_email><![CDATA[n75tal@zoho.com]]></wp:author_email>
  <wp:author_display_name><![CDATA[נועם טל]]></wp:author_display_name>
  <wp:author_first_name><![CDATA[נועם]]></wp:author_first_name>
  <wp:author_last_name><![CDATA[טל]]></wp:author_last_name>
</wp:author>
```

**Field Descriptions:**

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `wp:author_id` | Integer | 12 | Unique numeric identifier in WordPress |
| `wp:author_login` | String | `n75tal` | Username; **KEY FIELD** for post linking |
| `wp:author_email` | String | `n75tal@zoho.com` | Contact email address |
| `wp:author_display_name` | String | `נועם טל` | Full name as displayed on website |
| `wp:author_first_name` | String | `נועם` | First name component |
| `wp:author_last_name` | String | `טל` | Last name component(s) |

**Notable Authors:**
- **omertzuk** (עומר צוק) — Site editor, primary administrator
- **yogevtuval** (תובל יוגב) — Co-founder
- **shaykreitzman** (שי קרייצמן) — Editorial staff
- **n75tal** (נועם טל) — Contributor
- **mgotman** (מתי גוטמן) — Contributor
- And 65+ additional contributors

**Author ID Range:** Non-sequential; author IDs and logins are taken directly from WordPress and preserved in frontmatter.

### 3. Post Structure

**Format:** RSS `<item>` elements (one per post/page/attachment)

**Location in XML:** Lines ~1055 onwards

The post extraction script keeps only `post` and `page` records, ignores attachments and navigation items, and links each post to a valid author file through `dc:creator`.

**Complete Post Example:**

```xml
<item>
  <!-- Display Information -->
  <title>לא צריך דת ללמד לא תרצח (ולא מתי)</title>
  <link>https://humanist.co.il/circumcision-poem/</link>
  <pubDate>Sat, 06 Aug 2016 10:50:58 +0000</pubDate>
  
  <!-- Author Reference (KEY LINK) -->
  <dc:creator><![CDATA[n75tal]]></dc:creator>
  
  <!-- Identifiers -->
  <guid isPermaLink="false">http://humanist.co.il/?p=1093</guid>
  
  <!-- Content -->
  <description></description>
  <content:encoded><![CDATA[...full HTML content...]]></content:encoded>
  <excerpt:encoded><![CDATA[...excerpt text...]]></excerpt:encoded>
  
  <!-- WordPress Post Metadata -->
  <wp:post_id>1093</wp:post_id>
  <wp:post_date><![CDATA[2016-08-06 13:50:58]]></wp:post_date>
  <wp:post_date_gmt><![CDATA[2016-08-06 10:50:58]]></wp:post_date_gmt>
  <wp:comment_status><![CDATA[open]]></wp:comment_status>
  <wp:ping_status><![CDATA[open]]></wp:ping_status>
  <wp:post_name><![CDATA[circumcision-poem]]></wp:post_name>
  <wp:status><![CDATA[publish]]></wp:status>
  <wp:post_parent>0</wp:post_parent>
  <wp:menu_order>0</wp:menu_order>
  
  <!-- Content Type Classification -->
  <wp:post_type><![CDATA[post]]></wp:post_type>
  
  <!-- Categorization -->
  <category domain="post_tag" nicename="יצירה-מקורית">
    <![CDATA[יצירה מקורית]]>
  </category>
  <category domain="category" nicename="תרבות">
    <![CDATA[תרבות]]>
  </category>
  
  <!-- Custom Metadata -->
  <wp:postmeta>
    <wp:meta_key><![CDATA[_edit_last]]></wp:meta_key>
    <wp:meta_value><![CDATA[3]]></wp:meta_value>
  </wp:postmeta>
  
  <!-- Comments (if any) -->
  <wp:comment>
    <wp:comment_id>79</wp:comment_id>
    <wp:comment_author><![CDATA[NOAM]]></wp:comment_author>
    <wp:comment_author_email><![CDATA[N75TAL@ZOHO.COM]]></wp:comment_author_email>
    <wp:comment_date><![CDATA[2016-10-10 11:59:34]]></wp:comment_date>
    <wp:comment_content><![CDATA[...comment text...]]></wp:comment_content>
    <wp:comment_approved><![CDATA[0]]></wp:comment_approved>
  </wp:comment>
</item>
```

### 4. Post Field Reference

| Element | Type | Description | Example |
|---------|------|-------------|---------|
| `title` | String | Post/page title | "לא צריך דת ללמד לא תרצח" |
| `link` | URL | Permalink to the post | `https://humanist.co.il/circumcision-poem/` |
| `pubDate` | RFC 2822 DateTime | Publication date (UTC) | `Sat, 06 Aug 2016 10:50:58 +0000` |
| **`dc:creator`** | String | **Author username** (references `wp:author_login`) | `n75tal` |
| `guid` | String | Global unique identifier | `http://humanist.co.il/?p=1093` |
| `content:encoded` | HTML | Full post/page content (may contain shortcodes) | `<p>...HTML content...</p>` |
| `excerpt:encoded` | Text | Post excerpt for previews | `"קל יותר להוליך אנשים שולל..."` |
| `wp:post_id` | Integer | WordPress post ID | `1093` |
| `wp:post_date` | DateTime | Local server time | `2016-08-06 13:50:58` |
| `wp:post_date_gmt` | DateTime | UTC time | `2016-08-06 10:50:58` |
| `wp:post_type` | String | Content type: `post`, `page`, `attachment` | `post` |
| `wp:status` | String | Status: `publish`, `draft`, `pending` | `publish` |
| `wp:post_name` | String | URL slug | `circumcision-poem` |
| `wp:post_parent` | Integer | Parent post ID (0 = no parent) | `0` |
| `category` | Element | Categories and tags (repeated) | See next section |
| `wp:postmeta` | Element | Custom metadata (repeated) | Theme settings, SEO data |
| `wp:comment` | Element | Comments (repeated) | Nested comment data |

### 5. Author-to-Post Connection Mechanism

**The Critical Link:**

The `<dc:creator>` element in each post contains a **username** that must be matched against the author database:

```
Post Entry:
  <dc:creator><![CDATA[n75tal]]></dc:creator>
         ↓
         Lookup in Author Database
         ↓
Author Entry:
  <wp:author_login><![CDATA[n75tal]]></wp:author_login>
         ↓
         Match Found: Access author metadata
         ↓
  <wp:author_display_name><![CDATA[נועם טל]]></wp:author_display_name>
  <wp:author_email><![CDATA[n75tal@zoho.com]]></wp:author_email>
```

**Connection Rules:**

1. **Every post has exactly one author** via `<dc:creator>` element
2. **The creator value is always a username** (e.g., `n75tal`, `omertzuk`, `mgotman`)
3. **Usernames must exist in author database** (defined at XML start)
4. **Author metadata is lookup-based**, not embedded in post
5. **Multiple posts can share the same author**

**Example Conversions:**

| Post Creator | Author Login | Display Name | Email |
|--------------|--------------|--------------|-------|
| `n75tal` | `n75tal` | נועם טל | n75tal@zoho.com |
| `omertzuk` | `omertzuk` | עומר צוק | humanistmag@gmail.com |
| `mgotman` | `mgotman` | מתי גוטמן | mgotman@gmail.com |

### 6. Categories and Tags

Both are stored as `<category>` elements with `domain` attribute distinguishing them:

```xml
<!-- Tag (post_tag domain) -->
<category domain="post_tag" nicename="יצירה-מקורית">
  <![CDATA[יצירה מקורית]]>
</category>

<!-- Category (category domain) -->
<category domain="category" nicename="תרבות">
  <![CDATA[תרבות]]>
</category>
```

**Attributes:**
- `domain="post_tag"` — Folksonomy tag
- `domain="category"` — Hierarchical category
- `nicename` — URL-encoded slug
- Text content — Display name (Hebrew)

### 7. Post Metadata (wp:postmeta)

Stores theme-specific and plugin-specific data:

```xml
<wp:postmeta>
  <wp:meta_key><![CDATA[_edit_last]]></wp:meta_key>
  <wp:meta_value><![CDATA[3]]></wp:meta_value>
</wp:postmeta>
```

**Common Meta Keys:**
| Key | Purpose | Example Value |
|-----|---------|----------------|
| `_edit_last` | Last editor's user ID | `3` |
| `_thumbnail_id` | Featured image ID | `1188` |
| `pyre_*` | Fusion theme settings | Various |
| `_yoast_wpseo_*` | Yoast SEO data | Various |
| `sbg_selected_sidebar` | Sidebar settings | Serialized array |

### 8. Comments

Nested within `<item>` elements:

```xml
<wp:comment>
  <wp:comment_id>79</wp:comment_id>
  <wp:comment_author><![CDATA[NOAM]]></wp:comment_author>
  <wp:comment_author_email><![CDATA[N75TAL@ZOHO.COM]]></wp:comment_author_email>
  <wp:comment_author_URL></wp:comment_author_URL>
  <wp:comment_date><![CDATA[2016-10-10 11:59:34]]></wp:comment_date>
  <wp:comment_content><![CDATA[...comment text...]]></wp:comment_content>
  <wp:comment_approved><![CDATA[0]]></wp:comment_approved>
  <wp:comment_type><![CDATA[]]></wp:comment_type>
  <wp:comment_parent>0</wp:comment_parent>
</wp:comment>
```

---

## Converted Markdown Files

### Current Conversion State

The XML has already been converted to markdown files in:

- `posts/` directory — Blog posts
- `pages/` directory — Static pages
- `custom/` directory — Custom post types
- `authors/` directory — One markdown file per author, including their publication list
- `images/` directory — Local copies of media extracted from the backup tree

### Markdown Frontmatter Format

**Current structure:**

```yaml
---
title: "לא צריך דת ללמד לא תרצח (ולא מתי)"
date: 2016-08-06 13:50:58
status: publish
type: post
author: "[[n75tal]]"
categories:
  - "יצירה-מקורית"
  - "תרבות"
tags:
  - "יצירה-מקורית"
  - "שירה"
---
```

The current extraction pipeline writes author, date, status, type, categories, and tags into frontmatter, then converts the HTML body to markdown.

### Desired Enhancement

To restore full author information, markdown files should include:

```yaml
---
title: "Post Title"
date: 2016-08-06
author: "נועם טל"              # Display name
author_login: "n75tal"          # Username
author_email: "n75tal@zoho.com" # Email
categories: 
  - "יצירה-מקורית"
tags: 
  - "שירה"
---
```

---

## Data Extraction Tasks

### Task 1: Author Metadata Mapping

**Objective:** Create a JSON/YAML mapping of all authors in the export

**Source:** Lines 39-1055 of WordPress.2024-08-07.xml

**Output Format:**

```json
{
  "n75tal": {
    "id": 12,
    "login": "n75tal",
    "email": "n75tal@zoho.com",
    "display_name": "נועם טל",
    "first_name": "נועם",
    "last_name": "טל"
  },
  "omertzuk": {
    "id": 2,
    "login": "omertzuk",
    "email": "humanistmag@gmail.com",
    "display_name": "עומר צוק",
    "first_name": "עומר",
    "last_name": "צוק"
  },
  ...
}
```

### Task 2: Post-Author Linking

**Objective:** Create mapping of posts to their authors

**Source:** Each post's `<dc:creator>` and `<wp:post_id>` elements

**Output Format:**

```json
{
  "1093": {
    "post_id": 1093,
    "title": "לא צריך דת ללמד לא תרצח (ולא מתי)",
    "author_login": "n75tal",
    "author_name": "נועם טל",
    "author_email": "n75tal@zoho.com",
    "date": "2016-08-06",
    "status": "publish"
  },
  ...
}
```

### Task 3: Markdown File Augmentation

**Objective:** Add author fields and normalize the post archive

**Process:**
1. Extract post metadata from XML, including ID, date, creator, categories, and tags
2. Convert HTML content to markdown
3. Remove WordPress and Fusion Builder shortcodes
4. Normalize multi-word tags with underscores
5. Match markdown files to the corresponding XML posts
6. Write frontmatter with author and publication metadata

### Task 4: Media Processing

**Objective:** Keep images and video embeds usable in the static archive

**Process:**
1. Scan each post for image references and YouTube iframes
2. Copy matching image files from the backup tree into `images/`
3. Rewrite markdown image URLs to point to local paths
4. Convert YouTube embeds into clickable thumbnail links

---

## Technical Specifications

### Character Encoding

- **XML Encoding:** UTF-8
- **Content Language:** Hebrew (RTL)
- **Post Content:** Mixed HTML and shortcodes
- **Special Handling:** Hebrew characters preserved; no encoding errors expected

### Date/Time Information

Posts contain two timestamp formats:

1. **`<wp:post_date>`** — Local server time (Israeli timezone)
   - Format: `YYYY-MM-DD HH:MM:SS`
   - Example: `2016-08-06 13:50:58`

2. **`<wp:post_date_gmt>`** — UTC/GMT time
   - Format: `YYYY-MM-DD HH:MM:SS`
   - Example: `2016-08-06 10:50:58`

**Timezone:** UTC+3 (UTC+2 in summer) can be inferred from the offset

### Content Issues to Be Aware Of

1. **Shortcodes:** Posts may contain WordPress shortcodes (e.g., `[gallery]`, `[contact-form-7]`) that may not render in static sites

2. **HTML Markup:** Content is stored as HTML, may need conversion to Markdown

3. **Relative Links:** Some internal links may be absolute URLs to humanist.co.il

4. **Theme Styling:** Posts may reference theme-specific CSS classes

5. **Media References:** Images may be referenced with full absolute paths

---

## Conversion Workflow for Agent Setup

### Phase 1: Data Extraction
- Parse WordPress.2024-08-07.xml
- Extract about 100 author records
- Build author lookup database
- Extract post/author relationships

### Phase 2: Author Restoration
- Match each markdown file to XML post entry
- Extract author metadata
- Update frontmatter with author fields
- Validate all author references

### Phase 3: Media Processing
- Map image references in posts to the backup directory
- Copy referenced images into `images/`
- Update image paths in markdown so they point to local files
- Convert YouTube embeds into clickable thumbnail links
- Create a media-aware archive that does not depend on the live site

### Phase 4: Validation & Cleanup
- Verify all authors assigned to posts
- Check for orphaned posts (no author found)
- Validate frontmatter syntax
- Generate conversion report

---

## Next Steps

To set up an agent for this conversion:

1. **Provide the agent with:**
   - This README.md (context)
   - Path to WordPress.2024-08-07.xml
   - Path to current markdown files in `posts/` and `pages/`
   - Path to image backups

2. **Agent capabilities needed:**
   - XML parsing
   - Markdown file reading/writing
   - Path manipulation
   - Metadata extraction and matching
   - File system operations

3. **Define agent instructions to:**
   - Extract author database from XML header
   - Identify all posts and their creator usernames
   - Locate corresponding markdown files
   - Add/update author metadata in frontmatter
   - Report any unmatched posts or missing authors


## Conversion Implementation (scripts)

This repository includes two Python helper scripts that perform the practical conversion from the
`archive_humanist_backup_files/WordPress.2024-08-07.xml` export and the image backup tree into the
Quartz-compatible content layout used by this project.

- `extract_authors.py`
  - Parses the WXR export and extracts all `wp:author` records.
  - Produces one Markdown author file per WordPress user in `humanist-co-il-quartz/content/authors/`.
  - Each author file contains Quartz-compatible YAML frontmatter (`title`, `aliases`, `tags`) and a
    chronological list of the author's posts (wikilinks into the archive).

- `extract_posts.py`
  - Parses `<item>` entries from the same WXR export and processes records with `wp:post_type` of
    `post` or `page`.
  - Converts post HTML to Markdown using `markdownify` and writes Quartz frontmatter (title, date,
    `author: [[username]]`, categories, tags) into `humanist-co-il-quartz/content/posts/YYYY/MM/`.
  - Scans post HTML for `<img>` tags and attempts to copy matching files from the backup image tree
    (under `archive_humanist_backup_files/hgtransfer/.../wp-content/uploads`) into
    `humanist-co-il-quartz/content/assets/images/YYYY/MM/`, rewriting image URLs in the markdown to
    point at `/assets/images/...`.
  - Converts YouTube iframes into clickable thumbnail links before HTML→Markdown conversion.
  - Removes WordPress/Fusion shortcodes and normalizes newlines and tags.

Key configuration values used by the scripts are defined at the top of each file (for example,
`XML_FILE`, the backup image base path, and the `POSTS_DIR`/`AUTHORS_DIR` output paths). The scripts
are intentionally small and work from the repository root so paths resolve correctly.

Quick usage (run from the repository root):

```bash
python3 extract_authors.py
pip install markdownify   # if needed
python3 extract_posts.py
```

Notes and recommendations:
- The `extract_posts.py` script requires the `markdownify` package (`pip install markdownify`).
- Image copying looks for year/month folders; if a file is not found at the expected path the script
  searches recursively under the backup images base and copies the first match it finds.
- After running the scripts you should add and commit the generated `content/` files to git. Quartz
  will warn that author files are "not yet tracked by git" and dates may be inaccurate until files
  are committed; committing preserves date metadata and removes the warnings.
- The scripts are safe to re-run; they will create missing folders and will append post IDs to
  filenames when collisions occur.

---

## Resources

- **WordPress Export Format:** https://wordpress.org/support/article/tools-export-screen/
- **WXR Format Spec:** https://wordpress.org/plugins/wordpress-importer/
- **Hebrew Language Support:** RTL, no special encoding needed (UTF-8 handles it)
- **Markdown Frontmatter (YAML):** https://jekyllrb.com/docs/front-matter/

---

## Project Metadata

- **Website:** humanist.co.il
- **Language:** Hebrew (עברית)
- **Export Date:** 2024-08-07
- **WordPress Version:** 5.3.18
- **Total Authors:** About 100
- **Extracted Posts/Pages:** 235
- **Images Copied Locally:** 66
- **Estimated Pages:** Included in the 235 extracted posts/pages set
- **Date Range:** 2016-2020 (with 2022 entries)
- **Primary Categories:** Religion, Philosophy, Humanism, Culture, Current Events

---

**Created:** 2026-05-03  
**Purpose:** Static site conversion documentation  
**Status:** In progress
