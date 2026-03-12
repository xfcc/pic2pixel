#!/usr/bin/env bash
# 首次推送到 GitHub：https://github.com/xfcc/pic2pixel
set -e
cd "$(dirname "$0")"

REMOTE="https://github.com/xfcc/pic2pixel.git"
BRANCH="main"

echo ">>> 检查未跟踪/未提交文件..."
git status -s

echo ""
echo ">>> 确保 .gitignore 生效（venv 等不应被提交）..."
git check-ignore -v venv/ 2>/dev/null || true

echo ""
echo ">>> 添加所有项目文件（遵守 .gitignore）..."
git add .
if git diff --cached --quiet; then
  echo "    没有新变更，使用当前提交推送。"
else
  echo "    创建新提交..."
  git commit -m "Sync: Pic2Pixel 1-bit pixel art web app (Flask + hitherdither)"
fi

echo ""
echo ">>> 设置远程仓库并推送..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin "$BRANCH"

echo ""
echo ">>> 推送完成。请打开 https://github.com/xfcc/pic2pixel 确认文件已出现。"
