import os
import shutil
from typing import Dict, Any, Optional
from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass


def clean_photo(
    input_path: str,
    output_path: str,
    keep_color_profile: bool = False
) -> Dict[str, Any]:
    """
    Remove all EXIF, GPS, IPTC, XMP, and device metadata from an image.
    Bakes orientation into pixels before stripping EXIF so the image
    remains right side up.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    tmp_output = output_path + ".tmp"

    orig_size = os.path.getsize(input_path)

    try:
        with Image.open(input_path) as img:
            # 1. Correct orientation according to EXIF before stripping
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass  # Keep going even if transpose fails

            orig_format = img.format if img.format else None
            ext = os.path.splitext(output_path)[1].lower()

            # Determine format
            format_map = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".webp": "WEBP",
                ".tif": "TIFF",
                ".tiff": "TIFF",
                ".bmp": "BMP",
                ".gif": "GIF",
                ".heic": "HEIF",
                ".heif": "HEIF",
            }
            save_format = format_map.get(ext, orig_format or "JPEG")

            # 2. Extract ICC profile if requested
            icc_profile = None
            if keep_color_profile:
                icc_profile = img.info.get("icc_profile")

            # 3. Create a clean image object devoid of any attached metadata
            # Handle color modes
            mode = img.mode
            if save_format == "JPEG" and mode not in ("RGB", "L"):
                # JPEG does not support RGBA or P transparency
                clean_img = Image.new("RGB", img.size, (255, 255, 255))
                if mode in ("RGBA", "LA"):
                    clean_img.paste(img, mask=img.split()[-1])
                else:
                    clean_img.paste(img.convert("RGB"))
            else:
                clean_img = Image.new(mode, img.size)
                clean_img.paste(img)

            save_args = {}
            if icc_profile:
                save_args["icc_profile"] = icc_profile

            if save_format == "JPEG":
                save_args["quality"] = 96
                save_args["subsampling"] = 0
                save_args["optimize"] = True
            elif save_format == "PNG":
                save_args["optimize"] = True
            elif save_format == "WEBP":
                save_args["quality"] = 96
                save_args["method"] = 6
            elif save_format == "HEIF":
                save_args["quality"] = 95

            # Save clean image
            clean_img.save(tmp_output, format=save_format, **save_args)

        # Atomic rename
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
