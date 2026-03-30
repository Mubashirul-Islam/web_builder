from PIL import Image
from moviepy import VideoFileClip

from website.constants import AssetTypes


class AssetDimensions:
    """A class to get the dimensions of an image or video file."""

    @staticmethod
    def get_dimensions(file_obj, file_type):
        if file_type == AssetTypes.IMAGE:
            return AssetDimensions._get_image_dimensions(file_obj)
        elif file_type == AssetTypes.VIDEO:
            return AssetDimensions._get_video_dimensions(file_obj)

    @staticmethod
    def _get_image_dimensions(file_obj):
        file_obj.seek(0)
        with Image.open(file_obj) as img:
            width, height = img.size
        file_obj.seek(0)
        return width, height

    @staticmethod
    def _get_video_dimensions(file_obj):
        file_obj.seek(0)
        with VideoFileClip(file_obj.temporary_file_path()) as clip:
            width, height = clip.size
        file_obj.seek(0)
        return int(width), int(height)
