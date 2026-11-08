#!/bin/sh
# Construit dist/nanosound-oled_<version>_all.deb
# Usage : ./build-deb.sh [version]   (défaut : contenu du fichier VERSION)
set -eu

cd "$(dirname "$0")"
VERSION="${1:-$(cat VERSION)}"
VERSION="${VERSION#v}"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
chmod 755 "$STAGE"

install -d -m 755 "$STAGE/DEBIAN" "$STAGE/usr/lib/nanosound-oled" "$STAGE/lib/systemd/system" "$STAGE/usr/share/doc/nanosound-oled"
sed "s/@VERSION@/$VERSION/" packaging/DEBIAN/control > "$STAGE/DEBIAN/control"
chmod 644 "$STAGE/DEBIAN/control"
for f in postinst prerm postrm; do
    install -m 755 "packaging/DEBIAN/$f" "$STAGE/DEBIAN/$f"
done
install -m 755 oled_display/oled_display.py "$STAGE/usr/lib/nanosound-oled/oled_display.py"
install -m 644 systemd/nanosound-oled.service "$STAGE/lib/systemd/system/nanosound-oled.service"
install -m 644 LICENSE "$STAGE/usr/share/doc/nanosound-oled/copyright"

# Un retour chariot Windows casserait les scripts du paquet
sed -i 's/\r$//' "$STAGE/DEBIAN/"* "$STAGE/usr/lib/nanosound-oled/oled_display.py" "$STAGE/lib/systemd/system/nanosound-oled.service"

mkdir -p dist
dpkg-deb --build --root-owner-group "$STAGE" "dist/nanosound-oled_${VERSION}_all.deb"
