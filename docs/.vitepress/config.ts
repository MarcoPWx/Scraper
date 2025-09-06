import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Scraper',
  description: 'Local Knowledge Harvester & Compliance Packager',
  lang: 'en-US',
  lastUpdated: true,
  cleanUrls: true,
  head: [
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1' }],
    ['meta', { property: 'og:title', content: 'Scraper – Local Knowledge Harvester' }],
    ['meta', { property: 'og:description', content: 'Privacy-first harvesting and packaging with explainable heuristics and idempotent adapters.' }]
  ],
  markdown: {
    lineNumbers: true,
    mermaid: true
  },
  themeConfig: {
    search: { provider: 'local' },
    nav: [
      { text: 'Handbook', link: '/handbook/start-here' },
      { text: 'Meeting Mode', link: '/meeting-mode' },
      { text: 'Lookup', link: '/hub/MEETING_MODE' },
      { text: 'Quick Lookup', link: '/lookup/' },
      { text: 'Syllabus', link: '/syllabus' },
      { text: 'Expert', link: '/expert/checklist' },
      { text: 'All Lessons', link: '/all-lessons' },
      { text: 'Glossary', link: '/glossary' },
      { text: 'Architecture', link: '/architecture/GALLERY' },
      { text: 'Cheatsheets', link: '/cheatsheets/' },
      { text: 'Runbooks', link: '/ops/runbooks/' },
      { text: 'Logs', link: '/learning/logs/' },
      { text: 'Roadmap', link: '/roadmap/overview' },
      { text: 'Devlog', link: '/devlog' },
      { text: 'Status', link: '/SYSTEM_STATUS' }
    ],
    sidebar: {
      '/handbook/': [
        { text: 'Start Here', link: '/handbook/start-here' }
      ],
      '/lessons/': [
        {
          text: 'Masterclass 00–12',
          items: [
            { text: '00 · Start Here', link: '/lessons/00-intro' },
            { text: '01 · Harvesters', link: '/lessons/01-harvesters' },
            { text: '02 · TF‑IDF & Uniqueness', link: '/lessons/02-tfidf-uniqueness' },
            { text: '03 · Exporters & Manifests', link: '/lessons/03-export-manifest' },
            { text: '04 · Importers', link: '/lessons/04-importers' },
            { text: '05 · SimHash Dedupe', link: '/lessons/05-simhash' },
            { text: '06 · Difficulty & Confidence', link: '/lessons/06-difficulty-confidence' },
            { text: '07 · Strict Gates', link: '/lessons/07-strict-gates' },
            { text: '08 · HTML Reports', link: '/lessons/08-html-reports' },
            { text: '09 · Learning Center', link: '/lessons/09-learning-center' },
            { text: '10 · Tauri UI', link: '/lessons/10-tauri-ui' },
            { text: '11 · Packaging & CI', link: '/lessons/11-packaging-ci' },
            { text: '12 · Extensibility', link: '/lessons/12-extensibility' },
            { text: 'Template (Mini-lab)', link: '/lessons/TEMPLATE_MINILAB' }
          ]
        }
      ],
      '/cheatsheets/': [
        { text: 'Cheatsheets', items: [
          { text: 'Index', link: '/cheatsheets/' },
          { text: 'Prompts', link: '/cheatsheets/prompts' },
          { text: 'RAG', link: '/cheatsheets/rag' },
          { text: 'Contracts', link: '/cheatsheets/contracts' },
          { text: 'Observability', link: '/cheatsheets/observability' },
          { text: 'Guardrails', link: '/cheatsheets/guardrails' },
          { text: 'Gateway & SSE', link: '/cheatsheets/gateway_sse' },
          { text: 'Thresholds & knobs', link: '/cheatsheets/thresholds' },
          { text: 'CLI commands', link: '/cheatsheets/cli' },
          { text: 'ASR', link: '/cheatsheets/asr' },
          { text: 'TTS & SSML', link: '/cheatsheets/tts_ssml' }
        ]}
      ],
      '/architecture/': [
        { text: 'Architecture', items: [
          { text: 'Gallery', link: '/architecture/GALLERY' }
        ]}
      ],
      '/concepts/': [
        { text: 'Concepts & Heuristics', items: [
          { text: 'Overview', link: '/concepts/' },
          { text: 'Distractors', link: '/concepts/distractors' },
          { text: 'Uniqueness & dedup', link: '/concepts/uniqueness' },
          { text: 'Answer balance', link: '/concepts/answer-balance' },
          { text: 'Scoring', link: '/concepts/scoring' },
          { text: 'Learn the ideas', link: '/concepts/learn' }
        ]}
      ],
      '/hub/': [
        { text: 'Meeting Mode', items: [
          { text: 'Meeting Mode', link: '/hub/MEETING_MODE' }
        ]}
      ],
      '/journeys/': [
        { text: 'Journeys', items: [
          { text: 'Overview', link: '/journeys/' },
          { text: 'User Stories', link: '/journeys/user-stories' },
          { text: 'S2S', link: '/journeys/s2s' }
        ]}
      ],
      '/specs/': [
        { text: 'Specs', items: [
          { text: 'Specs Index', link: '/specs/' },
          { text: 'Persistence (SQLite)', link: '/specs/persistence' },
          { text: 'Known gaps & wins', link: '/specs/gaps' }
        ]}
      ],
      '/ops/': [
        { text: 'Runbooks', items: [
          { text: 'Ship (Local)', link: '/ops/runbooks/ship-local' }
        ]}
      ],
      '/learning/': [
        { text: 'Learning Logs', items: [
          { text: 'Logs Index', link: '/learning/logs/' }
        ]}
      ],
      '/expert/': [
        { text: 'Expert', items: [
          { text: 'Expert Checklist', link: '/expert/checklist' },
          { text: 'Mastery Dashboard', link: '/expert/dashboard' }
        ]}
      ],
      '/interview/': [
        { text: 'Interview', items: [
          { text: 'Quick Cards', link: '/quick-cards' }
        ]}
      ],
      '/roadmap/': [
        { text: 'Roadmap', items: [
          { text: 'Overview', link: '/roadmap/overview' },
          { text: 'Epics & Tasks', link: '/roadmap/issues' },
          { text: 'Board', link: '/roadmap/board' }
        ]}
      ],
      '/': [
        { text: 'Overview', items: [
          { text: 'Home', link: '/' },
          { text: 'Syllabus', link: '/syllabus' },
          { text: 'All Lessons', link: '/all-lessons' },
          { text: 'Glossary', link: '/glossary' }
        ]}
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/MarcoPWx/Scraper' }
    ],
    editLink: {
      pattern: 'https://github.com/MarcoPWx/Scraper/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },
    lastUpdated: {
      text: 'Last updated',
      formatOptions: { dateStyle: 'short', timeStyle: 'short' }
    }
  }
})

