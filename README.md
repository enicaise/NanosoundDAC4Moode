# OLED Display for MoOde Audio 🎵📟

Afficheur OLED personnalisé pour MoOde Audio avec boutons GPIO pour contrôler la lecture, arrêter ou changer de webradio favorite.

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

## 📦 Installation

### 1. Clone du dépôt

```bash
git clone https://github.com/votre-utilisateur/moode-oled-display.git
cd moode-oled-display
```
### 2. Copie des fichiers
```bash
sudo cp -r oled_display /var/local/
sudo cp systemd/oled-display.service /etc/systemd/system/
```
### 3. Activation du service
```bash
sudo systemctl daemon-reexec
sudo systemctl enable oled-display.service
sudo systemctl start oled-display.service
```

🔧 Dépendances
- Python 3
- python3-pip
- RPi.GPIO
- luma.oled
- mpd (en local via MoOde)

🧾 Licence
MIT — voir le fichier LICENSE
