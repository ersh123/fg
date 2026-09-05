#!/bin/bash
# Removes only symlinks created by after-install.sh.
set -e

case "${1-}" in
  0 | remove | purge) ;;
  *) exit 0 ;;
esac

link="/usr/bin/orca-ide"
desktop_link="/usr/bin/orca-hardened-desktop"

remove_owned_link() {
  local candidate="$1"
  if [ -L "$candidate" ]; then
    target="$(readlink "$candidate" || true)"
    case "$target" in
      /opt/Orca/*|/opt/orca-ide/*|/opt/orca/*)
        rm -f "$candidate"
        ;;
    esac
  fi
}

remove_owned_link "$link"
remove_owned_link "$desktop_link"

exit 0
