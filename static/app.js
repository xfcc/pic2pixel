(function () {
  const form = document.getElementById('convert-form');
  const imageInput = document.getElementById('image');
  const submitBtn = document.getElementById('submit-btn');
  const messageEl = document.getElementById('message');
  const originalPreview = document.getElementById('original-preview');
  const resultPreview = document.getElementById('result-preview');
  const downloadLink = document.getElementById('download-link');

  function showMessage(text, type) {
    messageEl.textContent = text;
    messageEl.className = 'message ' + (type || 'error');
    messageEl.hidden = false;
  }

  function hideMessage() {
    messageEl.hidden = true;
  }

  function setPlaceholder(el, text) {
    el.innerHTML = '<span class="placeholder">' + (text || '—') + '</span>';
  }

  imageInput.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) {
      setPlaceholder(originalPreview, '选择图片后显示预览');
      return;
    }
    const url = URL.createObjectURL(file);
    originalPreview.innerHTML = '<img src="' + url + '" alt="原图预览">';
    resultPreview.innerHTML = '';
    downloadLink.hidden = true;
    hideMessage();
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const file = imageInput.files[0];
    if (!file) {
      showMessage('请先选择一张图片。');
      return;
    }

    submitBtn.disabled = true;
    hideMessage();
    setPlaceholder(resultPreview, '转换中…');

    const formData = new FormData();
    formData.append('image', file);
    formData.append('algorithm', document.getElementById('algorithm').value);
    const ratio = document.getElementById('ratio').value;
    if (ratio) formData.append('ratio', ratio);
    const maxWidth = document.getElementById('max_width').value;
    const maxHeight = document.getElementById('max_height').value;
    if (maxWidth) formData.append('max_width', maxWidth);
    if (maxHeight) formData.append('max_height', maxHeight);

    try {
      const res = await fetch('/convert', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = data.error || '转换失败（' + res.status + '）';
        showMessage(msg);
        setPlaceholder(resultPreview, '');
        return;
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      resultPreview.innerHTML = '<img src="' + url + '" alt="1-bit 结果">';
      downloadLink.href = url;
      downloadLink.download = 'pic2pixel.png';
      downloadLink.hidden = false;
      showMessage('转换完成，可下载 PNG。', 'success');
    } catch (err) {
      showMessage('请求失败，请检查网络或稍后重试。');
      setPlaceholder(resultPreview, '');
    } finally {
      submitBtn.disabled = false;
    }
  });

  setPlaceholder(originalPreview, '选择图片后显示预览');
  setPlaceholder(resultPreview, '');
})();
