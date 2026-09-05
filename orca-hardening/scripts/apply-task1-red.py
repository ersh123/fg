from pathlib import Path

session_test = Path('source/src/main/daemon/session.test.ts')
text = session_test.read_text()

old_retry = """    it('allows a graceful retry when the first kill is rejected', () => {
      let attempts = 0
      subprocess.kill = () => {
        attempts++
        if (attempts === 1) {
          throw new Error('graceful kill rejected')
        }
      }
      createSession()
"""
new_retry = """    it('allows a graceful retry when the first kill is rejected', () => {
      let attempts = 0
      subprocess.kill = () => {
        attempts++
        if (attempts === 1) {
          throw new Error('graceful kill rejected')
        }
      }
      killWithDescendantSweepMock.mockImplementation(
        (_pid: number, signalRoot: () => void) => signalRoot()
      )
      createSession()
"""
assert old_retry in text
text = text.replace(old_retry, new_retry)

old_kill = """    it('non-agent kill stays synchronous and never routes through the descendant sweep', () => {
      createSession()
      session.kill()
      expect(subprocess.killed).toBe(true)
      expect(killWithDescendantSweepMock).not.toHaveBeenCalled()
    })
"""
new_kill = """    it('plain-session kill snapshots descendants before signalling the root', () => {
      createSession()
      session.kill()
      expect(killWithDescendantSweepMock).toHaveBeenCalledWith(
        subprocess.pid,
        expect.any(Function),
        expect.objectContaining({ ownsRoot: expect.any(Function) })
      )
      expect(subprocess.killed).toBe(false)
      const killRoot = killWithDescendantSweepMock.mock.calls[0][1] as () => void
      killRoot()
      expect(subprocess.killed).toBe(true)
    })
"""
assert old_kill in text
text = text.replace(old_kill, new_kill)
session_test.write_text(text)

teardown_test = Path('source/src/main/daemon/terminal-session-teardown.test.ts')
text = teardown_test.read_text()

old_immediate = """  it('non-win32 immediate kill skips the tree kill (pgroup force-kill suffices)', async () => {
    setPlatform('linux')
    const session = createPlainShellSession()
    const teardown = new TerminalSessionTeardown(new Map([['s1', session]]))

    await teardown.killSession('s1', session, true)

    expect(killWithDescendantSweepMock).not.toHaveBeenCalled()
    expect(session.forceKillAndWaitForExit).toHaveBeenCalled()
  })
"""
new_immediate = """  it('linux immediate kill snapshots descendants before force-killing the root', async () => {
    setPlatform('linux')
    const session = createPlainShellSession()
    const teardown = new TerminalSessionTeardown(new Map([['s1', session]]))

    await teardown.killSession('s1', session, true)

    expect(killWithDescendantSweepMock).toHaveBeenCalledWith(
      4242,
      expect.any(Function),
      expect.objectContaining({ ownsRoot: expect.any(Function) })
    )
    expect(session.forceKillAndWaitForExit).toHaveBeenCalled()
  })
"""
assert old_immediate in text
text = text.replace(old_immediate, new_immediate)

old_graceful = """  it('non-immediate (graceful) kill uses the plain kill path without a sweep', async () => {
    setPlatform('win32')
    const session = createPlainShellSession()
    const teardown = new TerminalSessionTeardown(new Map([['s1', session]]))

    await teardown.killSession('s1', session, false)

    expect(killWithDescendantSweepMock).not.toHaveBeenCalled()
    expect(session.forceKillAndWaitForExit).not.toHaveBeenCalled()
    expect(session.kill).toHaveBeenCalled()
  })
"""
new_graceful = """  it('linux graceful close snapshots descendants for a hand-typed agent', async () => {
    setPlatform('linux')
    const session = createPlainShellSession()
    const teardown = new TerminalSessionTeardown(new Map([['s1', session]]))

    await teardown.killSession('s1', session, false)

    expect(killWithDescendantSweepMock).toHaveBeenCalledWith(
      4242,
      expect.any(Function),
      expect.objectContaining({ ownsRoot: expect.any(Function) })
    )
    expect(session.scheduleForceDisposeFallback).toHaveBeenCalled()
    expect(session.signalTerminationRoot).not.toHaveBeenCalled()
    const killRoot = killWithDescendantSweepMock.mock.calls[0][1] as () => void
    killRoot()
    expect(session.signalTerminationRoot).toHaveBeenCalled()
  })
"""
assert old_graceful in text
text = text.replace(old_graceful, new_graceful)
teardown_test.write_text(text)
