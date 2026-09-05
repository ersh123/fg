import { afterEach, describe, expect, it, vi } from 'vitest'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { DaemonClient } from './client'
import { DaemonServer } from './daemon-server'
import type { TerminalSpawnAdmission } from './linux-terminal-spawn-admission'
import type { SubprocessHandle } from './session-subprocess-handle'

function createMockSubprocess(): SubprocessHandle {
  let onExit: ((code: number) => void) | undefined
  return {
    pid: 71001,
    getForegroundProcess: vi.fn(() => null),
    write: vi.fn(),
    resize: vi.fn(),
    kill: vi.fn(() => onExit?.(0)),
    terminateOwnedTree: () => 'unavailable' as const,
    forceKill: vi.fn(() => onExit?.(137)),
    signal: vi.fn(),
    onData: vi.fn(),
    onExit: vi.fn((callback) => {
      onExit = callback
    }),
    dispose: vi.fn()
  }
}

type Started = {
  directory: string
  server: DaemonServer
  client: DaemonClient
}

async function startServer(options: {
  terminalSpawnAdmission: TerminalSpawnAdmission
  spawnSubprocess: () => SubprocessHandle
}): Promise<Started> {
  const directory = mkdtempSync(join(tmpdir(), 'orca-linux-admission-'))
  const socketPath = join(directory, 'daemon.sock')
  const tokenPath = join(directory, 'daemon.token')
  const server = new DaemonServer({
    socketPath,
    tokenPath,
    terminalSpawnAdmission: options.terminalSpawnAdmission,
    spawnSubprocess: options.spawnSubprocess
  })
  await server.start()
  const client = new DaemonClient({ socketPath, tokenPath })
  await client.ensureConnected()
  return { directory, server, client }
}

describe('DaemonServer Linux terminal admission integration', () => {
  const started: Started[] = []

  afterEach(async () => {
    for (const fixture of started.splice(0)) {
      fixture.client.disconnect()
      await fixture.server.shutdown()
      rmSync(fixture.directory, { recursive: true, force: true })
    }
  })

  it('refuses a denied reservation before invoking the PTY spawner', async () => {
    const spawnSubprocess = vi.fn(() => createMockSubprocess())
    const terminalSpawnAdmission: TerminalSpawnAdmission = {
      acquire: vi.fn(async () => {
        throw new Error('linux_memory_reserve')
      })
    }
    const fixture = await startServer({ terminalSpawnAdmission, spawnSubprocess })
    started.push(fixture)

    await expect(
      fixture.client.request('createOrAttach', {
        sessionId: 'denied-agent',
        cols: 80,
        rows: 24,
        command: 'codex'
      })
    ).rejects.toThrow('linux_memory_reserve')

    expect(spawnSubprocess).not.toHaveBeenCalled()
  })

  it('classifies an agent command and treats a later request as an attach', async () => {
    const release = vi.fn()
    const acquire = vi.fn(async () => release)
    const fixture = await startServer({
      terminalSpawnAdmission: { acquire },
      spawnSubprocess: () => createMockSubprocess()
    })
    started.push(fixture)

    await fixture.client.request('createOrAttach', {
      sessionId: 'classified-agent',
      cols: 80,
      rows: 24,
      command: 'codex'
    })
    await fixture.client.request('createOrAttach', {
      sessionId: 'classified-agent',
      cols: 120,
      rows: 40,
      command: 'codex'
    })

    expect(acquire).toHaveBeenNthCalledWith(1, {
      createsNewSession: true,
      isAgent: true
    })
    expect(acquire).toHaveBeenNthCalledWith(2, {
      createsNewSession: false,
      isAgent: true
    })
    expect(release).toHaveBeenCalledTimes(2)
  })

  it('releases a reservation when subprocess creation fails', async () => {
    const release = vi.fn()
    const fixture = await startServer({
      terminalSpawnAdmission: { acquire: vi.fn(async () => release) },
      spawnSubprocess: () => {
        throw new Error('spawn failed')
      }
    })
    started.push(fixture)

    await expect(
      fixture.client.request('createOrAttach', {
        sessionId: 'failed-spawn',
        cols: 80,
        rows: 24
      })
    ).rejects.toThrow('spawn failed')

    expect(release).toHaveBeenCalledOnce()
  })
})
