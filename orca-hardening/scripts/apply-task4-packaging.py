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
