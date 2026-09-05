# Orca Linux Hardened 26.9.5-hardened.3

## Install

```bash
sudo apt install ./orca-ide_26.9.5-hardened.3_amd64.deb
```

Launch from the desktop menu or run `orca-hardened-desktop`.

The launcher derives a systemd memory boundary from installed RAM and preserves 20% for the desktop, with a minimum 2 GiB and maximum 8 GiB reserve. The daemon also refuses unsafe terminal or agent starts before memory pressure becomes critical.

Optional overrides: `ORCA_HARDENED_MEMORY_HIGH_MB`, `ORCA_HARDENED_MEMORY_MAX_MB`, `ORCA_HARDENED_SWAP_MAX_MB`, `ORCA_HARDENED_TASKS_MAX`, `ORCA_LINUX_MAX_TERMINALS`, `ORCA_LINUX_MAX_AGENTS`, `ORCA_LINUX_MAX_CONCURRENT_STARTS`, and `ORCA_LINUX_MEMORY_RESERVE_MB`.
