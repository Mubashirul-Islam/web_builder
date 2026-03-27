from PIL import Image
from moviepy import VideoFileClip

from website.models import Asset


class AssetDimensions:
    """A class to get the dimensions of an image or video file."""

    def __init__(self, file_obj, file_type):
        self.file_obj = file_obj
        self.file_type = file_type

    def get_dimensions(self):
        if self.file_type == Asset.AssetType.IMAGE:
            return self.get_image_dimensions()
        elif self.file_type == Asset.AssetType.VIDEO:
            return self.get_video_dimensions()

    def get_image_dimensions(self):
        self.file_obj.seek(0)
        with Image.open(self.file_obj) as img:
            width, height = img.size
        self.file_obj.seek(0)
        return width, height

    def get_video_dimensions(self):
        self.file_obj.seek(0)
        with VideoFileClip(self.file_obj.temporary_file_path()) as clip:
            width, height = clip.size
        self.file_obj.seek(0)
        return int(width), int(height)
