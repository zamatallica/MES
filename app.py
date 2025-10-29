import os
import re
import subprocess
from flask import Flask, render_template, send_from_directory, jsonify, request, request
import requests, re
import pyodbc
from dotenv import load_dotenv
import os, requests

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
# Environment variables for database configuration
DATABASE_DRIVER = os.getenv("DATABASE_DRIVER", "ODBC Driver 18 for SQL Server")
DATABASE_SERVER = os.getenv("DATABASE_SERVER")
DATABASE_NAME = os.getenv("DATABASE_NAME", "MES")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")


app = Flask(__name__)

# Build connection string from environment variables
def get_connection_string():
    if not all([DATABASE_SERVER, DATABASE_USERNAME, DATABASE_PASSWORD]):
        raise ValueError("Missing required database environment variables")
    
    return (
        f"DRIVER={{{DATABASE_DRIVER}}};"
        f"SERVER={DATABASE_SERVER};"
        f"DATABASE={DATABASE_NAME};"
        f"UID={DATABASE_USERNAME};"
        f"PWD={DATABASE_PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"APP=MES: Mixtli Entertainment System (1.0)"
    )

def get_connection():
    conn_str = get_connection_string()
    return pyodbc.connect(conn_str)

#  Utility helpers
def db_query(sql, params=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        cols = [column[0] for column in cursor.description]
        results = [dict(zip(cols, row)) for row in cursor.fetchall()]
        return results

def db_exec(sql, params=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        conn.commit()


BASE_DIR = os.path.dirname(__file__)
RETRO_FILE = os.path.join(BASE_DIR, "retro.txt")  # fallback list

ROMS_DIR = os.path.join(BASE_DIR, "ROMS")
COVERS_DIR = os.path.join(BASE_DIR, "static", "covers")

# ----------------------------
# Emulator config (EDIT THESE)
# ----------------------------
# You point each platform to an emulator command.
# For RetroArch cores: retroarch.exe -L core.dll "path\to\rom"
# For standalone (PPSSPP, Dolphin, etc.): just executable "rom"
EMULATORS = {
    "SNES": r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\snes9x_libretro.dll",
    "NES":  r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\nestopia_libretro.dll",
    "GBA":  r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\mgba_libretro.dll",
    "GBC":  r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\gambatte_libretro.dll",
    "GB":   r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\gambatte_libretro.dll",
    "N64":  r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\mupen64plus_next_libretro.dll",
    "PS1":  r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\pcsx_rearmed_libretro.dll",
    "PSP":  r"C:\Emulators\PPSSPP\PPSSPPWindows64.exe",
    "SEGA": r"C:\Emulators\RetroArch\retroarch.exe -L C:\Emulators\RetroArch\cores\genesis_plus_gx_libretro.dll",
    "UNKNOWN": r"C:\Emulators\RetroArch\retroarch.exe"
}

# -------------
# Helpers
# -------------

def guess_platform_from_name(name: str):
    """
    Infer platform from folder names / filename / extensions.
    We match aggressively so you can put ROMS in /ROMS/SNES, /ROMS/GBA, etc.
    """
    lowered = name.lower()

    platform_map = {
        "gba": "GBA",
        "game boy advance": "GBA",
        "gbc": "GBC",
        "game boy color": "GBC",
        " gb ": "GB",
        "game boy": "GB",
        "snes": "SNES",
        "super nintendo": "SNES",
        "super famicom": "SNES",
        "nes": "NES",
        "nintendo entertainment system": "NES",
        "n64": "N64",
        "nintendo 64": "N64",
        "psx": "PS1",
        "ps1": "PS1",
        "playstation": "PS1",
        "psp": "PSP",
        "ppsspp": "PSP",
        "sega": "SEGA",
        "genesis": "SEGA",
        "megadrive": "SEGA",
        "mega drive": "SEGA",
    }

    # check subfolders / tokens first
    for key, plat in platform_map.items():
        if key in lowered:
            return plat

    # extension fallback
    if lowered.endswith(".gba"):
        return "GBA"
    if lowered.endswith(".gbc"):
        return "GBC"
    if lowered.endswith(".gb"):
        return "GB"
    if lowered.endswith(".smc") or lowered.endswith(".sfc"):
        return "SNES"
    if lowered.endswith(".nes"):
        return "NES"
    if lowered.endswith(".z64") or lowered.endswith(".n64") or lowered.endswith(".v64"):
        return "N64"
    if lowered.endswith(".bin") or lowered.endswith(".cue") or lowered.endswith(".img") or lowered.endswith(".iso"):
        # bin/cue could be PS1, iso could be PS1 or PSP
        if "psp" in lowered:
            return "PSP"
        return "PS1"

    return "UNKNOWN"


def normalize_title(raw: str):
    """
    Turn 'Super Metroid (USA) [!].smc' into 'Super Metroid'
    """
    just_name = os.path.basename(raw)
    just_name = re.sub(r"\.[A-Za-z0-9]{1,4}$", "", just_name)          # drop extension
    just_name = re.sub(r"\s*\[[^\]]+\]", "", just_name)                # drop [!], [t1], etc.
    just_name = re.sub(r"\s*\([^)]+\)", "", just_name)                 # drop (USA), (E), etc.
    just_name = re.sub(r"\s{2,}", " ", just_name).strip()              # clean doublespaces
    return just_name


def build_cover_filename(title: str):
    """
    Check /static/covers for a matching cover asset (jpg/png/jpeg).
    Fall back to default.png if not found.
    """
    safe = re.sub(r"[^A-Za-z0-9 _-]", "", title)
    candidates = [
        f"{safe}.jpg",
        f"{safe}.png",
        f"{safe}.jpeg",
    ]
    for c in candidates:
        if os.path.exists(os.path.join(COVERS_DIR, c)):
            return c
    return "default.png"


def scan_roms():
    """
    Walk ROMS_DIR recursively, build structured game list.
    If ROMS_DIR doesn't exist, we fall back to retro.txt.
    """
    games = []

    if os.path.exists(ROMS_DIR):
        for root, _, files in os.walk(ROMS_DIR):
            for f in files:
                ext = f.lower().split(".")[-1]
                # list of extensions we consider "launchable"
                if ext not in [
                    "nes", "smc", "sfc",
                    "gba", "gbc", "gb",
                    "z64", "n64", "v64",
                    "iso", "bin", "img", "cue", "chd",
                    "pbp", "elf", "prx",
                    "zip", "7z"
                ]:
                    continue

                full_path = os.path.join(root, f)
                plat = guess_platform_from_name(root + " " + f)
                title = normalize_title(f)
                cover_file = build_cover_filename(title)

                games.append({
                    "title": title,
                    "platform": plat,
                    "cover": f"/static/covers/{cover_file}",
                    "path": full_path
                })

    # fallback: retro.txt
    if not games and os.path.exists(RETRO_FILE):
        with open(RETRO_FILE, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                raw = line.strip()
                if not raw:
                    continue
                title = normalize_title(raw)
                plat = guess_platform_from_name(raw)
                cover_file = build_cover_filename(title)
                rom_path = os.path.join(os.path.dirname(RETRO_FILE), raw)
                games.append({
                    "title": title,
                    "platform": plat,
                    "cover": f"/static/covers/{cover_file}",
                    "path": rom_path
                })

    # dedupe by (title,platform)
    seen = set()
    deduped = []
    for g in games:
        key = (g["title"].lower(), g["platform"].lower())
        if key not in seen:
            deduped.append(g)
            seen.add(key)

    deduped.sort(key=lambda x: x["title"].lower())
    return deduped


@app.route("/")
def index():
    games = scan_roms()
    return render_template("index.html", games=games)


@app.route("/api/games")
def api_games():
    return jsonify(scan_roms())


@app.route("/covers/<path:filename>")
def covers(filename):
    return send_from_directory(COVERS_DIR, filename)


@app.route("/launch", methods=["POST"])
def launch_game():
    """
    Launch a game using the appropriate emulator.
    We trust this machine (local kiosk). For multi-user LAN
    you'd add auth here.
    """
    data = request.get_json()
    title = data.get("title")
    platform = (data.get("platform") or "UNKNOWN").upper()
    rom_path = data.get("path")

    if not rom_path or not os.path.exists(rom_path):
        return jsonify({"status": "error", "message": "ROM not found"}), 404

    # choose emulator
    base_cmd = EMULATORS.get(platform, EMULATORS["UNKNOWN"])

    # Note: base_cmd may itself contain arguments & core selection.
    # We'll append ROM path quoted.
    full_cmd = f'{base_cmd} "{rom_path}"'

    try:
        subprocess.Popen(full_cmd, shell=True)
        print(f"[Mixtli] Launching {title} ({platform}) -> {rom_path}")
        return jsonify({"status": "ok", "message": f"Launched {title}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/search_ost")
def search_ost():
    import re, requests
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"videoId": None})

    query = f"{title} OST site:youtube.com"
    print(f"🎮 Searching OST for: {query}")

    engines = [
        f"https://html.duckduckgo.com/html/?q={query}",
        f"https://www.google.com/search?q={query}",
        f"https://search.brave.com/search?q={query}"
    ]

    for url in engines:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=6)
            html = resp.text
            match = re.search(r"https://www\.youtube\.com/watch\?v=[\w-]+", html)
            if match:
                video_url = match.group(0)
                video_id = video_url.split("v=")[1]
                print(f"✅ Found OST: {video_id}")
                return jsonify({"videoId": video_id})
        except Exception as e:
            print(f"❌ Failed from {url}: {e}")

    print("🚫 No OST found")
    return jsonify({"videoId": None})

@app.route("/api/roms")
def get_roms():
    sql = """
        SELECT r.RomID, mr.DisplayName, r.YouTubeOST, 
               s.SystemName, s.SystemID
        FROM MESRetroLibrary r
        JOIN MES_Systems s ON r.SystemID = s.SystemID
		JOIN MES_roms mr on r.romID = mr.romid
        ORDER BY s.SystemName, mr.DisplayName
    """
    rows = db_query(sql)
    return jsonify(rows)

@app.route("/search_yt")
def search_yt():
    q = request.args.get("q", "")
    params = {
        "part": "snippet",
        "q": q,
        "maxResults": 5,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }

    resp = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    print("YouTube API response code:", resp.status_code)
    print("Raw text (first 300 chars):", resp.text[:300])

    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        results = []
        for item in items:
            results.append({
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
            })
        return jsonify(results)
    else:
        return jsonify([])  # Always return a list, even if empty



@app.route("/api/save_ost", methods=["POST"])
def save_ost():
    try:
        data = request.get_json(force=True)
        rom_id = data.get("RomID")
        video_id = data.get("YouTubeOST")

        if not rom_id or not video_id:
            return jsonify({"status": "error", "error": "Missing ROM ID or Video ID"}), 400

        sql = """
            UPDATE MESRetroLibrary
            SET YouTubeOST = ?
            WHERE RomID = ?
        """
        db_exec(sql, (video_id, rom_id))

        print(f"✅ Saved OST for ROM {rom_id}: {video_id}")
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error saving OST:", e)
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/cataloguer")
def cataloguer():
    return render_template("cataloguer.html")


if __name__ == "__main__":
    # Run like a living room console dashboard
    app.run(host="0.0.0.0", port=5000, debug=True)
