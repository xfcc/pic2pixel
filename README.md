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
2. 选择抖动算法（默认 Atkinson），详见下方「抖动算法」说明。
3. 可选填写「缩小尺寸」：可设「限定比例」后只填宽或只填高；或宽高都填（不按比例时按最大边约束，按比例时按设定比例输出）。
4. 点击「转换为 1-bit」，在右侧查看结果并下载 PNG。

## 抖动算法

本项目使用误差扩散（error diffusion）将灰度/彩色图量化为黑白两色，不同算法在颗粒感与细节之间取舍不同。

| 算法 | 说明 |
|------|------|
| **Floyd-Steinberg** | 1976 年提出，最常用。误差向 4 个邻像素扩散（7/16、3/16、5/16、1/16），效果细腻，偶有“虫纹”感。 |
| **Atkinson** | 苹果 Bill Atkinson 提出，仅扩散约 75% 误差，保留细节较好，高光/暗部略有损失。默认推荐。 |
| **Jarvis-Judice-Ninke** | 与 Floyd-Steinberg 同期，误差向 12 个邻像素扩散，颗粒更粗、伪影更少，略糊。 |
| **Stucki** | Jarvis-Judice-Ninke 的变体，计算更轻、结果更干净锐利。 |
| **Burkes** | Stucki 的简化版，速度更快，细腻度略逊。 |
| **Sierra3** | Sierra 系列，基于 Jarvis 思路，在速度与质量之间折中。 |
| **Sierra2** | 两行扩散的 Sierra 变体，比 Sierra3 更轻量。 |
| **Sierra-2-4A** | 最简 Sierra 变体，扩散范围小，速度最快、颗粒感最明显。 |

## 项目结构

- `app.py` — Flask 入口与 `/convert` 接口
- `converter.py` — 1-bit 抖动封装（hitherdither + Pillow）
- `templates/index.html` — 单页上传与预览
- `static/` — CSS 与 JS
