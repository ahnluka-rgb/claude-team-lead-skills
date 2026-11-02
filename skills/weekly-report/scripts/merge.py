"""Merge team members' weekly Excel sheets (each in its own format) into one report.

Usage:
  python merge.py <folder> [-o report.xlsx] [--map "열이름=task,열이름=status"]

Reads every .xlsx in <folder> (originals are never modified), finds the header row,
maps columns by keyword, normalizes status words, removes exact duplicates, and writes
a new report workbook plus <report>.json (used by check.py). Prints a JSON summary.
"""
import argparse, datetime, json, os, re, sys
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

FIELDS = {
    "task": ["업무명", "업무", "한 일", "한일", "할 일", "내용", "작업", "항목", "task", "item", "todo"],
    "status": ["완료여부", "진행상태", "진행률", "진척", "상태", "진행", "결과", "status", "progress"],
    "due": ["마감", "기한", "예정일", "완료일", "일정", "날짜", "일자", "due", "date", "deadline"],
    "note": ["막힌 점", "막힌점", "이슈", "비고", "메모", "다음 주", "다음주", "코멘트", "note", "memo", "comment"],
    "category": ["구분", "분류", "category"],
    "skip": ["no", "no.", "번호", "순번", "#"],
}
STATUS = [  # (label, exact words, substrings)
    ("지연·막힘", {"x", "✕", "×", "❌", "🔴"}, ["지연", "늦어", "밀림", "보류", "막힘", "블락", "block", "delay", "hold"]),
    ("완료", {"o", "○", "◯", "v", "✓", "✔", "✅", "⭕", "완", "100%", "done"}, ["완료", "끝", "마감함", "complete"]),
    ("예정", {"0%"}, ["시작 전", "시작전", "예정", "착수 전", "미착수", "todo", "to do", "not started"]),
    ("진행", {"⏳", "🔄", "△", "🟡"}, ["진행", "하는 중", "작업중", "작업 중", "doing", "wip", "in progress"]),
]
NAME_DROP = {"주간", "주간보고", "주간업무", "주간업무보고", "업무", "보고", "보고서", "weekly", "report",
             "이번주", "이번", "주", "최종", "수정", "본", "사본", "복사본", "copy", "xlsx"}


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip() if s is not None else ""


def field_of(header):
    h = norm(header).lower()
    if not h:
        return None
    for f, words in FIELDS.items():
        if h in words:
            return f
    for f, words in FIELDS.items():
        if f != "skip" and any(w in h for w in words if len(w) > 1):
            return f
    return None


def status_of(raw):
    s = norm(raw).lower()
    if not s:
        return "확인 필요"
    m = re.fullmatch(r"(\d{1,3})\s*%", s)
    f = re.fullmatch(r"(0(\.\d+)?|1(\.0+)?)", s)  # Excel percent cells come in as 0~1
    if m or f:
        n = int(m.group(1)) if m else round(float(s) * 100)
        return "완료" if n >= 100 else "예정" if n == 0 else "진행"
    for label, exact, subs in STATUS:
        if s in exact or any(w in s for w in subs):
            return label
    return "확인 필요"


def person_of(path, ws):
    stem = os.path.splitext(os.path.basename(path))[0]
    for tok in re.split(r"[_\-\s()\[\].]+", stem):
        t = tok.strip()
        if t and t.lower() not in NAME_DROP and not re.fullmatch(r"\d+", t):
            return t
    title = norm(ws.cell(1, 1).value)
    return title.split()[0] if title else stem


def find_header(ws, overrides):
    best = None
    for r in range(1, min(ws.max_row, 10) + 1):
        cells = [norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
        filled = [c for c in cells if c]
        if len(filled) < 2:
            continue
        mapping = {}
        for c, v in enumerate(cells, 1):
            f = overrides.get(v) or field_of(v)
            if f and f != "skip" and f not in mapping:
                mapping[f] = c
        if "task" in mapping:
            return r, mapping, cells
        if best is None:
            best = (r, mapping, cells)
    return best if best else (None, {}, [])


def read_sheet(path, overrides):
    wb = load_workbook(path, data_only=True, read_only=False)
    ws = wb.worksheets[0]
    person = person_of(path, ws)
    hr, mapping, headers = find_header(ws, overrides)
    info = {"file": os.path.basename(path), "sheet": ws.title, "person": person,
            "header_row": hr, "columns": {f: headers[c - 1] for f, c in mapping.items()},
            "task_col": mapping.get("task"), "unmapped": []}
    if len(wb.worksheets) > 1:
        info["note"] = f"시트 {len(wb.worksheets)}개 중 첫 시트 「{ws.title}」만 읽음 — 다른 시트가 이번 주면 알려 주세요"
    rows = []
    if not hr or "task" not in mapping:
        info["problem"] = "업무 칸을 찾지 못함 — --map 으로 알려 주세요"
        return info, rows
    info["unmapped"] = [h for c, h in enumerate(headers, 1) if h and c not in mapping.values()
                        and field_of(h) != "skip"]
    for r in range(hr + 1, ws.max_row + 1):
        task = norm(ws.cell(r, mapping["task"]).value)
        if not task:
            continue
        get = lambda f: norm(ws.cell(r, mapping[f]).value) if f in mapping else ""
        due = ws.cell(r, mapping["due"]).value if "due" in mapping else None
        if isinstance(due, (datetime.date, datetime.datetime)):
            due = due.strftime("%m/%d")
        cat = get("category")
        rows.append({"person": person, "task": task, "task_shown": f"[{cat}] {task}" if cat else task,
                     "status_raw": get("status"), "status": status_of(get("status")),
                     "due": norm(due), "note": get("note"), "file": info["file"], "row": r})
    return info, rows


def write_report(out, rows, dups, infos, summary):
    wb = Workbook()
    ws = wb.active
    ws.title = "요약"
    bold, head = Font(bold=True), PatternFill("solid", fgColor="E8ECF2")
    ws["A1"] = f"주간보고 통합 ({summary['made']})"
    ws["A1"].font = Font(bold=True, size=14)
    lines = [("팀원", summary["people"]), ("업무(중복 제거)", summary["tasks"]),
             ("완료", summary["status"].get("완료", 0)), ("진행", summary["status"].get("진행", 0)),
             ("예정", summary["status"].get("예정", 0)), ("지연·막힘", summary["status"].get("지연·막힘", 0)),
             ("확인 필요", summary["status"].get("확인 필요", 0)), ("중복으로 뺀 줄", len(dups))]
    for i, (k, v) in enumerate(lines, 3):
        ws.cell(i, 1, k).font = bold
        ws.cell(i, 2, v)
    r = len(lines) + 4
    for title, items in (("지연·막힘 (먼저 볼 것)", [x for x in rows if x["status"] == "지연·막힘"]),
                         ("확인 필요 (상태를 못 읽음)", [x for x in rows if x["status"] == "확인 필요"]),
                         ("중복으로 뺀 줄", dups)):
        ws.cell(r, 1, title).font = bold
        r += 1
        if not items:
            ws.cell(r, 1, "없음")
            r += 1
        for x in items:
            ws.cell(r, 1, x["person"])
            ws.cell(r, 2, x["task_shown"])
            ws.cell(r, 3, " / ".join(v for v in (x["status_raw"], x["note"]) if v))
            r += 1
        r += 1
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 44
    ws.column_dimensions["C"].width = 40

    t = wb.create_sheet("팀원별")
    cols = ["팀원", "업무", "상태", "원래 적은 상태", "마감", "메모", "원본 파일", "원본 행"]
    for c, h in enumerate(cols, 1):
        cell = t.cell(1, c, h)
        cell.font, cell.fill = bold, head
    for i, x in enumerate(rows, 2):
        vals = [x["person"], x["task_shown"], x["status"], x["status_raw"], x["due"], x["note"], x["file"], x["row"]]
        for c, v in enumerate(vals, 1):
            t.cell(i, c, v).alignment = Alignment(vertical="top", wrap_text=c in (2, 6))
        if x["status"] == "지연·막힘":
            t.cell(i, 3).font = Font(bold=True, color="C0392B")
    for c, w in zip("ABCDEFGH", (10, 42, 10, 14, 10, 34, 26, 8)):
        t.column_dimensions[c].width = w
    t.freeze_panes = "A2"
    t.auto_filter.ref = f"A1:H{max(len(rows) + 1, 2)}"
    wb.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("-o", "--out")
    ap.add_argument("--map", default="", help='예: "한 일=task,진척=status"')
    a = ap.parse_args()
    overrides = dict(p.split("=", 1) for p in a.map.split(",") if "=" in p)
    folder = os.path.abspath(a.folder)
    out = os.path.abspath(a.out or folder.rstrip("\\/") + "_통합.xlsx")
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".xlsx") and not f.startswith("~$"))
    infos, rows, dups, seen = [], [], [], {}
    for f in files:
        p = os.path.join(folder, f)
        if os.path.abspath(p) == out:
            continue
        info, rs = read_sheet(p, overrides)
        infos.append(info)
        for x in rs:
            key = (x["person"], re.sub(r"\s+", "", x["task"]))
            if key in seen:
                dups.append(x)
            else:
                seen[key] = x
                rows.append(x)
    counts = {}
    for x in rows:
        counts[x["status"]] = counts.get(x["status"], 0) + 1
    summary = {"made": datetime.date.today().isoformat(), "folder": folder, "report": out,
               "files": len(infos), "people": len({x["person"] for x in rows}), "tasks": len(rows),
               "status": counts, "duplicates": [f'{x["person"]}: {x["task"]}' for x in dups],
               "late": [f'{x["person"]}: {x["task"]} ({" / ".join(v for v in (x["status_raw"], x["note"]) if v)})'
                        for x in rows if x["status"] == "지연·막힘"],
               "check_needed": [f'{x["person"]}: {x["task"]} ({x["status_raw"]})' for x in rows if x["status"] == "확인 필요"],
               "sheets": infos}
    write_report(out, rows, dups, infos, summary)
    json.dump({"summary": summary, "rows": rows, "duplicates": dups},
              open(out + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "sheets"} |
                     {"problems": [i for i in infos if i.get("problem") or i["unmapped"] or i.get("note")]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
