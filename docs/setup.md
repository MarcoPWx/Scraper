---
title: Setup – VitePress Dev/Build
---

# Setup – VitePress

You already have the docs/ structure. To run it locally:

## One-shot (no package.json required)
```bash
# Generate prebuilt recent updates (uses local Git). Optional but recommended.
node docs/.vitepress/scripts/generate-recent.js

# Dev server (hot reload)
npx vitepress dev docs

# Build static site (to docs/.vitepress/dist)
node docs/.vitepress/scripts/generate-recent.js && npx vitepress build docs

# Preview build
npx vitepress preview docs
```

## Optional: Add scripts via package.json
```bash
npm init -y
npm i -D vitepress@latest

# package.json scripts
# {
#   "scripts": {
#     "docs:prebuild": "node docs/.vitepress/scripts/generate-recent.js",
#     "docs:dev": "npm run docs:prebuild && vitepress dev docs",
#     "docs:build": "npm run docs:prebuild && vitepress build docs",
#     "docs:preview": "vitepress preview docs"
#   }
# }
```

Notes
- Last Updated uses Git history (lastUpdated: true). Ensure this repo is under Git and files are committed.
- Mermaid is enabled in config (markdown.mermaid: true).
- Press `/` anywhere to focus the search input.
- Recently updated on the home page prefers prebuilt data (docs/public/recent.json) and falls back to GitHub commits if missing.

