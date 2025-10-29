# 🎮 Mixtli Entertainment System (MES)

A comprehensive **retro gaming entertainment system** that combines game launching, OST cataloguing, and a beautiful retro-inspired interface.

<p align="center">
  <img src="https://img.shields.io/badge/Theme-Retro%2520Gaming-00ffd9?style=for-the-badge" alt="Theme Badge">
  <img src="https://img.shields.io/badge/Flask-2.3.3-000?style=for-the-badge&logo=flask" alt="Flask Badge">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge">
</p>

---

## 🕹️ Overview

**Mixtli Entertainment System (MES)** is a full-featured retro gaming platform that provides:

- 🎞️ **Game Library Browser:** Beautiful carousel interface for browsing ROM collections  
- 🎵 **OST Cataloguer:** Link YouTube soundtracks to your games  
- 🧩 **Multi-Platform Support:** SNES, NES, GBA, PS1, N64, and more  
- 🧠 **Authentic Retro Experience:** CRT effects, scanlines, and pixel-perfect aesthetics  

---

## ⚙️ Features

### 🧭 Core System
- **Game Carousel:** Smooth scrolling interface with platform badges  
- **Multi-Emulator Support:** Configurable emulators per platform  
- **Auto-Detection:** Automatic platform detection from filenames  
- **Gamepad Support:** Full controller compatibility  
- **Boot Sequence:** Authentic startup animation  

### 🎧 OST Cataloguer
- **YouTube Integration:** Search and link game soundtracks  
- **Visual Management:** Track linked OSTs with icons  
- **Manual Entry:** Direct YouTube video ID input  
- **Live Previews:** Embedded player for previews  
- **Database Backed:** Persistent storage for OST links  

### 🌈 Retro Aesthetic
- **CRT Effects:** Authentic scanlines and curvature  
- **Animated Backgrounds:** Floating pixels and retro sprites  
- **Glowing UI Elements:** Neon accents and pulsing animations  
- **8-bit Typography:** “Press Start 2P” font throughout  
- **Sound Effects:** Authentic retro feedback  

---

## 🧰 Installation

### 🔧 Prerequisites
- Python **3.8+**  
- SQL Server (for database)  
- Retro emulators installed on your system  

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/mixtli-entertainment-system.git
cd mixtli-entertainment-system
```

### 2️⃣ Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Environment Configuration
Create a `.env` file:
```env
# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here

# Database Configuration
DATABASE_DRIVER=ODBC Driver 18 for SQL Server
DATABASE_SERVER=your-server-name,port
DATABASE_NAME=MES
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
```

### 4️⃣ Emulator Configuration
Ensure your SQL Server is running and update the .env file with your database credentials:

- DATABASE_SERVER: Your SQL Server instance (e.g., localhost,1433 or server-name,port)

- DATABASE_USERNAME: Database username

- DATABASE_PASSWORD: Database password

- DATABASE_NAME: Database name (default: MES)

- DATABASE_DRIVER: ODBC driver name (default: ODBC Driver 18 for SQL Server)

### 5️⃣ Directory Structure
```
mixtli/
├── ROMS/           # Game ROMs by platform
├── static/
│   ├── covers/     # Game cover art
│   ├── bg/         # Background music
│   └── sfx/        # Sound effects
├── templates/
└── app.py
```

---

## 🚀 Usage

### Launch the System
```bash
python app.py
```
App available at [http://localhost:5000](http://localhost:5000)

### Main Interface
- Navigate with arrow keys or gamepad  
- Press **Enter/A** to launch games  
- OST auto-plays when linked  

### OST Cataloguer
- Browse ROM library  
- Search or manually link OSTs  
- Preview YouTube tracks  
- Visual checkmarks for linked games  

---

## 🎮 Controls

| Key | Action |
|:---:|:-------|
| ← / → | Navigate carousel |
| Enter | Launch selected game |
| Shift + M | Toggle background music |
| Escape | Clear selection (cataloguer) |

**Gamepad:**  
- **D-pad/Left Stick:** Navigate  
- **A Button:** Launch  
- **B Button:** Back/Exit  

---

## 🧱 Project Structure
```
mixtli/
├── app.py
├── cataloguer.html
├── index.html
├── style.css
├── script.js
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── static/
    ├── covers/
    ├── bg/
    │   ├── Mii-Channel-Plaza.mp3
    │   └── 02_ShopChannel.mp3
    └── sfx/
        ├── boot.mp3
        ├── move.mp3
        └── launch.mp3
```

---

## 🛠️ Configuration

### Supported Platforms
SNES · NES · GBA · GBC · GB · N64 · PS1 · PSP · SEGA Genesis

### File Extensions
| Platform | Extensions |
|-----------|-------------|
| NES | `.nes` |
| SNES | `.smc`, `.sfc` |
| GBA | `.gba` |
| GBC | `.gbc` |
| GB | `.gb` |
| N64 | `.z64`, `.n64`, `.v64` |
| PS1 | `.bin`, `.cue`, `.img`, `.iso` |
| PSP | `.iso`, `.pbp` |
| SEGA | various |

### Cover Art
Place in `static/covers/`  
Naming: `Game Title.jpg` or `Game Title.png`  
Fallback: `default.png`

---

## 🧩 API Endpoints

### 🎮 Game Management
- `GET /api/games` — Retrieve game list  
- `GET /api/roms` — Retrieve ROMs  
- `POST /launch` — Launch game  

### 🎵 OST Management
- `GET /search_yt?q=query` — Search YouTube for OSTs  
- `POST /api/save_ost` — Save OST link  
- `GET /search_ost?title=name` — Retrieve OST  

### 🗂️ Static Files
- `GET /static/*` — Serve assets  
- `GET /covers/*` — Serve covers  

---

## 🎼 OST Cataloguer Highlights

### Workflow
1. Select ROM from library  
2. Search or manually input YouTube ID  
3. Preview and save link  
4. Linked ROMs marked visually  

### Visuals
- Animated pixel backgrounds  
- Live video previews  
- Retro audio cues  
- Keyboard shortcuts (`Shift+M` for audio)  

---

## 🧯 Troubleshooting

### Common Issues

#### ❌ Games Not Launching
- Verify emulator paths  
- Check ROM permissions  
- Ensure emulator is installed  

#### 🎧 OST Search Not Working
- Validate YouTube API key  
- Ensure valid 11-char video IDs  

#### 🔇 Audio Issues
- Browser autoplay may block audio  
- Check music paths and formats  

#### 💾 Database Connection
- Validate SQL Server credentials  
- Confirm ODBC driver installation  

### Performance Tips
- Organize ROMs per platform  
- Optimize cover art (360×240px)  
- Use compressed ROM formats  

---

## 🤝 Contributing

### Development Workflow
```bash
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

### Code Standards
- Maintain retro aesthetic  
- Test cross-browser  
- Add inline comments  

### Feature Requests
Open an issue describing:
- Use case  
- Expected behavior  
- Design considerations  

---

## 📜 License
Licensed under the **MIT License** — see the `LICENSE` file for details.

---

## 🙏 Acknowledgments
- Retro gaming community  
- YouTube API developers  
- Flask framework  
- “Press Start 2P” font creators  
- Emulator developers and maintainers  

---

<div align="center">

❤️ Made with love for the retro gaming community  
🎮 *Keep the classics alive!*  

</div>
