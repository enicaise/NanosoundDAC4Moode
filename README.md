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
