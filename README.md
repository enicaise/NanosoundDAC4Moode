# OLED Display for MoOde Audio 🎵📟

Afficheur OLED personnalisé pour MoOde Audio avec boutons GPIO pour contrôler la lecture, arrêter ou changer de webradio favorite.
Conçu pour le NanoSound DAC (écran OLED SH1106 en I2C, adresse 0x3C) sur Raspberry Pi 3/4.

## 🚀 Fonctionnalités

- Affichage du titre, artiste, statut (▶, ⏸, ⏹)
- Encodage audio (bitrate) centré
- Message de bienvenue au démarrage
- Boutons GPIO :
  - Lecture/Pause (GPIO13)
  - Stop (GPIO16)
  - Radio suivante (GPIO12)
  - Radio précédente (GPIO11)
  - Extinction (GPIO26)
- Démarrage automatique via systemd

## ✅ Prérequis

- moOde 9.x (Raspberry Pi OS Bookworm), testé avec moOde 9.4.2
- Dans moOde, Configure → Audio : périphérique **HiFiBerry DAC+** (pilote du NanoSound DAC)
- Une playlist MPD nommée **`RADIO`** contenant tes webradios favorites (boutons radio suivante/précédente)
- Un accès SSH au player (utilisateur et mot de passe définis dans Raspberry Pi Imager)

## 📦 Installation (paquet .deb, recommandé)

Sur le player, en SSH :

```bash
wget https://github.com/enicaise/NanosoundDAC4Moode/releases/download/v1.0.0/nanosound-oled_1.0.0_all.deb
sudo apt install ./nanosound-oled_1.0.0_all.deb
sudo reboot
```

Le paquet :

- installe les dépendances par apt (`python3-luma.oled`, `python3-rpi.gpio`, `python3-mpd`, `python3-pil`) ; pas de `pip`
- active l'I2C (`raspi-config`) si ce n'est pas déjà fait — d'où le redémarrage
- installe et démarre le service `nanosound-oled`
- désactive l'ancien service manuel `oled-display` s'il existe (les fichiers de `/var/local/oled_display` peuvent ensuite être supprimés)

### Mises à jour de moOde

Le paquet est indépendant de `moode-player` : les mises à jour de moOde (Configure → System → Software update) ne le touchent pas.
Après une réinstallation complète de moOde (nouvelle carte SD), il suffit de refaire les trois commandes ci-dessus.

### Mettre à jour ou désinstaller l'afficheur

```bash
sudo apt install ./nanosound-oled_<nouvelle-version>_all.deb
sudo apt remove nanosound-oled
```

## 🛠️ Dépannage

```bash
systemctl status nanosound-oled
journalctl -u nanosound-oled -n 30
sudo i2cdetect -y 1   # l'écran doit apparaître en 3c (paquet i2c-tools)
```

## 🏗️ Construire le paquet

Sur une machine Debian/Ubuntu (ou WSL) avec `dpkg-deb` :

```bash
./build-deb.sh          # version lue dans le fichier VERSION
./build-deb.sh 1.0.1    # ou version explicite
```

Le paquet est produit dans `dist/`. Pousser un tag `vX.Y.Z` sur GitHub construit le `.deb` et le publie dans une release (workflow `.github/workflows/release.yml`).

🧾 Licence
MIT — voir le fichier LICENSE
