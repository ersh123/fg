import { readFile } from 'node:fs/promises'

const KIB = 1024
const MIB = 1024 ** 2
const GIB = 1024 ** 3
const DEFAULT_MINIMUM_AVAILABLE_BYTES = 2 * GIB
const DEFAULT_TERMINAL_RESERVATION_BYTES = 256 * MIB
const DEFAULT_AGENT_RESERVATION_BYTES = 2 * GIB
const MAX_DERIVED_MEMORY_RESERVE_BYTES = 8 * GIB

export type LinuxMemoryInfo = {
  totalBytes: number
  availableBytes: number
}

export type LinuxTerminalSpawnInventory = {
  liveTerminals: number
  liveAgents: number
}

export type LinuxTerminalSpawnPolicy = {
  maxTerminals: number
  maxAgents: number
  maxConcurrentStarts: number
  minimumAvailableBytes: number
  terminalReservationBytes: number
  agentReservationBytes: number
}

export type TerminalSpawnAdmissionRequest = {
  createsNewSession: boolean
  isAgent: boolean
}

export type TerminalSpawnAdmission = {
  acquire(request: TerminalSpawnAdmissionRequest): Promise<() => void>
}

export type LinuxTerminalSpawnAdmissionCode =
  | 'linux_terminal_limit'
  | 'linux_agent_terminal_limit'
  | 'linux_terminal_start_limit'
  | 'linux_memory_reserve'
  | 'linux_memory_unavailable'

export class LinuxTerminalSpawnAdmissionError extends Error {
  constructor(
    readonly code: LinuxTerminalSpawnAdmissionCode,
    message: string
  ) {
    super(message)
    this.name = 'LinuxTerminalSpawnAdmissionError'
  }
}

type LinuxTerminalSpawnAdmissionOptions = {
  platform?: NodeJS.Platform
  env?: NodeJS.ProcessEnv
  readMemoryInfo?: () => Promise<LinuxMemoryInfo>
  readInventory: () => LinuxTerminalSpawnInventory
  log?: (event: string, details: Record<string, unknown>) => void
}

type PendingAdmissionState = {
  starts: number
  terminals: number
  agents: number
  reservedBytes: number
}

function readKilobytes(fields: ReadonlyMap<string, number>, name: string): number {
  return Math.max(0, fields.get(name) ?? 0) * KIB
}

export function parseLinuxMeminfo(text: string): LinuxMemoryInfo | null {
  const fields = new Map<string, number>()
  for (const line of text.split(/\r?\n/)) {
    const match = /^([A-Za-z_()]+):\s+(\d+)\s+kB\s*$/.exec(line.trim())
    if (match) {
      fields.set(match[1], Number.parseInt(match[2], 10))
    }
  }

  const totalBytes = readKilobytes(fields, 'MemTotal')
  if (totalBytes <= 0) {
    return null
  }
  const reportedAvailableBytes = readKilobytes(fields, 'MemAvailable')
  const derivedAvailableBytes = Math.max(
    0,
    readKilobytes(fields, 'MemFree') +
      readKilobytes(fields, 'Buffers') +
      readKilobytes(fields, 'Cached') +
      readKilobytes(fields, 'SReclaimable') -
      readKilobytes(fields, 'Shmem')
  )
  const availableBytes = reportedAvailableBytes || derivedAvailableBytes
  if (availableBytes <= 0) {
    return null
  }
  return {
    totalBytes,
    availableBytes: Math.min(totalBytes, availableBytes)
  }
}

function positiveInteger(value: string | undefined): number | null {
  if (!value?.trim()) {
    return null
  }
  const parsed = Number(value)
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : null
}

function envCount(env: NodeJS.ProcessEnv, name: string, fallback: number): number {
  return positiveInteger(env[name]) ?? fallback
}

function envMebibytes(env: NodeJS.ProcessEnv, name: string, fallbackBytes: number): number {
  const value = positiveInteger(env[name])
  return value === null ? fallbackBytes : value * MIB
}

function clampInteger(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, Math.floor(value)))
}

export function deriveLinuxTerminalSpawnPolicy(
  memory: LinuxMemoryInfo,
  env: NodeJS.ProcessEnv = process.env
): LinuxTerminalSpawnPolicy {
  const derivedReserveBytes = Math.min(
    MAX_DERIVED_MEMORY_RESERVE_BYTES,
    Math.max(DEFAULT_MINIMUM_AVAILABLE_BYTES, Math.floor(memory.totalBytes * 0.2))
  )
  const usableBytes = Math.max(0, memory.totalBytes - derivedReserveBytes)
  const derivedMaxAgents = clampInteger(usableBytes / DEFAULT_AGENT_RESERVATION_BYTES, 1, 8)
  const derivedMaxTerminals = clampInteger(usableBytes / (512 * MIB), 4, 24)
  const derivedConcurrentStarts = clampInteger(Math.min(2, derivedMaxAgents), 1, 4)

  return {
    maxTerminals: envCount(env, 'ORCA_LINUX_MAX_TERMINALS', derivedMaxTerminals),
    maxAgents: envCount(env, 'ORCA_LINUX_MAX_AGENTS', derivedMaxAgents),
    maxConcurrentStarts: envCount(
      env,
      'ORCA_LINUX_MAX_CONCURRENT_STARTS',
      derivedConcurrentStarts
    ),
    minimumAvailableBytes: envMebibytes(
      env,
      'ORCA_LINUX_MEMORY_RESERVE_MB',
      derivedReserveBytes
    ),
    terminalReservationBytes: envMebibytes(
      env,
      'ORCA_LINUX_TERMINAL_RESERVATION_MB',
      DEFAULT_TERMINAL_RESERVATION_BYTES
    ),
    agentReservationBytes: envMebibytes(
      env,
      'ORCA_LINUX_AGENT_RESERVATION_MB',
      DEFAULT_AGENT_RESERVATION_BYTES
    )
  }
}

async function readProcMemoryInfo(): Promise<LinuxMemoryInfo> {
  const parsed = parseLinuxMeminfo(await readFile('/proc/meminfo', 'utf8'))
  if (!parsed) {
    throw new Error('Linux memory information is incomplete')
  }
  return parsed
}

function nonNegativeInteger(value: number): number {
  return Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0
}

export class LinuxTerminalSpawnAdmission implements TerminalSpawnAdmission {
  private readonly platform: NodeJS.Platform
  private readonly env: NodeJS.ProcessEnv
  private readonly readMemoryInfo: () => Promise<LinuxMemoryInfo>
  private readonly pending: PendingAdmissionState = {
    starts: 0,
    terminals: 0,
    agents: 0,
    reservedBytes: 0
  }

  constructor(private readonly options: LinuxTerminalSpawnAdmissionOptions) {
    this.platform = options.platform ?? process.platform
    this.env = options.env ?? process.env
    this.readMemoryInfo = options.readMemoryInfo ?? readProcMemoryInfo
  }

  async acquire(request: TerminalSpawnAdmissionRequest): Promise<() => void> {
    if (
      this.platform !== 'linux' ||
      !request.createsNewSession ||
      this.env.ORCA_LINUX_ADMISSION_DISABLED === '1'
    ) {
      return () => {}
    }

    let memory: LinuxMemoryInfo
    try {
      memory = await this.readMemoryInfo()
    } catch {
      throw this.refuse(
        'linux_memory_unavailable',
        'Cannot verify Linux memory safety before starting another terminal.'
      )
    }

    const policy = deriveLinuxTerminalSpawnPolicy(memory, this.env)
    const inventory = this.options.readInventory()
    const liveTerminals = nonNegativeInteger(inventory.liveTerminals)
    const liveAgents = nonNegativeInteger(inventory.liveAgents)
    const requestBytes = request.isAgent
      ? policy.agentReservationBytes
      : policy.terminalReservationBytes

    if (this.pending.starts >= policy.maxConcurrentStarts) {
      throw this.refuse(
        'linux_terminal_start_limit',
        `Linux terminal start limit reached (${policy.maxConcurrentStarts}).`
      )
    }
    if (liveTerminals + this.pending.terminals + 1 > policy.maxTerminals) {
      throw this.refuse(
        'linux_terminal_limit',
        `Linux terminal limit reached (${policy.maxTerminals}); close an idle terminal and retry.`
      )
    }
    if (request.isAgent && liveAgents + this.pending.agents + 1 > policy.maxAgents) {
      throw this.refuse(
        'linux_agent_terminal_limit',
        `Linux agent terminal limit reached (${policy.maxAgents}); release a finished agent and retry.`
      )
    }
    if (
      memory.availableBytes - this.pending.reservedBytes - requestBytes <
      policy.minimumAvailableBytes
    ) {
      throw this.refuse(
        'linux_memory_reserve',
        `Starting another terminal would cross the Linux memory reserve (${Math.ceil(policy.minimumAvailableBytes / MIB)} MiB).`
      )
    }

    this.pending.starts += 1
    this.pending.terminals += 1
    this.pending.agents += request.isAgent ? 1 : 0
    this.pending.reservedBytes += requestBytes
    let released = false
    return () => {
      if (released) {
        return
      }
      released = true
      this.pending.starts -= 1
      this.pending.terminals -= 1
      this.pending.agents -= request.isAgent ? 1 : 0
      this.pending.reservedBytes -= requestBytes
    }
  }

  private refuse(code: LinuxTerminalSpawnAdmissionCode, message: string): Error {
    this.options.log?.('terminal-spawn-refused', {
      code,
      pendingStarts: this.pending.starts,
      pendingTerminals: this.pending.terminals,
      pendingAgents: this.pending.agents,
      pendingReservedBytes: this.pending.reservedBytes
    })
    return new LinuxTerminalSpawnAdmissionError(code, message)
  }
}
