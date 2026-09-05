from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    if text.count(old) != 1:
        raise SystemExit(f'{path}: expected exactly one replacement target, found {text.count(old)}')
    file.write_text(text.replace(old, new))


replace_once(
    'src/main/daemon/daemon-server-options.ts',
    "import type { DaemonFileLog } from './daemon-file-log'\n",
    "import type { DaemonFileLog } from './daemon-file-log'\n"
    "import type { TerminalSpawnAdmission } from './linux-terminal-spawn-admission'\n",
)
replace_once(
    'src/main/daemon/daemon-server-options.ts',
    '  log?: DaemonFileLog\n',
    '  log?: DaemonFileLog\n  terminalSpawnAdmission?: TerminalSpawnAdmission\n',
)

replace_once(
    'src/main/daemon/terminal-host.ts',
    "import { randomUUID } from 'node:crypto'\n",
    "import { randomUUID } from 'node:crypto'\n"
    "import { recognizeAgentProcess } from '../../shared/agent-process-recognition'\n",
)
replace_once(
    'src/main/daemon/terminal-host.ts',
    '  // Why: null-not-throw — fetched for the tab-bar icon, so a vanished pane should quietly yield "no agent".\n'
    '  getForegroundProcess(sessionId: string): string | null {\n',
    "  hasLiveSession(sessionId: string): boolean {\n"
    "    return this.sessions.get(sessionId)?.isAlive === true\n"
    "  }\n\n"
    "  getTerminalSpawnInventory(): { liveTerminals: number; liveAgents: number } {\n"
    "    let liveTerminals = 0\n"
    "    let liveAgents = 0\n"
    "    for (const session of this.sessions.values()) {\n"
    "      if (!session.isAlive) {\n"
    "        continue\n"
    "      }\n"
    "      liveTerminals += 1\n"
    "      if (session.launchAgent || recognizeAgentProcess(session.getForegroundProcess())) {\n"
    "        liveAgents += 1\n"
    "      }\n"
    "    }\n"
    "    return { liveTerminals, liveAgents }\n"
    "  }\n\n"
    '  // Why: null-not-throw — fetched for the tab-bar icon, so a vanished pane should quietly yield "no agent".\n'
    '  getForegroundProcess(sessionId: string): string | null {\n',
)

replace_once(
    'src/main/daemon/daemon-terminal-admission.ts',
    "import { isTuiAgent } from '../../shared/tui-agent-config'\n",
    "import { isTuiAgent } from '../../shared/tui-agent-config'\n"
    "import { recognizeAgentProcessFromCommandLine } from '../../shared/agent-process-recognition'\n"
    "import type { TerminalSpawnAdmission } from './linux-terminal-spawn-admission'\n",
)
replace_once(
    'src/main/daemon/daemon-terminal-admission.ts',
    '  log: DaemonFileLog\n',
    '  log: DaemonFileLog\n  spawnAdmission: TerminalSpawnAdmission\n',
)
replace_once(
    'src/main/daemon/daemon-terminal-admission.ts',
    '    let spawnPreparation: PendingPtySpawnPreparation | null = null\n',
    '    let spawnPreparation: PendingPtySpawnPreparation | null = null\n'
    '    let releaseSpawnAdmission: (() => void) | null = null\n',
)
identity_check = """      if (
        payload.agentSessionEnsure !== undefined &&
        (!isAgentSessionExecutionClaim(payload.agentSessionEnsure.claim) ||
          !isAgentSessionSurfaceBinding(payload.agentSessionEnsure.surface))
      ) {
        throw new Error('agent_session_identity_required')
      }
"""
replace_once(
    'src/main/daemon/daemon-terminal-admission.ts',
    identity_check,
    identity_check
    + """      releaseSpawnAdmission = await this.options.spawnAdmission.acquire({
        createsNewSession: !attachOnly && !this.options.host.hasLiveSession(payload.sessionId),
        isAgent:
          isTuiAgent(payload.launchAgent) ||
          recognizeAgentProcessFromCommandLine(payload.command, {
            includeHeadlessOneShot: true
          }) !== null
      })
""",
)
replace_once(
    'src/main/daemon/daemon-terminal-admission.ts',
    '    } finally {\n      if (spawnPreparation) {\n',
    '    } finally {\n      releaseSpawnAdmission?.()\n      if (spawnPreparation) {\n',
)

replace_once(
    'src/main/daemon/daemon-server.ts',
    "import { DaemonTerminalAdmission } from './daemon-terminal-admission'\n",
    "import { DaemonTerminalAdmission } from './daemon-terminal-admission'\n"
    "import { LinuxTerminalSpawnAdmission } from './linux-terminal-spawn-admission'\n",
)
replace_once(
    'src/main/daemon/daemon-server.ts',
    """    this.admission = new DaemonTerminalAdmission({
      host: this.host,
""",
    """    const terminalSpawnAdmission =
      options.terminalSpawnAdmission ??
      new LinuxTerminalSpawnAdmission({
        readInventory: () => this.host.getTerminalSpawnInventory(),
        log: (event, details) => this.log.log(event, details)
      })
    this.admission = new DaemonTerminalAdmission({
      host: this.host,
      spawnAdmission: terminalSpawnAdmission,
""",
)
