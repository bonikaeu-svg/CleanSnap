"""
Cleaner package for stripping EXIF, GPS, camera, and container metadata from photos and videos.
"""
from cleaner.metadata_extractor import (
    extract_metadata,
    extract_photo_metadata,
    extract_video_metadata,
    is_photo,
    is_video,
    is_supported,
)
from cleaner.photo_cleaner import clean_photo
from cleaner.video_cleaner import clean_video
from cleaner.processor import process_single_file, BatchCleanWorker, resolve_output_path

__all__ = [
    "extract_metadata",
    "extract_photo_metadata",
    "extract_video_metadata",
    "is_photo",
    "is_video",
    "is_supported",
    "clean_photo",
    "clean_video",
    "process_single_file",
    "BatchCleanWorker",
    "resolve_output_path",
]
