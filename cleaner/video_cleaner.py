import os
import subprocess
from typing import Dict, Any, Optional

from cleaner.metadata_extractor import FFMPEG_EXE


def clean_video(
    input_path: str,
    output_path: str,
    custom_ffmpeg: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove all global container metadata, stream tags, chapter data,
    creation timestamps, and GPS/location tags from video files.
    Uses lossless stream copying (-c copy) so quality is 100% preserved
    and processing finishes in seconds.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input video not found: {input_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    tmp_output = output_path + ".tmp" + os.path.splitext(output_path)[1]

    orig_size = os.path.getsize(input_path)
    exe = custom_ffmpeg or FFMPEG_EXE

    # FFmpeg command stripping all container & stream metadata
    cmd = [
        exe,
        "-y",
        "-i", input_path,
        "-map_metadata", "-1",
        "-map_chapters", "-1",
        "-c", "copy",
        "-fflags", "+bitexact",
        "-flags:v", "+bitexact",
        "-flags:a", "+bitexact",
        tmp_output
    ]

    try:
        # Hide console window on Windows if subprocess spawned
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            errors="replace"
        )

        if proc.returncode != 0:
            # Fallback without bitexact flags if container doesn't support them
            fallback_cmd = [
                exe,
                "-y",
                "-i", input_path,
                "-map_metadata", "-1",
                "-c", "copy",
                tmp_output
            ]
            proc = subprocess.run(
                fallback_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                errors="replace"
            )
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg failed with code {proc.returncode}: {proc.stderr[-300:]}")

        # Replace destination file atomically
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_output, output_path)

        new_size = os.path.getsize(output_path)
        return {
            "success": True,
            "original_size": orig_size,
            "cleaned_size": new_size,
            "size_diff": new_size - orig_size,
            "output_path": output_path
        }
    except Exception as e:
        if os.path.exists(tmp_output):
            try:
                os.remove(tmp_output)
            except Exception:
                pass
        return {
            "success": False,
            "error": str(e),
            "output_path": output_path
        }
