from moviepy import VideoFileClip

def get_video_dimensions(file_obj):
    file_obj.seek(0)
    with VideoFileClip(file_obj.temporary_file_path()) as clip:
        width, height = clip.size
    file_obj.seek(0)
    return int(width), int(height)