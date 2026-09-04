#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${RUNNER_TEMP:-/tmp}/orca-linux-hardened"
UPSTREAM_SHA=5ee4ace516080891731d100f843b074408a9ce0e
VERSION=1.4.198-hardened.1
OUT="$ROOT/out"

rm -rf "$WORK" "$OUT"
git clone --filter=blob:none --no-checkout https://github.com/stablyai/orca.git "$WORK"
git -C "$WORK" fetch --depth 1 origin "$UPSTREAM_SHA"
git -C "$WORK" checkout --detach "$UPSTREAM_SHA"
test "$(git -C "$WORK" rev-parse HEAD)" = "$UPSTREAM_SHA"

base_patch="${RUNNER_TEMP:-/tmp}/orca-linux-production.patch"
base64 -d "$ROOT/patches/orca-linux-production-green.patch.gz.b64" | gzip -dc > "$base_patch"
printf '%s  %s\n' 'cf2381f60caa483978b2895bcb37198cbf548a91d9a8fdf411a8f15eb79b7014' "$base_patch" | sha256sum --check --strict

test "$(git -C "$ROOT" hash-object patches/orca-linux-production-green-fix-v2.patch)" = '41c0a016a35e3fbdff69f245f4c873a9e66b18e8'
test "$(git -C "$ROOT" hash-object patches/orca-linux-production-quality-fix.patch)" = '9166fd0aef14f40e5f6f2e0d22a780a9b0f68ac1'
test "$(git -C "$ROOT" hash-object patches/orca-linux-production-packaging-exec-fix.patch)" = 'f989fefe4ddd5ce9e5a6226742b7ff442a3ef52f'
test "$(git -C "$ROOT" hash-object patches/orca-linux-production-updater-red.patch)" = '535d178da7fdcf964f93d2d7c7c8863372b2ab9f'

patches=(
  "$base_patch"
  "$ROOT/patches/orca-linux-production-green-fix-v2.patch"
  "$ROOT/patches/orca-linux-production-quality-fix.patch"
  "$ROOT/patches/orca-linux-production-packaging-exec-fix.patch"
  "$ROOT/patches/orca-linux-production-updater-red.patch"
)
for patch in "${patches[@]}"; do
  git -C "$WORK" apply --check "$patch"
  git -C "$WORK" apply "$patch"
done
git -C "$WORK" diff --check

git -C "$WORK" config user.name 'Orca Hardened CI'
git -C "$WORK" config user.email 'orca-hardened@users.noreply.github.com'
git -C "$WORK" add -A
git -C "$WORK" commit -m 'build(linux): apply reviewed hardening patchset'
HARDENED_SOURCE_SHA="$(git -C "$WORK" rev-parse HEAD)"

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  at-spi2-core \
  binutils \
  gir1.2-atspi-2.0 \
  python3-gi \
  rpm \
  xauth \
  xclip \
  xdotool \
  xvfb

cd "$WORK"
pnpm install --frozen-lockfile

pnpm exec vitest run --config config/vitest.config.ts \
  src/main/daemon/terminal-session-teardown.test.ts \
  src/main/daemon/linux-terminal-admission-budget.test.ts \
  src/main/daemon/daemon-terminal-admission-linux.test.ts \
  src/main/updater.hardened-linux.test.ts \
  src/renderer/src/components/native-chat/use-native-chat-composer-attachments.test.tsx \
  config/scripts/linux-production-hardening.test.mjs \
  config/scripts/linux-package-maintainer-scripts.test.mjs \
  src/main/cli/packaged-cli-assets.test.ts

NODE_OPTIONS=--max-old-space-size=8192 pnpm run typecheck:node
NODE_OPTIONS=--max-old-space-size=8192 pnpm run typecheck:web
pnpm run check:code-quality:changed -- "$UPSTREAM_SHA"

export NODE_OPTIONS=--max-old-space-size=8192
export ORCA_LOCAL_BUILD_VERSION="$VERSION"
export ORCA_BUILD_COMMIT="$HARDENED_SOURCE_SHA"
pnpm run build:desktop
pnpm run ensure:electron-runtime
pnpm exec electron-builder --config config/electron-builder.config.cjs --linux deb --x64 --publish never

node -e "require('./config/scripts/verify-linux-glibc-floor.cjs').verifyLinuxGlibcFloor('dist/linux-unpacked/resources', { targetArch: 'x64' })"
node config/scripts/run-linux-packaged-node-pty-floor-smoke.mjs --app-dir dist/linux-unpacked

deb="$(find dist -maxdepth 2 -type f -name '*.deb' -print -quit)"
test -n "$deb"
test "$(dpkg-deb -f "$deb" Package)" = 'orca-ide'
test "$(dpkg-deb -f "$deb" Architecture)" = 'amd64'
test "$(dpkg-deb -f "$deb" Version)" = "$VERSION"

mkdir -p "$OUT"
cp "$deb" "$OUT/orca-hardened_${VERSION}_amd64.deb"
dpkg-deb --info "$deb" > "$OUT/deb-info.txt"
dpkg-deb --contents "$deb" > "$OUT/deb-contents.txt"
dpkg-deb -f "$deb" Package Version Architecture Depends > "$OUT/deb-metadata.txt"
sha256sum "$OUT/orca-hardened_${VERSION}_amd64.deb" > "$OUT/SHA256SUMS"

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$deb"
test -x /opt/Orca/orca-ide
test -x /usr/bin/orca-hardened
test -x /usr/bin/orca-hardened-doctor
test -x /usr/bin/orca-hardened-gc
test -x /usr/bin/orca-ide
test -L /usr/lib/systemd/user/orca-hardened.slice
test -L /usr/lib/systemd/user/orca-hardened-gc.service
test -L /usr/lib/systemd/user/orca-hardened-gc.timer
grep -F 'Exec=/usr/bin/orca-hardened' /usr/share/applications/orca-ide.desktop

SYSTEMD_UNIT_PATH='/usr/lib/systemd/user:/lib/systemd/user:/usr/lib/systemd/system:/lib/systemd/system' \
  systemd-analyze --user verify \
    /usr/lib/systemd/user/orca-hardened.slice \
    /usr/lib/systemd/user/orca-hardened-gc.service \
    /usr/lib/systemd/user/orca-hardened-gc.timer

/usr/bin/orca-hardened-doctor --json | tee "$OUT/doctor.json"
python3 - "$OUT/doctor.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1]))
assert value['cgroupV2'] is True
assert value['sliceInstalled'] is True
assert value['launcherInstalled'] is True
PY

timeout 60s /usr/bin/orca-ide --help > "$OUT/cli-help.txt"
timeout 30s xvfb-run -a /usr/bin/orca-hardened --version > "$OUT/gui-version.txt"

mkdir -p "$HOME/.config/orca"
printf 'preserve\n' > "$HOME/.config/orca/hardened-uninstall-marker"
package="$(dpkg-deb -f "$deb" Package)"
sudo DEBIAN_FRONTEND=noninteractive apt-get remove -y "$package"
test -f "$HOME/.config/orca/hardened-uninstall-marker"
test ! -L /usr/bin/orca-hardened
test ! -L /usr/bin/orca-hardened-doctor
test ! -L /usr/bin/orca-hardened-gc
test ! -L /usr/lib/systemd/user/orca-hardened.slice
test ! -L /usr/lib/systemd/user/orca-hardened-gc.service
test ! -L /usr/lib/systemd/user/orca-hardened-gc.timer

cat > "$OUT/PRODUCTION-GATE.txt" <<EOF
VERDICT=PRODUCTION_READY_LINUX_AMD64
UPSTREAM_SOURCE_SHA=$UPSTREAM_SHA
HARDENED_SOURCE_SHA=$HARDENED_SOURCE_SHA
PACKAGE_VERSION=$VERSION
TESTS=PASS
TYPECHECK=PASS
CODE_QUALITY=PASS
BUILD=PASS
GLIBC_2_31_FLOOR=PASS
DEB_INSTALL=PASS
CLI_SMOKE=PASS
GUI_SMOKE=PASS
UPSTREAM_UPDATER_DISABLED=PASS
UNINSTALL_ROLLBACK=PASS
USER_DATA_PRESERVATION=PASS
EOF
