#!/usr/bin/env node
/**
 * Generate docs/public/recent.json from local Git history.
 * Lists the most recently updated docs pages with title, route, and timestamp.
 */
const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const repoRoot = path.resolve(__dirname, '..', '..', '..')
const docsDir = path.resolve(__dirname, '..', '..')
const outDir = path.resolve(docsDir, 'public')
const outFile = path.join(outDir, 'recent.json')

function run(cmd) {
  return execSync(cmd, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'ignore'] }).toString('utf8')
}

function toRoute(file) {
  // file is like docs/lessons/00-intro.md
  const rel = path.relative(docsDir, path.resolve(repoRoot, file)).replace(/\\/g, '/')
  if (!rel.endsWith('.md')) return null
  if (rel.endsWith('index.md')) {
    return '/' + rel.replace(/index\.md$/, '')
  }
  return '/' + rel.replace(/\.md$/, '')
}

function readTitle(absPath) {
  try {
    const txt = fs.readFileSync(absPath, 'utf8')
    // try frontmatter title:
    const m1 = txt.match(/^---[\s\S]*?^title:\s*(.+?)\s*$/m)
    if (m1) return m1[1].trim()
    // try first markdown H1
    const m2 = txt.match(/^#\s+(.+)$/m)
    if (m2) return m2[1].trim()
  } catch {}
  return null
}

function main() {
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true })
  // Get last 100 commits that touched docs/** (excluding merges)
  const log = run(
    'git --no-pager log --no-merges --pretty=format:%ct\t%H\t%s --name-only -- docs'
  )
  const lines = log.split(/\r?\n/)
  const latest = new Map() // file -> { ts, sha, msg }
  let current = null
  for (const line of lines) {
    if (!line.trim()) continue
    if (/^\d+\t[0-9a-f]+\t/.test(line)) {
      const [ts, sha, ...msgParts] = line.split('\t')
      current = { ts: Number(ts) * 1000, sha, msg: msgParts.join('\t') }
    } else if (current) {
      const file = line.trim()
      if (!file.startsWith('docs/')) continue
      if (!file.endsWith('.md')) continue
      // record only the most recent commit for a file
      if (!latest.has(file)) {
        latest.set(file, current)
      }
    }
  }
  const items = Array.from(latest.entries())
    .map(([file, { ts }]) => ({ file, ts }))
    .sort((a, b) => b.ts - a.ts)
    .slice(0, 15)
    .map(({ file, ts }) => {
      const route = toRoute(file)
      const abs = path.resolve(repoRoot, file)
      const title = readTitle(abs) || route || file
      return { route, title, updated_at: new Date(ts).toISOString() }
    })
    .filter(i => !!i.route)

  fs.writeFileSync(outFile, JSON.stringify({ generated_at: new Date().toISOString(), items }, null, 2))
  console.log(`[recent] wrote ${outFile} with ${items.length} items`)
}

main()

