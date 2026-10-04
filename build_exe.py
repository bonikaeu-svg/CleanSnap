"""
Automated PyInstaller build script for CleanSnap.exe
"""
import os
import sys
import shutil
import subprocess
import imageio_ffmpeg

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")

# Get FFmpeg exe
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Bundling FFmpeg binary: {ffmpeg_exe}")

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name", "CleanSnap",
    "--noconsole",
    "--onefile",
    "--icon", os.path.join(PROJECT_ROOT, "app_icon.ico"),
    "--add-data", f"{os.path.join(PROJECT_ROOT, 'app_icon.png')};.",
    "--add-data", f"{ffmpeg_exe};.",
    "--collect-all", "pillow_heif",
    "--collect-all", "imageio_ffmpeg",
    "--collect-all", "PyQt6",
    "--noconfirm",
    "--clean",
    os.path.join(PROJECT_ROOT, "app.py")
]

print("Running PyInstaller with arguments:")
print(" ".join(cmd))

res = subprocess.run(cmd)
if res.returncode == 0:
    target_exe = os.path.join(DIST_DIR, "CleanSnap.exe")
    if os.path.exists(target_exe):
        sz_mb = os.path.getsize(target_exe) / (1024 * 1024)
        print("\n==========================================")
        print(f"🎉 Build SUCCESSFUL!")
        print(f"Executable created: {target_exe}")
        print(f"File Size: {sz_mb:.2f} MB")
        print("==========================================\n")
    else:
        print("Error: Dist output exe not found.")
else:
    print(f"Build failed with exit code {res.returncode}")
    sys.exit(res.returncode)
