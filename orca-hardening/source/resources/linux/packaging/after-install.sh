#!/bin/bash
# Registers packaged launchers without replacing unrelated system files.
set -e

cli_link="/usr/bin/orca-ide"
desktop_link="/usr/bin/orca-hardened-desktop"

is_owned_link() {
  local link="$1" basename="$2"
  [ -L "$link" ] || return 1
  local link_target candidate candidate_target
  link_target="$(readlink -f -- "$link" 2>/dev/null || true)"
  for candidate in "/opt/Orca/resources/bin/$basename" "/opt/orca-ide/resources/bin/$basename" "/opt/orca/resources/bin/$basename"; do
    candidate_target="$(readlink -f -- "$candidate" 2>/dev/null || true)"
    if [ -n "$candidate_target" ] && [ "$link_target" = "$candidate_target" ]; then
      return 0
    fi
  done
  return 1
}

register_owned_link() {
  local target="$1" link="$2" basename="$3"
  [ -x "$target" ] || return 0
  if { [ ! -e "$link" ] && [ ! -L "$link" ]; } || is_owned_link "$link" "$basename"; then
    ln -sfn -- "$target" "$link"
  fi
}

desktop_file="${ORCA_HARDENED_DESKTOP_FILE:-/usr/share/applications/orca-ide.desktop}"
if [ -f "$desktop_file" ]; then
  sed -i 's|^Exec=.*|Exec=orca-hardened-desktop %U|' "$desktop_file"
fi

for dir in /opt/Orca /opt/orca-ide /opt/orca; do
  sandbox="$dir/chrome-sandbox"
  if [ -f "$sandbox" ]; then
    chmod 4755 "$sandbox" || true
  fi

  cli="$dir/resources/bin/orca-ide"
  desktop="$dir/resources/bin/orca-hardened-desktop"
  if [ -x "$cli" ] || [ -x "$desktop" ]; then
    register_owned_link "$cli" "$cli_link" "orca-ide"
    register_owned_link "$desktop" "$desktop_link" "orca-hardened-desktop"
    break
  fi
done

exit 0
