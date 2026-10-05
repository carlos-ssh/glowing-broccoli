#!/bin/bash
# Construye MaschineMK1-<version>.pkg con un binario universal (Intel + Apple Silicon).
# Uso: ./build-pkg.sh [version]
#   Firma opcional: SIGN_ID="Developer ID Installer: Nombre (TEAMID)" ./build-pkg.sh
set -euo pipefail
cd "$(dirname "$0")"
VERSION="${1:-0.1.0}"
ID="io.github.carlos-ssh.maschine-mk1"
OUT="build"
rm -rf "$OUT" && mkdir -p "$OUT/root/usr/local/libexec/maschine-mk1" "$OUT/root/Library/LaunchAgents"

clang -arch x86_64 -arch arm64 -mmacosx-version-min=10.13 -Wno-deprecated-declarations \
      -o "$OUT/root/usr/local/libexec/maschine-mk1/mk1midi" ../driver/mk1midi.c \
      -framework IOKit -framework CoreFoundation -framework CoreMIDI
cp uninstall.sh "$OUT/root/usr/local/libexec/maschine-mk1/uninstall.sh"
cp "$ID.plist" "$OUT/root/Library/LaunchAgents/$ID.plist"
chmod 644 "$OUT/root/Library/LaunchAgents/$ID.plist"

pkgbuild --root "$OUT/root" --identifier "$ID" --version "$VERSION" \
         --scripts scripts --install-location / "$OUT/component.pkg"

SIGN=()
[ -n "${SIGN_ID:-}" ] && SIGN=(--sign "$SIGN_ID")
productbuild --package "$OUT/component.pkg" ${SIGN[@]+"${SIGN[@]}"} "$OUT/MaschineMK1-$VERSION.pkg"
echo "Listo: packaging/$OUT/MaschineMK1-$VERSION.pkg"
[ -z "${SIGN_ID:-}" ] && echo "Aviso: sin firmar. Gatekeeper pedira abrirlo con clic derecho -> Abrir."
