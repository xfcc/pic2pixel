"""
Convert an image to 1-bit pixel art PNG using hitherdither error diffusion.
"""
import os
import sys
from io import BytesIO

# Ensure vendored hitherdither (lib/) is on path when not installed as package
_here = os.path.dirname(os.path.abspath(__file__))
_lib = os.path.join(_here, "lib")
if _lib not in sys.path:
    sys.path.insert(0, _lib)

from PIL import Image
from hitherdither.palette import Palette
from hitherdither.diffusion import error_diffusion_dithering

# 1-bit palette: black and white
ONE_BIT_PALETTE = Palette([(0, 0, 0), (255, 255, 255)])

# Supported algorithm names (must match hitherdither.diffusion._DIFFUSION_MAPS keys)
ALGORITHMS = (
    "floyd-steinberg",
    "atkinson",
    "jarvis-judice-ninke",
    "stucki",
    "burkes",
    "sierra3",
    "sierra2",
    "sierra-2-4a",
)


def convert_to_1bit(
    image_input,
    algorithm="atkinson",
    max_size=None,
    target_size=None,
) -> bytes:
    """
    Convert image to 1-bit dithered PNG.

    :param image_input: PIL Image, file-like object, or bytes of image data.
    :param algorithm: Dithering method (e.g. "atkinson", "floyd-steinberg").
    :param max_size: Optional (width, height) to fit inside (keeps aspect, no crop).
    :param target_size: Optional (width, height) for exact output size (resize + center crop).
    :return: PNG image as bytes.
    """
    if isinstance(image_input, bytes):
        image_input = BytesIO(image_input)

    img = Image.open(image_input).convert("RGB")

    if target_size:
        # Exact size: scale to cover then center-crop
        tw, th = target_size
        if tw < 1 or th < 1:
            target_size = None
        else:
            r = max(tw / img.width, th / img.height)
            new_w = max(1, int(round(img.width * r)))
            new_h = max(1, int(round(img.height * r)))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            x = (new_w - tw) // 2
            y = (new_h - th) // 2
            img = img.crop((x, y, x + tw, y + th))

    if not target_size and max_size and (img.width > max_size[0] or img.height > max_size[1]):
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

    algo = algorithm.lower() if algorithm else "atkinson"
    if algo not in ALGORITHMS:
        algo = "atkinson"

    dithered = error_diffusion_dithering(img, ONE_BIT_PALETTE, method=algo, order=2)

    buf = BytesIO()
    dithered.save(buf, format="PNG")
    return buf.getvalue()
