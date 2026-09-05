import type { OrcaRuntimeService } from '../orca-runtime'
import type { OrchestrationDb } from './db'
import type { LifecycleReconciliationResult } from './lifecycle-reconciliation'
import {
  reconcileRequestedWorkerTerminalReleases,
  type WorkerTerminalReleaseReconciliationResult
} from './worker-terminal-release-reconciliation'

const DEFAULT_AUTO_RELEASE_DELAY_MS = 750

type ReconcileWorkerTerminalReleases = (
  runtime: OrcaRuntimeService
) => Promise<WorkerTerminalReleaseReconciliationResult>
type ScheduleAutoRelease = (task: () => void) => void
type AutoReleaseLog = (message: string, details: Record<string, unknown>) => void

export type WorkerTerminalAutoReleaseDisposition =
  | 'ignored'
  | 'retained'
  | 'requested'
  | 'already_released'
  | 'failed'

export type SettledWorkerTerminalAutoReleaseOptions = {
  db: OrchestrationDb
  runtime: OrcaRuntimeService
  lifecycle: LifecycleReconciliationResult
  reconcile?: ReconcileWorkerTerminalReleases
  schedule?: ScheduleAutoRelease
  log?: AutoReleaseLog
}

function scheduleAfterReply(task: () => void): void {
  const timer = setTimeout(task, DEFAULT_AUTO_RELEASE_DELAY_MS)
  timer.unref?.()
}

function defaultLog(message: string, details: Record<string, unknown>): void {
  console.warn(`[orchestration] ${message}`, details)
}

export function scheduleSettledWorkerTerminalAutoRelease(
  options: SettledWorkerTerminalAutoReleaseOptions
): WorkerTerminalAutoReleaseDisposition {
  const { lifecycle } = options
  if (lifecycle.action !== 'completed' && lifecycle.action !== 'failed') {
    return 'ignored'
  }

  const resource = options.db.getWorkerTerminalResourceByOwner(lifecycle.dispatchId)
  if (!resource) {
    return 'ignored'
  }
  if (resource.release_state === 'retained' && resource.retained_reason === 'user_requested') {
    return 'retained'
  }

  const reconcile = options.reconcile ?? reconcileRequestedWorkerTerminalReleases
  const schedule = options.schedule ?? scheduleAfterReply
  const log = options.log ?? defaultLog
  try {
    const request = options.db.requestWorkerTerminalRelease(lifecycle.dispatchId)
    if (request.disposition === 'retained') {
      return 'retained'
    }
    if (request.disposition === 'already_released') {
      return 'already_released'
    }
    schedule(() => {
      void reconcile(options.runtime).catch((error: unknown) => {
        log('worker terminal auto-release reconciliation failed', {
          dispatchId: lifecycle.dispatchId,
          error: error instanceof Error ? error.message : String(error)
        })
      })
    })
    return 'requested'
  } catch (error) {
    log('worker terminal auto-release request failed', {
      dispatchId: lifecycle.dispatchId,
      error: error instanceof Error ? error.message : String(error)
    })
    return 'failed'
  }
}
