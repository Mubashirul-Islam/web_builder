import os
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from moviepy import VideoFileClip
from PIL import Image

from website.constants import AssetTypes


class AssetCompression:
    """Compress image and video uploads before persisting them."""

    IMAGE_QUALITY = 75
    VIDEO_BITRATE = "900k"
    AUDIO_BITRATE = "96k"

    @classmethod
    def compress(cls, file_obj: object, file_type: str) -> object:
        """Return a compressed file object for supported asset types."""
        file_obj.seek(0)
        try:
            if file_type == AssetTypes.IMAGE:
                return cls._compress_image(file_obj)
            if file_type == AssetTypes.VIDEO:
                return cls._compress_video(file_obj)
        except Exception:
            # Fallback: return original file on any error
            file_obj.seek(0)
            return file_obj

        raise ValueError(f"Unsupported asset type '{file_type}'.")

    @classmethod
    def _compress_image(cls, file_obj: object) -> object:
        """Compress image uploads while preserving filename and content type."""
        file_obj.seek(0)
        with Image.open(file_obj) as image:
            output = BytesIO()
            fmt = (image.format or "").upper()

            # Convert unsupported modes to RGB for JPEG
            if fmt in {"JPEG", "JPG"}:
                if image.mode in {"RGBA", "P"}:
                    image = image.convert("RGB")
                image.save(output, format="JPEG", optimize=True, quality=cls.IMAGE_QUALITY, progressive=True)
            elif fmt == "PNG":
                image.save(output, format="PNG", optimize=True, compress_level=9)
            elif fmt == "WEBP":
                image.save(output, format="WEBP", quality=cls.IMAGE_QUALITY, method=6)
            elif fmt == "GIF":
                image.save(output, format="GIF", optimize=True)
            else:
                file_obj.seek(0)
                return file_obj  # unsupported format

        compressed_bytes = output.getvalue()
        original_size = getattr(file_obj, "size", 0)
        if original_size and len(compressed_bytes) >= original_size:
            file_obj.seek(0)
            return file_obj

        return SimpleUploadedFile(
            name=getattr(file_obj, "name", "upload.bin"),
            content=compressed_bytes,
            content_type=getattr(file_obj, "content_type", "application/octet-stream"),
        )

    @classmethod
    def _compress_video(cls, file_obj: object) -> object:
        """Compress video uploads and return a replacement file if smaller."""
        file_obj.seek(0)
        input_path, delete_input = cls._prepare_video_path(file_obj)
        suffix = os.path.splitext(getattr(file_obj, "name", ""))[1] or ".mp4"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_out:
            output_path = temp_out.name

        try:
            with VideoFileClip(input_path) as clip:
                clip.write_videofile(
                    output_path,
                    bitrate=cls.VIDEO_BITRATE,
                    audio_bitrate=cls.AUDIO_BITRATE,
                    logger=None,
                )

            compressed_size = os.path.getsize(output_path)
            original_size = getattr(file_obj, "size", 0)
            if original_size and compressed_size >= original_size:
                file_obj.seek(0)
                return file_obj

            with open(output_path, "rb") as f:
                return SimpleUploadedFile(
                    name=getattr(file_obj, "name", "upload.mp4"),
                    content=f.read(),
                    content_type=getattr(file_obj, "content_type", "application/octet-stream"),
                )
        finally:
            file_obj.seek(0)
            if delete_input and input_path:
                try:
                    os.remove(input_path)
                except FileNotFoundError:
                    pass

            try:
                os.remove(output_path)
            except FileNotFoundError:
                pass

    @staticmethod
    def _prepare_video_path(file_obj: object) -> tuple[str, bool]:
        """Return a local path for a video file and whether it should be deleted."""
        if hasattr(file_obj, "temporary_file_path"):
            return file_obj.temporary_file_path(), False

        suffix = os.path.splitext(getattr(file_obj, "name", ""))[1] or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            if hasattr(file_obj, "chunks"):
                for chunk in file_obj.chunks():
                    temp.write(chunk)
            else:
                temp.write(file_obj.read())
            return temp.name, True