from PIL import Image

def get_image_dimensions(file_obj):
    file_obj.seek(0)
    with Image.open(file_obj) as img:
        width, height = img.size
    file_obj.seek(0)
    return width, height