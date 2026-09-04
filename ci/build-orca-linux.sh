#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$RUNNER_TEMP/orca-linux-hardened"
rm -rf "$WORK"
git clone --depth 1 --branch v1.4.197 https://github.com/stablyai/orca.git "$WORK"
git -C "$WORK" apply --check "$ROOT/patches/orca-linux-production.patch"
git -C "$WORK" apply "$ROOT/patches/orca-linux-production.patch"
cd "$WORK"

corepack enable
corepack prepare pnpm@12.0.0 --activate
pnpm install --frozen-lockfile

pnpm exec vitest run --config config/vitest.config.ts \
  src/main/daemon/terminal-session-teardown.test.ts \
  src/main/daemon/linux-terminal-admission-budget.test.ts \
  src/renderer/src/components/native-chat/use-native-chat-composer-attachments.test.tsx \
  config/scripts/linux-production-hardening.test.mjs

pnpm run typecheck:node
pnpm run typecheck:web
pnpm run check:code-quality:changed

export ORCA_LOCAL_BUILD_VERSION=1.4.197-hardened.1
export ORCA_BUILD_COMMIT="$(git rev-parse HEAD)"
pnpm run build:desktop
pnpm run ensure:electron-runtime
pnpm exec electron-builder --config config/electron-builder.config.cjs --linux deb --x64 --publish never

mkdir -p "$ROOT/out"
find dist -maxdepth 2 -type f -name '*.deb' -exec cp -v {} "$ROOT/out/orca-hardened_1.4.197-hardened.1_amd64.deb" \;
test -s "$ROOT/out/orca-hardened_1.4.197-hardened.1_amd64.deb"
dpkg-deb --info "$ROOT/out/orca-hardened_1.4.197-hardened.1_amd64.deb"
dpkg-deb --contents "$ROOT/out/orca-hardened_1.4.197-hardened.1_amd64.deb" > "$ROOT/out/deb-contents.txt"
sha256sum "$ROOT/out/orca-hardened_1.4.197-hardened.1_amd64.deb" > "$ROOT/out/SHA256SUMS"
