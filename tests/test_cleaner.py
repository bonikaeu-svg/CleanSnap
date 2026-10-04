import os
import unittest
from PIL import Image
from PIL.ExifTags import Base, GPS

from cleaner.metadata_extractor import (
    extract_metadata,
    extract_photo_metadata,
    extract_video_metadata,
    is_photo,
    is_video
)
from cleaner.photo_cleaner import clean_photo
from cleaner.video_cleaner import clean_video
from cleaner.processor import process_single_file, resolve_output_path


class TestMetadataCleaner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        cls.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(cls.test_dir, exist_ok=True)
        os.makedirs(cls.output_dir, exist_ok=True)

        # 1. Create photo with EXIF + GPS
        cls.photo_path = os.path.join(cls.test_dir, "test_photo.jpg")
        img = Image.new("RGB", (150, 150), color="crimson")
        exif = img.getexif()
        exif[Base.Make] = "Nikon"
        exif[Base.Model] = "Z8"
        exif[Base.DateTime] = "2026:01:01 12:00:00"
        gps_ifd = {
            GPS.GPSLatitudeRef: "N",
            GPS.GPSLatitude: (48.0, 51.0, 29.0),
            GPS.GPSLongitudeRef: "E",
            GPS.GPSLongitude: (2.0, 17.0, 40.0),
        }
        exif[Base.GPSInfo] = gps_ifd
        img.save(cls.photo_path, exif=exif)

        # 2. Path to video fixture
        cls.video_path = os.path.join(cls.test_dir, "test_video.mp4")

    def test_photo_extraction(self):
        meta = extract_metadata(self.photo_path)
        self.assertTrue(meta["has_metadata"])
        self.assertEqual(meta["type"], "photo")
        self.assertIn("Nikon", meta["summary"])
        self.assertIn("GPS", meta["summary"])

    def test_photo_cleaning(self):
        out_path = os.path.join(self.output_dir, "test_photo_cleaned.jpg")
        res = clean_photo(self.photo_path, out_path)
        self.assertTrue(res["success"])
        self.assertTrue(os.path.exists(out_path))

        # Verify EXIF is completely gone
        post_meta = extract_metadata(out_path)
        self.assertFalse(post_meta["has_metadata"])
        self.assertEqual(post_meta["device"], {})
        self.assertEqual(post_meta["gps"], {})

    def test_video_extraction(self):
        if os.path.exists(self.video_path):
            meta = extract_metadata(self.video_path)
            self.assertTrue(meta["has_metadata"])
            self.assertEqual(meta["type"], "video")
            self.assertIn("title", meta["tags"])

    def test_video_cleaning(self):
        if os.path.exists(self.video_path):
            out_path = os.path.join(self.output_dir, "test_video_cleaned.mp4")
            res = clean_video(self.video_path, out_path)
            self.assertTrue(res["success"])
            self.assertTrue(os.path.exists(out_path))

            post_meta = extract_metadata(out_path)
            # Verify container tags are stripped
            self.assertFalse(post_meta["has_metadata"])
            self.assertEqual(post_meta["tags"], {})

    def test_process_single_file(self):
        res = process_single_file(self.photo_path, self.output_dir, overwrite=True)
        self.assertTrue(res["success"])
        self.assertTrue(res.get("verified_clean"))

    def test_resolve_output_path(self):
        p1 = resolve_output_path(self.photo_path, self.output_dir, overwrite=True)
        self.assertEqual(os.path.basename(p1), "test_photo.jpg")

        # Test deduplication when file exists
        existing = os.path.join(self.output_dir, "sample.jpg")
        with open(existing, "w") as f:
            f.write("test")
        p2 = resolve_output_path(existing, self.output_dir, overwrite=False)
        self.assertEqual(os.path.basename(p2), "sample_clean.jpg")


if __name__ == "__main__":
    unittest.main()
