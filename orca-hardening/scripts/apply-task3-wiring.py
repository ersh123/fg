from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    if text.count(old) != 1:
        raise SystemExit(f'{path}: expected exactly one replacement target, found {text.count(old)}')
    file.write_text(text.replace(old, new))


replace_once(
    'src/main/runtime/rpc/methods/orchestration-send-point-to-point.ts',
    "import { reconcileLifecycleMessage } from '../../orchestration/lifecycle-reconciliation'\n",
    "import { reconcileLifecycleMessage } from '../../orchestration/lifecycle-reconciliation'\n"
    "import { scheduleSettledWorkerTerminalAutoRelease } from '../../orchestration/worker-terminal-auto-release'\n",
)
replace_once(
    'src/main/runtime/rpc/methods/orchestration-send-point-to-point.ts',
    """    const reconciled = reconcileLifecycleMessage(db, msg)
    // Why: a suppressed message is already read, so skip the notify that would wake a check --wait waiter to an empty result.
""",
    """    const reconciled = reconcileLifecycleMessage(db, msg)
    scheduleSettledWorkerTerminalAutoRelease({ db, runtime, lifecycle: reconciled })
    // Why: a suppressed message is already read, so skip the notify that would wake a check --wait waiter to an empty result.
""",
)

replace_once(
    'src/main/runtime/rpc/methods/orchestration-check-direct.ts',
    "import { reconcileLifecycleMessage } from '../../orchestration/lifecycle-reconciliation'\n",
    "import { reconcileLifecycleMessage } from '../../orchestration/lifecycle-reconciliation'\n"
    "import { scheduleSettledWorkerTerminalAutoRelease } from '../../orchestration/worker-terminal-auto-release'\n",
)
replace_once(
    'src/main/runtime/rpc/methods/orchestration-check-direct.ts',
    """        const reconciled = reconcileLifecycleMessage(db, message)
        return reconciled.action === 'rejected'
""",
    """        const reconciled = reconcileLifecycleMessage(db, message)
        scheduleSettledWorkerTerminalAutoRelease({ db, runtime, lifecycle: reconciled })
        return reconciled.action === 'rejected'
""",
)
