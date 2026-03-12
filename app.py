"""
Pic2Pixel: Web app to convert images to 1-bit pixel art PNG.
"""
from io import BytesIO

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.exceptions import RequestEntityTooLarge

from converter import convert_to_1bit, ALGORITHMS

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
MAX_PIXELS = 2000 * 2000
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# 限定比例选项：前端显示名 -> (宽比, 高比)，如 16:9 -> (16, 9)
RATIO_OPTIONS = [
    ("", "无"),
    ("1:1", "1:1"),
    ("4:3", "4:3"),
    ("3:2", "3:2"),
    ("16:9", "16:9"),
    ("21:9", "21:9"),
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in ALLOWED_EXTENSIONS


def parse_size_and_ratio():
    """从 request.form 解析 max_width, max_height, ratio，返回 (max_size, target_size)。"""
    ratio_raw = (request.form.get("ratio") or "").strip()
    max_width = request.form.get("max_width", type=int)
    max_height = request.form.get("max_height", type=int)
    max_size = None
    target_size = None
    ratio_w, ratio_h = None, None
    if ratio_raw and ":" in ratio_raw:
        try:
            a, b = ratio_raw.split(":", 1)
            ratio_w, ratio_h = int(a), int(b)
            if ratio_w < 1 or ratio_h < 1:
                ratio_w, ratio_h = None, None
        except (ValueError, TypeError):
            pass
    has_w = max_width and 0 < max_width <= 2000
    has_h = max_height and 0 < max_height <= 2000
    if ratio_w and ratio_h:
        if has_w and has_h:
            target_size = (max_width, max_height)
        elif has_w:
            h = max(1, int(round(max_width * ratio_h / ratio_w)))
            target_size = (max_width, min(h, 2000))
        elif has_h:
            w = max(1, int(round(max_height * ratio_w / ratio_h)))
            target_size = (min(w, 2000), max_height)
    else:
        if has_w and has_h:
            max_size = (max_width, max_height)
    return max_size, target_size


@app.route("/")
def index():
    return render_template(
        "index.html",
        algorithms=ALGORITHMS,
        ratio_options=RATIO_OPTIONS,
    )


@app.route("/convert", methods=["POST"])
def convert():
    if "image" not in request.files:
        return jsonify({"error": "No image file"}), 400

    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, GIF or WebP."}), 415

    try:
        data = file.read()
    except Exception as e:
        return jsonify({"error": "Failed to read file"}), 400

    algorithm = request.form.get("algorithm", "atkinson").strip().lower()
    if algorithm not in ALGORITHMS:
        algorithm = "atkinson"

    max_size, target_size = parse_size_and_ratio()

    try:
        from PIL import Image

        img = Image.open(BytesIO(data))
        w, h = img.size
        if w * h > MAX_PIXELS:
            return jsonify({"error": "Image too large (max 2000×2000 pixels)"}), 413
    except Exception:
        return jsonify({"error": "Invalid or corrupted image"}), 400

    try:
        png_bytes = convert_to_1bit(
            data,
            algorithm=algorithm,
            max_size=max_size,
            target_size=target_size,
        )
    except Exception as e:
        return jsonify({"error": "Conversion failed"}), 500

    return send_file(
        BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=False,
        download_name="pic2pixel.png",
    )


@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return jsonify({"error": "File too large (max 10 MB)"}), 413


if __name__ == "__main__":
    app.run(port=8000, debug=True)
