import os
import re
import subprocess
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

import sys

def get_ffmpeg_executable() -> str:
    """Find FFmpeg binary when running from source or frozen in PyInstaller."""
    # 1. Check PyInstaller _MEIPASS bundle
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        candidates = [
            os.path.join(base_dir, "ffmpeg.exe"),
            os.path.join(base_dir, "ffmpeg-win-x86_64-v7.1.exe"),
            os.path.join(base_dir, "imageio_ffmpeg", "binaries", "ffmpeg-win-x86_64-v7.1.exe"),
            os.path.join(base_dir, "imageio_ffmpeg", "binaries", "ffmpeg.exe"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c

    # 2. Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.isfile(exe):
            return exe
    except Exception:
        pass

    # 3. Fallback to system PATH
    return "ffmpeg"


FFMPEG_EXE = get_ffmpeg_executable()


PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif",
    ".heic", ".heif", ".bmp", ".gif"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm",
    ".flv", ".wmv", ".3gp", ".ts", ".mts", ".m2ts"
}


def is_photo(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    return ext in PHOTO_EXTENSIONS


def is_video(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    return ext in VIDEO_EXTENSIONS


def is_supported(path: str) -> bool:
    return is_photo(path) or is_video(path)


def _dms_to_decimal(dms: Any, ref: str) -> Optional[float]:
    """Convert degrees, minutes, seconds tuple or list to decimal degrees."""
    try:
        if isinstance(dms, (tuple, list)) and len(dms) >= 3:
            deg = float(dms[0])
            mins = float(dms[1])
            secs = float(dms[2])
            dec = deg + (mins / 60.0) + (secs / 3600.0)
            if ref.upper() in ["S", "W"]:
                dec = -dec
            return round(dec, 6)
        elif isinstance(dms, (int, float)):
            dec = float(dms)
            if ref.upper() in ["S", "W"]:
                dec = -dec
            return round(dec, 6)
    except Exception:
        pass
    return None


def extract_photo_metadata(path: str) -> Dict[str, Any]:
    """Extract detailed metadata and summary for an image file."""
    result = {
        "type": "photo",
        "has_metadata": False,
        "summary": "No metadata detected",
        "device": {},
        "datetime": {},
        "gps": {},
        "camera": {},
        "raw_tags": {},
    }

    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif or len(exif) == 0:
                # Also check PNG / WebP info dict
                info = {k: v for k, v in img.info.items() if k not in ["jfif", "jfif_version", "jfif_unit", "jfif_density"]}
                if info:
                    result["has_metadata"] = True
                    result["summary"] = f"Embedded chunks ({', '.join(info.keys())})"
                    result["raw_tags"] = {str(k): str(v)[:200] for k, v in info.items()}
                return result

            result["has_metadata"] = True
            tags_summary = []

            # 1. Base tags
            for tag_id, val in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                result["raw_tags"][tag_name] = str(val)

                if tag_name in ["Make", "Model", "Software"]:
                    result["device"][tag_name] = str(val)
                elif tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                    result["datetime"][tag_name] = str(val)

            # 2. Exif IFD (sub-IFD for exposure, lens, etc.)
            try:
                exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                for tag_id, val in exif_ifd.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    result["raw_tags"][tag_name] = str(val)

                    if tag_name in ["DateTimeOriginal", "DateTimeDigitized"] and tag_name not in result["datetime"]:
                        result["datetime"][tag_name] = str(val)
                    elif tag_name in ["ExposureTime", "FNumber", "ISOSpeedRatings", "FocalLength", "LensModel", "LensMake"]:
                        result["camera"][tag_name] = str(val)
            except Exception:
                pass

            # 3. GPS IFD
            try:
                gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
                if gps_ifd:
                    gps_dict = {}
                    for g_id, g_val in gps_ifd.items():
                        g_name = ExifTags.GPSTAGS.get(g_id, str(g_id))
                        gps_dict[g_name] = g_val
                        result["raw_tags"][f"GPS_{g_name}"] = str(g_val)

                    lat = gps_dict.get("GPSLatitude")
                    lat_ref = gps_dict.get("GPSLatitudeRef", "N")
                    lon = gps_dict.get("GPSLongitude")
                    lon_ref = gps_dict.get("GPSLongitudeRef", "E")

                    if lat and lon:
                        dec_lat = _dms_to_decimal(lat, lat_ref)
                        dec_lon = _dms_to_decimal(lon, lon_ref)
                        if dec_lat is not None and dec_lon is not None:
                            result["gps"]["decimal"] = (dec_lat, dec_lon)
                            result["gps"]["display"] = f"{abs(dec_lat):.4f}° {lat_ref}, {abs(dec_lon):.4f}° {lon_ref}"
                            result["gps"]["maps_url"] = f"https://www.google.com/maps?q={dec_lat},{dec_lon}"
                            tags_summary.append("📍 GPS Location")
            except Exception:
                pass

            # Construct summary
            if "Make" in result["device"] or "Model" in result["device"]:
                dev_str = f"{result['device'].get('Make', '')} {result['device'].get('Model', '')}".strip()
                if dev_str:
                    tags_summary.append(dev_str)

            dt = result["datetime"].get("DateTimeOriginal") or result["datetime"].get("DateTime")
            if dt:
                tags_summary.append(str(dt))

            if not tags_summary:
                tags_summary.append(f"{len(result['raw_tags'])} EXIF tags")

            result["summary"] = " • ".join(tags_summary)
            return result
    except Exception as e:
        return {
            "type": "photo",
            "has_metadata": False,
            "summary": f"Could not parse: {str(e)[:50]}",
            "device": {},
            "datetime": {},
            "gps": {},
            "camera": {},
            "raw_tags": {},
        }


def extract_video_metadata(path: str) -> Dict[str, Any]:
    """Extract metadata and stream tags for a video using FFmpeg."""
    result = {
        "type": "video",
        "has_metadata": False,
        "summary": "No metadata detected",
        "tags": {},
        "streams": [],
        "duration": None,
        "raw_tags": {},
    }

    if not os.path.exists(path):
        return result

    try:
        cmd = [FFMPEG_EXE, "-hide_banner", "-i", path]
        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        output = proc.stderr

        # Check for Metadata block
        metadata_lines = []
        is_in_metadata = False
        current_section = "global"

        ignored_keys = {
            "major_brand", "minor_version", "compatible_brands",
            "encoder", "handler_name", "vendor_id"
        }

        user_identifiable_tags = {}
        tags_summary = []

        for line in output.splitlines():
            line_stripped = line.strip()

            if line_stripped.startswith("Duration:"):
                # Parse duration: Duration: 00:01:23.45, start: ...
                dur_match = re.search(r"Duration:\s*([0-9:.]+)", line_stripped)
                if dur_match:
                    result["duration"] = dur_match.group(1)

            if line_stripped.startswith("Metadata:"):
                is_in_metadata = True
                continue

            if is_in_metadata:
                if ":" in line_stripped and not line_stripped.startswith("Stream") and not line_stripped.startswith("Duration"):
                    parts = line_stripped.split(":", 1)
                    k = parts[0].strip()
                    v = parts[1].strip()
                    result["raw_tags"][k] = v

                    if k.lower() not in ignored_keys:
                        user_identifiable_tags[k] = v
                        if k.lower() in ["title", "artist", "album", "comment", "copyright", "make", "model"]:
                            tags_summary.append(f"{k}: {v[:25]}")
                        elif "date" in k.lower() or "creation_time" in k.lower():
                            tags_summary.append(f"Date: {v[:19]}")
                        elif "location" in k.lower() or "gps" in k.lower():
                            tags_summary.append("📍 Location Tag")
                elif line_stripped.startswith("Stream") or line_stripped.startswith("Duration"):
                    is_in_metadata = False

        result["tags"] = user_identifiable_tags
        if user_identifiable_tags:
            result["has_metadata"] = True
            result["summary"] = " • ".join(tags_summary) if tags_summary else f"{len(user_identifiable_tags)} metadata tags"
        else:
            result["summary"] = "Clean / Minimal container tags"

        return result
    except Exception as e:
        return {
            "type": "video",
            "has_metadata": False,
            "summary": f"Video probe error: {str(e)[:40]}",
            "tags": {},
            "streams": [],
            "duration": None,
            "raw_tags": {},
        }


def extract_metadata(path: str) -> Dict[str, Any]:
    """Unified metadata extraction based on file extension."""
    if is_photo(path):
        return extract_photo_metadata(path)
    elif is_video(path):
        return extract_video_metadata(path)
    else:
        return {
            "type": "unknown",
            "has_metadata": False,
            "summary": "Unsupported file format",
            "raw_tags": {},
        }
