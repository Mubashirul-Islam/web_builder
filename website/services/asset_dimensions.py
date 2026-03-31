import os
import tempfile

from PIL import Image
from moviepy import VideoFileClip

from website.constants import AssetTypes


class AssetDimensions:
    """A class to get the dimensions of an image or video file."""

    @staticmethod
    def get_dimensions(file_obj: object, file_type: str) -> tuple[int, int]:
        """Return width and height for a supported image or video upload."""
        if file_type == AssetTypes.IMAGE:
            return AssetDimensions._get_image_dimensions(file_obj)
        elif file_type == AssetTypes.VIDEO:
            return AssetDimensions._get_video_dimensions(file_obj)

        raise ValueError(f"Unsupported asset type '{file_type}'.")

    @staticmethod
    def _get_image_dimensions(file_obj: object) -> tuple[int, int]:
        """Read image dimensions while preserving the file pointer position."""
        file_obj.seek(0)
        with Image.open(file_obj) as img:
            width, height = img.size
        file_obj.seek(0)
        return width, height

    @staticmethod
    def _get_video_dimensions(file_obj: object) -> tuple[int, int]:
        """Return (width, height) of a video without altering file state."""

        file_obj.seek(0)

        temp_path = None

        try:
            # Case 1: File already exists on disk (Django TemporaryUploadedFile)
            if hasattr(file_obj, "temporary_file_path"):
                video_path = file_obj.temporary_file_path()

            # Case 2: In-memory file → write to temp file
            else:
                suffix = os.path.splitext(getattr(file_obj, "name", ""))[1]

                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
                    if hasattr(file_obj, "chunks"):
                        for chunk in file_obj.chunks():
                            temp.write(chunk)
                    else:
                        temp.write(file_obj.read())

                    video_path = temp.name
                    temp_path = video_path  # mark for cleanup

            # Extract dimensions
            with VideoFileClip(video_path) as clip:
                width, height = clip.size

            return int(width), int(height)

        finally:
            file_obj.seek(0)

            # Cleanup temp file if created
            if temp_path:
                try:
                    os.remove(temp_path)
                except FileNotFoundError:
                    pass
