"""
Command Line Interface for EXIF & Privacy Metadata Stripper.
"""
import os
import sys
import argparse
from typing import List

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from cleaner.metadata_extractor import extract_metadata, is_supported
from cleaner.processor import process_single_file
from ui.drop_area import scan_paths


def main():
    parser = argparse.ArgumentParser(
        description="Strip all EXIF, GPS, camera, and container metadata from photos and videos."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        nargs="+",
        help="One or more input files or directories"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Destination directory for cleaned files (required when cleaning)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files if they already exist in the output directory"
    )
    parser.add_argument(
        "--keep-icc",
        action="store_true",
        help="Preserve embedded ICC color profile for photos"
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Inspect and print metadata only without modifying or cleaning"
    )

    args = parser.parse_args()

    # Discover files
    files = scan_paths(args.input)
    if not files:
        print("No supported photo or video files found in the specified path(s).")
        sys.exit(1)

    print(f"Found {len(files)} supported file(s).")

    if args.inspect:
        print("\n--- Metadata Inspection ---")
        for f in files:
            meta = extract_metadata(f)
            print(f"\nFile: {os.path.basename(f)}")
            print(f"  Summary: {meta.get('summary', 'None')}")
            if meta.get("gps", {}).get("display"):
                print(f"  📍 GPS: {meta['gps']['display']}")
            for k, v in meta.get("device", {}).items():
                print(f"  📷 {k}: {v}")
            for k, v in meta.get("datetime", {}).items():
                print(f"  📅 {k}: {v}")
            for k, v in meta.get("tags", {}).items():
                print(f"  🎥 {k}: {v}")
        return

    if not args.output:
        print("Error: -o/--output directory is required when cleaning files.")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    print(f"Cleaning files to: {args.output}\n")

    success_cnt = 0
    error_cnt = 0

    for idx, f in enumerate(files, start=1):
        name = os.path.basename(f)
        print(f"[{idx}/{len(files)}] Processing {name}...", end=" ", flush=True)
        res = process_single_file(
            f,
            args.output,
            overwrite=args.overwrite,
            keep_color_profile=args.keep_icc
        )
        if res.get("success"):
            success_cnt += 1
            print("✓ DONE")
        else:
            error_cnt += 1
            print(f"✗ ERROR: {res.get('error')}")

    print(f"\nFinished: {success_cnt} cleaned, {error_cnt} errors.")


if __name__ == "__main__":
    main()
