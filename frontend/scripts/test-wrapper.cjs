#!/usr/bin/env node
// Wrapper to run Vitest while stripping unsupported Jest-style flags
const { spawnSync } = require('child_process')

// Known incompatible flags that sometimes appear in CI
const incompatible = new Set(['--runInBand', '--silent'])
const args = process.argv.slice(2).filter((a) => !incompatible.has(a))

// Use npx to ensure the local vitest is invoked
const cmdArgs = ['vitest', 'run', ...args]

const res = spawnSync('npx', cmdArgs, { stdio: 'inherit' })
process.exit(res.status || 0)
