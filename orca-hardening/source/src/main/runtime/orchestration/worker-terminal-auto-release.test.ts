import { describe, expect, it, vi } from 'vitest'
import type { OrchestrationDb } from './db'
import type { OrcaRuntimeService } from '../orca-runtime'
import {
  scheduleSettledWorkerTerminalAutoRelease,
  type WorkerTerminalAutoReleaseDisposition
} from './worker-terminal-auto-release'

function fixture(options: {
  lifecycle?: { action: 'completed' | 'failed'; taskId: string; dispatchId: string } | { action: 'ignored' }
  resource?: { release_state: string; retained_reason: string | null } | null
  requestDisposition?: 'requested' | 'already_released' | 'retained'
  requestThrows?: boolean
} = {}) {
  const lifecycle = options.lifecycle ?? {
    action: 'completed' as const,
    taskId: 'task_1',
    dispatchId: 'ctx_1'
  }
  const resource =
    options.resource === undefined
      ? { release_state: 'not_requested', retained_reason: null }
      : options.resource
  const requestWorkerTerminalRelease = vi.fn(() => {
    if (options.requestThrows) {
      throw new Error('release request failed')
    }
    const disposition = options.requestDisposition ?? 'requested'
    return disposition === 'retained'
      ? { disposition, resource: resource as never, reason: 'identity_unproven' as const }
      : { disposition, resource: resource as never }
  })
  const getWorkerTerminalResourceByOwner = vi.fn(() => resource as never)
  const reconcile = vi.fn(async () => ({
    attempted: 1,
    released: 1,
    pending: 0,
    unknown: 0,
    retained: 0
  }))
  const scheduled: (() => void)[] = []
  const schedule = vi.fn((task: () => void) => {
    scheduled.push(task)
  })
  const log = vi.fn()
  const db = {
    getWorkerTerminalResourceByOwner,
    requestWorkerTerminalRelease
  } as unknown as OrchestrationDb
  const runtime = {} as OrcaRuntimeService

  const disposition = scheduleSettledWorkerTerminalAutoRelease({
    db,
    runtime,
    lifecycle: lifecycle as never,
    reconcile,
    schedule,
    log
  })

  return {
    disposition,
    requestWorkerTerminalRelease,
    getWorkerTerminalResourceByOwner,
    reconcile,
    schedule,
    scheduled,
    log,
    runtime
  }
}

describe('settled worker terminal auto release', () => {
  it('ignores lifecycle results that did not settle a worker', () => {
    const result = fixture({ lifecycle: { action: 'ignored' } })

    expect(result.disposition).toBe<WorkerTerminalAutoReleaseDisposition>('ignored')
    expect(result.getWorkerTerminalResourceByOwner).not.toHaveBeenCalled()
    expect(result.requestWorkerTerminalRelease).not.toHaveBeenCalled()
  })

  it('ignores a settled dispatch without an owned terminal resource', () => {
    const result = fixture({ resource: null })

    expect(result.disposition).toBe('ignored')
    expect(result.requestWorkerTerminalRelease).not.toHaveBeenCalled()
  })

  it('preserves an explicit user retain', () => {
    const result = fixture({
      resource: { release_state: 'retained', retained_reason: 'user_requested' }
    })

    expect(result.disposition).toBe('retained')
    expect(result.requestWorkerTerminalRelease).not.toHaveBeenCalled()
    expect(result.schedule).not.toHaveBeenCalled()
  })

  it.each(['completed', 'failed'] as const)(
    'requests and schedules release after a %s worker report',
    (action) => {
      const result = fixture({
        lifecycle: { action, taskId: 'task_1', dispatchId: 'ctx_1' }
      })

      expect(result.disposition).toBe('requested')
      expect(result.requestWorkerTerminalRelease).toHaveBeenCalledWith('ctx_1')
      expect(result.schedule).toHaveBeenCalledOnce()
      result.scheduled[0]()
      expect(result.reconcile).toHaveBeenCalledWith(result.runtime)
    }
  )

  it('does not schedule work when the release state machine retains the resource', () => {
    const result = fixture({ requestDisposition: 'retained' })

    expect(result.disposition).toBe('retained')
    expect(result.schedule).not.toHaveBeenCalled()
  })

  it('does not turn a valid worker completion into an RPC failure when release setup throws', () => {
    const result = fixture({ requestThrows: true })

    expect(result.disposition).toBe('failed')
    expect(result.schedule).not.toHaveBeenCalled()
    expect(result.log).toHaveBeenCalledWith(
      'worker terminal auto-release request failed',
      expect.objectContaining({ dispatchId: 'ctx_1', error: 'release request failed' })
    )
  })
})
