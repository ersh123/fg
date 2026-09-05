import assert from 'node:assert/strict'
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import { afterEach, describe, it } from 'node:test'

const repoRoot = resolve(import.meta.dirname, '../..')
const launcher = join(repoRoot, 'resources/linux/bin/orca-hardened-desktop')
const builderConfig = join(repoRoot, 'config/electron-builder.config.cjs')
const afterInstall = join(repoRoot, 'resources/linux/packaging/after-install.sh')
const afterRemove = join(repoRoot, 'resources/linux/packaging/after-remove.sh')
const tempDirs = []

function tempDir() {
  const directory = mkdtempSync(join(tmpdir(), 'orca-hardened-launcher-'))
  tempDirs.push(directory)
  return directory
}

function executable(path, content) {
  writeFileSync(path, content)
  chmodSync(path, 0o755)
}

function runLauncher({ systemd = true, overrides = {}, args = ['--inspect', 'two words'] } = {}) {
  const directory = tempDir()
  const bin = join(directory, 'bin')
  const app = join(directory, 'orca-ide')
  const meminfo = join(directory, 'meminfo')
  const systemdArgs = join(directory, 'systemd-args')
  const appArgs = join(directory, 'app-args')
  spawnSync('mkdir', ['-p', bin], { stdio: 'inherit' })
  writeFileSync(
    meminfo,
    ['MemTotal:       16777216 kB', 'MemAvailable:   12582912 kB', ''].join('\n')
  )
  executable(app, `#!/bin/sh\nprintf '%s\\n' "$@" > ${JSON.stringify(appArgs)}\n`)
  executable(
    join(bin, 'systemctl'),
    systemd ? '#!/bin/sh\nexit 0\n' : '#!/bin/sh\nexit 1\n'
  )
  executable(
    join(bin, 'systemd-run'),
    `#!/bin/sh
printf '%s\\n' "$@" >> ${JSON.stringify(systemdArgs)}
while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do shift; done
[ "$#" -gt 0 ] && shift
if [ "\${1-}" = "true" ]; then exit 0; fi
exec "$@"
`
  )

  const result = spawnSync(launcher, args, {
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: `${bin}:${process.env.PATH}`,
      ORCA_HARDENED_APP_EXECUTABLE: app,
      ORCA_HARDENED_MEMINFO_PATH: meminfo,
      ...overrides
    }
  })
  return {
    ...result,
    appArgs: readFileSync(appArgs, 'utf8').trim().split('\n'),
    systemdArgs: systemd && readFileSync(systemdArgs, 'utf8')
  }
}

afterEach(() => {
  for (const directory of tempDirs.splice(0)) {
    rmSync(directory, { recursive: true, force: true })
  }
})

describe('Linux hardened desktop launcher', () => {
  it('launches Orca in a user systemd scope with memory and task boundaries', () => {
    const result = runLauncher()

    assert.equal(result.status, 0, result.stderr)
    assert.deepEqual(result.appArgs, ['--inspect', 'two words'])
    assert.match(result.systemdArgs, /MemoryAccounting=yes/)
    assert.match(result.systemdArgs, /MemoryHigh=/)
    assert.match(result.systemdArgs, /MemoryMax=/)
    assert.match(result.systemdArgs, /MemorySwapMax=/)
    assert.match(result.systemdArgs, /TasksMax=1024/)
  })

  it('honors explicit MiB and task-limit overrides', () => {
    const result = runLauncher({
      overrides: {
        ORCA_HARDENED_MEMORY_HIGH_MB: '4096',
        ORCA_HARDENED_MEMORY_MAX_MB: '6144',
        ORCA_HARDENED_SWAP_MAX_MB: '512',
        ORCA_HARDENED_TASKS_MAX: '333'
      }
    })

    assert.equal(result.status, 0, result.stderr)
    assert.match(result.systemdArgs, /MemoryHigh=4294967296/)
    assert.match(result.systemdArgs, /MemoryMax=6442450944/)
    assert.match(result.systemdArgs, /MemorySwapMax=536870912/)
    assert.match(result.systemdArgs, /TasksMax=333/)
  })

  it('falls back to one direct launch when the user systemd manager is unavailable', () => {
    const result = runLauncher({ systemd: false })

    assert.equal(result.status, 0, result.stderr)
    assert.deepEqual(result.appArgs, ['--inspect', 'two words'])
  })

  it('packages the wrapper and makes it the desktop-entry command', () => {
    const config = readFileSync(builderConfig, 'utf8')
    assert.match(config, /orca-hardened-desktop %U/)
    assert.match(config, /resources\/linux\/bin\/orca-hardened-desktop/)
  })

  it('registers and removes only the owned desktop launcher symlink', () => {
    assert.match(readFileSync(afterInstall, 'utf8'), /orca-hardened-desktop/)
    assert.match(readFileSync(afterRemove, 'utf8'), /orca-hardened-desktop/)
  })
})
