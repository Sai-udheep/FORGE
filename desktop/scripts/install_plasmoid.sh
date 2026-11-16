#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLASMOID_DIR="${SCRIPT_DIR}/../plasmoid/org.forge.execution"

echo "=== Installing FORGE 2.0 KDE Plasma 6 Plasmoid ==="
echo "Plasmoid path: ${PLASMOID_DIR}"

if ! command -v kpackagetool6 &>/dev/null; then
    echo "ERROR: kpackagetool6 not found. Are you on KDE Plasma 6?"
    exit 1
fi

# Check if already installed
if kpackagetool6 -t Plasma/Applet -l | grep -q "org.forge.execution"; then
    echo "Upgrading existing FORGE plasmoid..."
    kpackagetool6 -t Plasma/Applet -u "${PLASMOID_DIR}"
else
    echo "Installing new FORGE plasmoid..."
    kpackagetool6 -t Plasma/Applet -i "${PLASMOID_DIR}"
fi

echo ""
echo "✅ FORGE 2.0 Plasmoid successfully installed!"
echo "To add it to your desktop or panel:"
echo "1. Right-click your KDE desktop or panel -> 'Add Widgets...'"
echo "2. Search for 'FORGE 2.0'"
echo "3. Drag it onto your desktop or panel."
