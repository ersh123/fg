import { beforeEach, describe, expect, it, vi } from 'vitest'

const reconcileLifecycleMessageMock = vi.hoisted(() => vi.fn())
const scheduleSettledWorkerTerminalAutoReleaseMock = vi.hoisted(() => vi.fn())

vi.mock('../../orchestration/lifecycle-reconciliation', () => ({
  reconcileLifecycleMessage: reconcileLifecycleMessageMock
}))
vi.mock('../../orchestration/worker-terminal-auto-release', () => ({
  scheduleSettledWorkerTerminalAutoRelease: scheduleSettledWorkerTerminalAutoReleaseMock
}))

import { checkDirectMailbox } from './orchestration-check-direct'
import { sendPointToPointMessage } from './orchestration-send-point-to-point'

const message = {
  id: 'msg_done',
  from_handle: 'worker-1',
  to_handle: 'coordinator',
  subject: 'done',
  body: 'finished',
  type: 'worker_done',
  priority: 'normal',
  thread_id: null,
  payload: JSON.stringify({ taskId: 'task-1', dispatchId: 'ctx-1', outcome: 'succeeded' }),
  sender_pane_key: null,
  run_id: null,
  delivery_contract: null,
  delivered_at: null,
  read_at: null,
  created_at: '2026-09-05T00:00:00.000Z'
} as const

const lifecycle = {
  action: 'completed' as const,
  taskId: 'task-1',
  dispatchId: 'ctx-1'
}

describe('worker terminal auto-release wiring', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    reconcileLifecycleMessageMock.mockReturnValue(lifecycle)
  })

  it('schedules release when the point-to-point worker_done send settles a dispatch', () => {
    const runtime = { notifyMessageArrived: vi.fn() }
    const db = {
      insertMessage: vi.fn(() => message),
      getDispatchContextById: vi.fn(() => undefined)
    }

    sendPointToPointMessage({
      params: {
        subject: 'done',
        body: 'finished',
        type: 'worker_done',
        priority: 'normal',
        payload: { taskId: 'task-1', dispatchId: 'ctx-1', outcome: 'succeeded' }
      } as never,
      runtime: runtime as never,
      db: db as never,
      from: 'worker-1',
      to: 'coordinator',
      dispatchId: undefined,
      messageRunId: undefined,
      senderPaneKey: undefined,
      legacyCoordinatorRunId: undefined,
      orchestrationCapability: undefined,
      resolveProcessIncarnation: () => undefined,
      revalidateLegacyCoordinator: undefined,
      withSendWarnings: <T extends object>(receipt: T) => receipt
    })

    expect(scheduleSettledWorkerTerminalAutoReleaseMock).toHaveBeenCalledWith({
      db,
      runtime,
      lifecycle
    })
  })

  it('schedules release when a direct unread check performs deferred reconciliation', async () => {
    const runtime = { waitForMessage: vi.fn(), notifyMessageArrived: vi.fn() }
    const db = {
      getUnreadMessages: vi.fn(() => [message]),
      getAllMessagesForHandle: vi.fn(() => []),
      getMessageById: vi.fn(() => message),
      markAsRead: vi.fn()
    }

    await checkDirectMailbox({
      params: { wait: false } as never,
      runtime: runtime as never,
      db: db as never,
      handle: 'coordinator',
      typeFilter: undefined,
      signal: undefined
    })

    expect(scheduleSettledWorkerTerminalAutoReleaseMock).toHaveBeenCalledWith({
      db,
      runtime,
      lifecycle
    })
  })
})
