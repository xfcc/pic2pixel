# Pic2Pixel

将图片转换为 1-bit 像素风 PNG 的本地 Web 应用。使用 [hitherdither](https://github.com/hbldh/hitherdither) 与 PIL/Pillow 进行误差扩散抖动。

## 安装

```bash
cd Pic2Pixel
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

项目已内置 `lib/hitherdither` 的精简版本，无需从 GitHub 安装即可运行。若希望使用上游包，可执行：

```bash
pip install git+https://github.com/hbldh/hitherdither.git
```

## 运行

```bash
python app.py
```

浏览器打开：<http://127.0.0.1:5000>

## 使用

1. 点击「选择图片」上传一张图片（支持 PNG、JPG、GIF、WebP，最大 10MB，建议不超过 2000×2000 像素）。
2. 选择抖动算法（默认 Atkinson）。
3. 可选填写「缩小尺寸」的宽、高，转换前会先按比例缩小。
4. 点击「转换为 1-bit」，在右侧查看结果并下载 PNG。

## 项目结构

- `app.py` — Flask 入口与 `/convert` 接口
- `converter.py` — 1-bit 抖动封装（hitherdither + Pillow）
- `templates/index.html` — 单页上传与预览
- `static/` — CSS 与 JS
