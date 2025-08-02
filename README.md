# 🐍 Snake Game

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.1.2+-green.svg)](https://www.pygame.org/news)

The most feature-packed Snake game you'll ever play! A modern reimagining of the classic arcade game with stunning visuals, multiple game modes, power-ups, and deep customization options.

![Gameplay Screenshot](screenshot.png) <!-- Add a screenshot later -->

## ✨ Features

### 🎮 Game Modes
| Mode        | Description                                  | Challenge Level |
|-------------|----------------------------------------------|-----------------|
| **Classic** | Traditional snake experience                 | Casual          |
| **Time Attack** | Score as much as possible in 3 minutes   | Speedrun        |
| **Survival** | 3 lives against increasing obstacles     | Hardcore        |
| **Campaign** | Complete challenging levels with objectives | Progressive     |

### 🍎 Food System (15+ Types)
| Type        | Effect                      | Value | Visual Cue           | Sound Effect |
|-------------|-----------------------------|-------|----------------------|--------------|
| Normal      | +1 point, +1 length         | +1    | Green apple          | `eat.wav`    |
| Golden      | +5 points, +1 coin          | +5    | Sparkling gold       | `coin.wav`   |
| Speed       | 10s speed boost             | +2    | Blue lightning bolt  | `powerup.wav`|
| Shield      | Temporary protection        | +3    | Blue force field     | `powerup.wav`|
| Rainbow     | 2x score multiplier         | +10   | Color cycling        | `special.wav`|
| Poison      | -1 length                   | -1    | Skull icon           | `negative.wav`|

### 🛠️ Customization Options
- **Visuals**:
  - 15+ unlockable snake skins (Fire, Ice, Rainbow, Neon, etc.)
  - 6 dynamic background themes
  - Adjustable grid visibility
  - Particle effects toggle

- **Gameplay**:
  - 3 difficulty levels (Easy/Normal/Hard)
  - Control schemes (Arrow keys or WASD)
  - Adjustable game speed

- **Audio**:
  - Separate volume controls for music/sounds
  - 8-bit soundtrack with multiple tracks
  - Contextual sound effects

### ⚡ Technical Highlights
- 60FPS smooth gameplay with delta timing
- Advanced particle effects system
- Combo scoring system (up to 10x)
- Persistent save data (high scores, unlocks)
- Responsive input handling
- Dynamic screen scaling

## 🚀 Installation & Quick Start

### Requirements
- Python 3.8 or newer
- Pygame 2.1.2+ (`pip install pygame`)
- Assets folder with:
  - `/fonts/RetroGaming.ttf` (or other retro font)
  - `/sounds/` (see sound files table below)
  - `/music/` (background tracks)
