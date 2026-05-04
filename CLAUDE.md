# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Quartz v4 site configured in Hebrew (locale: he-IL) for publishing a digital garden. Quartz is a static site generator that transforms Markdown content into a fully-featured website with features like backlinks, graph views, full-text search, and SPA routing.

## Development Commands

### Building and Serving
- `npx quartz build` - Build the site into static HTML files
- `npx quartz build --serve` - Build and serve locally with hot-reload (default port 8080)
- `npx quartz build --serve -d docs` - Serve the docs folder specifically
- `npm run docs` - Shortcut for building and serving the docs folder

### Code Quality
- `npm run check` - Run TypeScript type checking and Prettier formatting check
- `npm run format` - Auto-format all files with Prettier
- `npm test` - Run tests using tsx test runner

### Other Commands
- `npx quartz create` - Initialize Quartz
- `npx quartz update` - Get the latest Quartz updates
- `npx quartz sync` - Sync to/from GitHub
- `npx quartz restore` - Restore content folder from cache

## Build System Architecture

### Three-Phase Build Pipeline

Quartz uses a plugin-based architecture with three distinct phases:

1. **Transformers** (`quartz/plugins/transformers/`) - Process Markdown content
   - Text transformations (e.g., frontmatter extraction)
   - Markdown plugins (remark) for mdast manipulation
   - HTML plugins (rehype) for hast manipulation
   - Pipeline: raw text → mdast (Markdown AST) → hast (HTML AST)

2. **Filters** (`quartz/plugins/filters/`) - Determine which content to publish
   - Implement `shouldPublish(ctx, content): boolean`
   - Example: RemoveDrafts filters out draft content

3. **Emitters** (`quartz/plugins/emitters/`) - Generate output files
   - Emit HTML pages, assets, RSS feeds, sitemaps, etc.
   - Can implement `partialEmit` for incremental builds during watch mode
   - HTML emitters convert hast → JSX → static HTML using Preact

### Key Build Files

- `quartz/bootstrap-cli.mjs` - Entry point, handles CLI args and transpilation with esbuild
- `quartz/build.ts` - Main build orchestrator
- `quartz/processors/parse.ts` - Markdown parsing with worker thread support (>128 files)
- `quartz/processors/filter.ts` - Content filtering
- `quartz/processors/emit.ts` - File emission

### Component System

Components are Preact-based and defined in `quartz/components/`. Each component:
- Receives `QuartzComponentProps` (ctx, fileData, cfg, tree, etc.)
- Can define `css`, `beforeDOMLoaded`, and `afterDOMLoaded` static properties
- Scripts ending in `.inline.ts` are bundled separately for browser execution

Page layouts are configured in `quartz.layout.ts`:
- `sharedPageComponents` - Shared across all pages (head, header, footer, afterBody)
- `defaultContentPageLayout` - Single note pages (beforeBody, left, right sidebars)
- `defaultListPageLayout` - List pages like tags/folders

## Configuration Files

### quartz.config.ts
Main configuration with three sections:
- `configuration` - Global settings (pageTitle, locale, theme, analytics, ignorePatterns, etc.)
- `plugins.transformers` - Content processing plugins
- `plugins.filters` - Publishing filters
- `plugins.emitters` - Output generators

### quartz.layout.ts
Defines page layouts using components. Structure:
- `head`, `header`, `footer`, `afterBody` - Shared layout elements
- `beforeBody` - Content before the main body
- `left`, `right` - Sidebar components
- `pageBody` - Main content area

## Content Structure

- Content lives in the `content/` folder (configurable via CLI `--directory`)
- Markdown files with frontmatter support
- Assets in `content/assets/`
- Authors in `content/authors/`
- Posts in `content/posts/`

## Site-Specific Configuration

This site is configured with:
- Hebrew locale (he-IL)
- Alef font for header and body
- JetBrains Mono for code
- Local font loading
- Plausible analytics
- Dark mode support
- SPA routing enabled
- Custom OG images (can be commented out to speed up builds)

## TypeScript Configuration

- Module system: `nodenext`
- Target: `esnext`
- JSX: `react-jsx` with Preact runtime
- Strict mode enabled
- All `.ts`, `.tsx` files included except `build/**/*.d.ts`

## Development Notes

### Hot Reload System
When using `--serve`:
- WebSocket server on port 3001 for hot-reload signals
- HTTP server on user-defined port (default 8080) for serving files
- File watchers for both source code (`.ts`, `.tsx`, `.scss`) and content (`.md`)
- Incremental builds using content map for fast rebuilds

### Plugin Development
When creating plugins:
- Transformers export a function returning `QuartzTransformerPluginInstance`
- Filters export a function returning `QuartzFilterPluginInstance`
- Emitters export a function returning `QuartzEmitterPluginInstance`
- See `quartz/plugins/types.ts` for interfaces

### Path Handling
- Quartz has complex path logic - see `quartz/util/path.ts`
- Files are slugified for URLs
- All paths use `FilePath` type for type safety

### Testing
- Test files: `**/*.test.ts`
- Run with `npm test` (uses tsx test runner)
- Existing tests: search functionality, path utilities, file trie

## Common Patterns

### Adding a Transformer Plugin
1. Create file in `quartz/plugins/transformers/`
2. Export a function that returns `QuartzTransformerPluginInstance`
3. Implement `name` and optionally `textTransform`, `markdownPlugins`, or `htmlPlugins`
4. Add to `quartz.config.ts` plugins.transformers array

### Adding a Component
1. Create `.tsx` file in `quartz/components/`
2. Define Preact component with `QuartzComponentProps`
3. Add optional `css`, `beforeDOMLoaded`, `afterDOMLoaded` static properties
4. Export from `quartz/components/index.ts`
5. Add to layout in `quartz.layout.ts`

### Styling
- SCSS files in `quartz/styles/`
- Custom styles in `quartz/styles/custom.scss`
- Component-specific styles via component `css` property
- Lightning CSS handles minification and vendor prefixes
