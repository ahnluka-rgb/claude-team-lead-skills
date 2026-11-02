#!/bin/bash
# Real end-to-end runs: fresh folder + plugin loaded + plain request, 3 times per skill.
# Usage: bash tests/live/run_live.sh <work_dir> [model]
# Uses the installed plugin; set PLUGIN_DIR=<repo> to load from a folder instead.
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
W="$1"; MODEL="${2:-sonnet}"
mkdir -p "$W"
export PYTHONIOENCODING=utf-8
for i in 1 2 3; do
  d="$W/wr$i"; rm -rf "$d"; mkdir -p "$d"
  cp -r "$REPO/skills/weekly-report/sample/팀원_주간보고" "$d/"
  ( cd "$d" && claude -p "팀원_주간보고 폴더에 있는 팀원들 주간보고 엑셀을 한 장으로 합쳐 줘." \
      ${PLUGIN_DIR:+--plugin-dir "$PLUGIN_DIR"} --model "$MODEL" --permission-mode auto --output-format json > run.json 2> err.txt )
  d="$W/mn$i"; rm -rf "$d"; mkdir -p "$d"
  cp "$REPO/skills/meeting-notes/sample/주간회의_1103.txt" "$d/"
  ( cd "$d" && claude -p "주간회의_1103.txt 회의록 정리해 줘." \
      ${PLUGIN_DIR:+--plugin-dir "$PLUGIN_DIR"} --model "$MODEL" --permission-mode auto --output-format json > run.json 2> err.txt )
done
echo done
