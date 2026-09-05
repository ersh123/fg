import { describe, expect, it, vi } from 'vitest'
import {
  LinuxTerminalSpawnAdmission,
  type LinuxTerminalSpawnAdmissionError,
  deriveLinuxTerminalSpawnPolicy,
  parseLinuxMeminfo,
  type LinuxMemoryInfo
} from './linux-terminal-spawn-admission'

const GIB = 1024 ** 3
const MIB = 1024 ** 2

function memory(totalGiB: number, availableGiB: number): LinuxMemoryInfo {
  return { totalBytes: totalGiB * GIB, availableBytes: availableGiB * GIB }
}

function env(overrides: NodeJS.ProcessEnv = {}): NodeJS.ProcessEnv {
  return {
    ORCA_LINUX_MAX_TERMINALS: '12',
    ORCA_LINUX_MAX_AGENTS: '4',
    ORCA_LINUX_MAX_CONCURRENT_STARTS: '2',
    ORCA_LINUX_MEMORY_RESERVE_MB: '2048',
    ORCA_LINUX_TERMINAL_RESERVATION_MB: '256',
    ORCA_LINUX_AGENT_RESERVATION_MB: '2048',
    ...overrides
  }
}

describe('Linux terminal spawn admission', () => {
  it('parses MemAvailable and converts kernel KiB to bytes', () => {
    expect(
      parseLinuxMeminfo(`
MemTotal:       16384000 kB
MemFree:         1000000 kB
MemAvailable:    7000000 kB
Cached:          3000000 kB
`)
    ).toEqual({
      totalBytes: 16_384_000 * 1024,
      availableBytes: 7_000_000 * 1024
    })
  })

  it('derives available memory when an older kernel omits MemAvailable', () => {
    expect(
      parseLinuxMeminfo(`
MemTotal:        8000000 kB
MemFree:         1000000 kB
Buffers:          200000 kB
Cached:          2500000 kB
SReclaimable:     400000 kB
Shmem:            100000 kB
`)
    ).toEqual({
      totalBytes: 8_000_000 * 1024,
      availableBytes: 4_000_000 * 1024
    })
  })

  it('applies explicit positive env overrides and ignores invalid values', () => {
    const policy = deriveLinuxTerminalSpawnPolicy(memory(32, 20), {
      ...env(),
      ORCA_LINUX_MAX_TERMINALS: '18',
      ORCA_LINUX_MAX_AGENTS: '-1',
      ORCA_LINUX_MEMORY_RESERVE_MB: '4096'
    })

    expect(policy.maxTerminals).toBe(18)
    expect(policy.maxAgents).toBeGreaterThan(0)
    expect(policy.minimumAvailableBytes).toBe(4096 * MIB)
  })

  it('bypasses attach-only and non-Linux requests without reading memory', async () => {
    const readMemoryInfo = vi.fn(async () => memory(16, 12))
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'darwin',
      env: env(),
      readMemoryInfo,
      readInventory: () => ({ liveTerminals: 999, liveAgents: 999 })
    })

    const releasePlatform = await admission.acquire({ createsNewSession: true, isAgent: true })
    const releaseAttach = await new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env(),
      readMemoryInfo,
      readInventory: () => ({ liveTerminals: 999, liveAgents: 999 })
    }).acquire({ createsNewSession: false, isAgent: true })

    releasePlatform()
    releaseAttach()
    expect(readMemoryInfo).not.toHaveBeenCalled()
  })

  it('counts pending starts before another concurrent request can enter', async () => {
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env({ ORCA_LINUX_MAX_CONCURRENT_STARTS: '1' }),
      readMemoryInfo: async () => memory(32, 24),
      readInventory: () => ({ liveTerminals: 0, liveAgents: 0 })
    })

    const release = await admission.acquire({ createsNewSession: true, isAgent: true })
    await expect(
      admission.acquire({ createsNewSession: true, isAgent: false })
    ).rejects.toMatchObject({ code: 'linux_terminal_start_limit' })

    release()
    await expect(
      admission.acquire({ createsNewSession: true, isAgent: false })
    ).resolves.toEqual(expect.any(Function))
  })

  it('enforces the live plus pending agent limit', async () => {
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env({ ORCA_LINUX_MAX_AGENTS: '2' }),
      readMemoryInfo: async () => memory(32, 24),
      readInventory: () => ({ liveTerminals: 3, liveAgents: 1 })
    })

    const release = await admission.acquire({ createsNewSession: true, isAgent: true })
    await expect(
      admission.acquire({ createsNewSession: true, isAgent: true })
    ).rejects.toMatchObject({ code: 'linux_agent_terminal_limit' })
    release()
  })

  it('preserves the configured memory reserve including pending estimates', async () => {
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env({
        ORCA_LINUX_MEMORY_RESERVE_MB: '2048',
        ORCA_LINUX_AGENT_RESERVATION_MB: '1536'
      }),
      readMemoryInfo: async () => memory(16, 4),
      readInventory: () => ({ liveTerminals: 1, liveAgents: 0 })
    })

    const release = await admission.acquire({ createsNewSession: true, isAgent: true })
    await expect(
      admission.acquire({ createsNewSession: true, isAgent: true })
    ).rejects.toMatchObject({ code: 'linux_memory_reserve' })
    release()
  })

  it('fails closed with a stable code when Linux memory cannot be observed', async () => {
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env(),
      readMemoryInfo: async () => {
        throw new Error('proc unavailable')
      },
      readInventory: () => ({ liveTerminals: 0, liveAgents: 0 })
    })

    await expect(
      admission.acquire({ createsNewSession: true, isAgent: false })
    ).rejects.toEqual(
      expect.objectContaining<Partial<LinuxTerminalSpawnAdmissionError>>({
        code: 'linux_memory_unavailable'
      })
    )
  })

  it('returns an idempotent release that restores every reservation counter', async () => {
    const admission = new LinuxTerminalSpawnAdmission({
      platform: 'linux',
      env: env({ ORCA_LINUX_MAX_TERMINALS: '1' }),
      readMemoryInfo: async () => memory(16, 12),
      readInventory: () => ({ liveTerminals: 0, liveAgents: 0 })
    })

    const release = await admission.acquire({ createsNewSession: true, isAgent: false })
    release()
    release()

    await expect(
      admission.acquire({ createsNewSession: true, isAgent: false })
    ).resolves.toEqual(expect.any(Function))
  })
})
