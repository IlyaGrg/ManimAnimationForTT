#!/usr/bin/env bash
# Рендер видео из папки videos/<name>/scene.py
#   ./render.sh pythagoras           — финал 1080x1920, 60 fps
#   ./render.sh pythagoras preview   — быстрый превью 540x960, 30 fps
set -euo pipefail
cd "$(dirname "$0")"

name="${1:?Укажи имя папки из videos/, например: ./render.sh pythagoras}"
mode="${2:-final}"
dir="videos/$name"
[[ -f "$dir/scene.py" ]] || { echo "Нет файла $dir/scene.py"; exit 1; }

if [[ "$mode" == "preview" ]]; then
    flags=(-r 540,960 --fps 30)
    out="$dir/${name}_preview.mp4"
else
    flags=()
    out="$dir/$name.mp4"
fi

.venv/bin/manim "${flags[@]}" -a --media_dir "$dir/media" "$dir/scene.py"

latest=$(ls -t "$dir"/media/videos/scene/*/*.mp4 | head -1)
cp "$latest" "$out"
echo "Готово: $out"
