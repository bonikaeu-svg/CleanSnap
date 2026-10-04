import os
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from cleaner.metadata_extractor import is_photo, is_video, extract_metadata
from cleaner.photo_cleaner import clean_photo
from cleaner.video_cleaner import clean_video


def resolve_output_path(
    input_path: str,
    output_dir: str,
    overwrite: bool = False
) -> str:
    """Generate a clean output destination file path."""
    base_name = os.path.basename(input_path)
    root, ext = os.path.splitext(base_name)
    target_path = os.path.join(output_dir, base_name)

    if overwrite or not os.path.exists(target_path):
        return target_path

    # If already exists and not overwrite, append _clean
    counter = 1
    new_name = f"{root}_clean{ext}"
    target_path = os.path.join(output_dir, new_name)

    while os.path.exists(target_path):
        new_name = f"{root}_clean_{counter}{ext}"
        target_path = os.path.join(output_dir, new_name)
        counter += 1

    return target_path


def process_single_file(
    input_path: str,
    output_dir: str,
    overwrite: bool = False,
    keep_color_profile: bool = False
) -> Dict[str, Any]:
    """Process a single photo or video and verify metadata removal."""
    out_path = resolve_output_path(input_path, output_dir, overwrite=overwrite)

    # Pre-extract metadata for logging
    pre_meta = extract_metadata(input_path)

    if is_photo(input_path):
        res = clean_photo(input_path, out_path, keep_color_profile=keep_color_profile)
    elif is_video(input_path):
        res = clean_video(input_path, out_path)
    else:
        return {
            "success": False,
            "error": "Unsupported file format",
            "input_path": input_path,
            "output_path": out_path
        }

    res["input_path"] = input_path
    res["pre_metadata"] = pre_meta

    if res.get("success"):
        # Post-verification to confirm all metadata is gone
        post_meta = extract_metadata(out_path)
        res["post_metadata"] = post_meta
        res["verified_clean"] = not post_meta.get("has_metadata", False)

    return res


class BatchCleanWorker(QThread):
    """Asynchronous background worker to clean files in batch without freezing the GUI."""

    file_started = pyqtSignal(int, str)             # (index, file_path)
    file_finished = pyqtSignal(int, dict)           # (index, result_dict)
    overall_progress = pyqtSignal(int, int)         # (current, total)
    batch_finished = pyqtSignal(dict)               # summary dict
    log_emitted = pyqtSignal(str, str)              # (message, level: 'info'|'success'|'warning'|'error')

    def __init__(
        self,
        file_items: List[Dict[str, Any]],
        output_dir: str,
        overwrite: bool = False,
        keep_color_profile: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.file_items = file_items
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.keep_color_profile = keep_color_profile
        self._is_cancelled = False

    def cancel(self):
        """Request worker cancellation."""
        self._is_cancelled = True

    def run(self):
        total = len(self.file_items)
        success_count = 0
        error_count = 0
        total_orig_bytes = 0
        total_cleaned_bytes = 0

        self.log_emitted.emit(f"🚀 Starting batch cleaning of {total} file(s)...", "info")
        self.log_emitted.emit(f"📁 Output directory: {self.output_dir}", "info")

        for index, item in enumerate(self.file_items):
            if self._is_cancelled:
                self.log_emitted.emit("⚠️ Batch cleaning cancelled by user.", "warning")
                break

            input_path = item["path"]
            file_name = os.path.basename(input_path)

            self.file_started.emit(index, input_path)
            self.log_emitted.emit(f"Processing ({index + 1}/{total}): {file_name}", "info")

            try:
                result = process_single_file(
                    input_path,
                    self.output_dir,
                    overwrite=self.overwrite,
                    keep_color_profile=self.keep_color_profile
                )
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e),
                    "input_path": input_path,
                    "output_path": ""
                }

            if result.get("success"):
                success_count += 1
                orig_b = result.get("original_size", 0)
                clean_b = result.get("cleaned_size", 0)
                total_orig_bytes += orig_b
                total_cleaned_bytes += clean_b

                pre_summary = result.get("pre_metadata", {}).get("summary", "Metadata")
                self.log_emitted.emit(
                    f"✓ Cleaned: {file_name} (Stripped: {pre_summary})",
                    "success"
                )
            else:
                error_count += 1
                err_msg = result.get("error", "Unknown error")
                self.log_emitted.emit(f"✗ Failed: {file_name} — {err_msg}", "error")

            self.file_finished.emit(index, result)
            self.overall_progress.emit(index + 1, total)

        summary = {
            "total": total,
            "processed": success_count + error_count,
            "success": success_count,
            "errors": error_count,
            "cancelled": self._is_cancelled,
            "total_orig_bytes": total_orig_bytes,
            "total_cleaned_bytes": total_cleaned_bytes,
            "output_dir": self.output_dir
        }

        self.log_emitted.emit(
            f"🎉 Completed: {success_count} cleaned, {error_count} errors.",
            "success" if error_count == 0 else "warning"
        )
        self.batch_finished.emit(summary)
