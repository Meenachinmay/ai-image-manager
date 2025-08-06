from PIL import Image
import io
from typing import Tuple, Optional


def validate_image(image_data: bytes) -> Tuple[bool, Optional[str]]:
    """Validate if the bytes represent a valid image."""
    try:
        image = Image.open(io.BytesIO(image_data))
        image.verify()
        return True, None
    except Exception as e:
        return False, str(e)


def resize_image(image_data: bytes, max_size: Tuple[int, int] = (800, 800)) -> bytes:
    """Resize image if it exceeds max dimensions."""
    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    output = io.BytesIO()
    image.save(output, format=image.format or 'JPEG')
    return output.getvalue()


def get_image_format(image_data: bytes) -> Optional[str]:
    """Get the format of an image."""
    try:
        image = Image.open(io.BytesIO(image_data))
        return image.format
    except Exception:
        return None