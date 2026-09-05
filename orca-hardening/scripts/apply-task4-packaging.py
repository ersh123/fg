from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    if text.count(old) != 1:
        raise SystemExit(f'{path}: expected exactly one replacement target, found {text.count(old)}')
    file.write_text(text.replace(old, new))


replace_once(
    'config/electron-builder.config.cjs',
    """      {
        from: 'resources/linux/bin/orca-ide',
        to: 'bin/orca-ide'
      },
""",
    """      {
        from: 'resources/linux/bin/orca-ide',
        to: 'bin/orca-ide'
      },
      {
        from: 'resources/linux/bin/orca-hardened-desktop',
        to: 'bin/orca-hardened-desktop'
      },
""",
)

replace_once(
    'config/scripts/linux-hardened-launcher.test.mjs',
    """  it('packages the wrapper and makes it the desktop-entry command', () => {
    const config = readFileSync(builderConfig, 'utf8')
    assert.match(config, /orca-hardened-desktop %U/)
    assert.match(config, /resources\\/linux\\/bin\\/orca-hardened-desktop/)
  })
""",
    """  it('packages the bounded desktop launcher as a Linux resource', () => {
    const config = readFileSync(builderConfig, 'utf8')
    assert.match(config, /resources\\/linux\\/bin\\/orca-hardened-desktop/)
    assert.doesNotMatch(config, /desktop:\\s*\\{[\\s\\S]*Exec:/)
  })
""",
)

replace_once(
    'config/scripts/linux-hardened-launcher.test.mjs',
    """  it('registers and removes only the owned desktop launcher symlink', () => {
    assert.match(readFileSync(afterInstall, 'utf8'), /orca-hardened-desktop/)
    assert.match(readFileSync(afterRemove, 'utf8'), /orca-hardened-desktop/)
  })
})
""",
    """  it('registers and removes only the owned desktop launcher symlink', () => {
    assert.match(readFileSync(afterInstall, 'utf8'), /orca-hardened-desktop/)
    assert.match(readFileSync(afterRemove, 'utf8'), /orca-hardened-desktop/)
  })

  it('rewrites the installed desktop entry through the bounded launcher', () => {
    const directory = tempDir()
    const desktopFile = join(directory, 'orca-ide.desktop')
    writeFileSync(
      desktopFile,
      ['[Desktop Entry]', 'Name=Orca', 'Exec=/opt/Orca/orca-ide %U', ''].join('\\n')
    )

    const result = spawnSync('bash', [afterInstall], {
      encoding: 'utf8',
      env: { ...process.env, ORCA_HARDENED_DESKTOP_FILE: desktopFile }
    })

    assert.equal(result.status, 0, result.stderr)
    assert.match(readFileSync(desktopFile, 'utf8'), /^Exec=orca-hardened-desktop %U$/m)
  })
})
""",
)
