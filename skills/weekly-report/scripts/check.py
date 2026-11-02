"""Check a merged weekly report against the original sheets.

Usage: python check.py <report.xlsx>

For every report row, re-opens the original file and confirms the task text in the
recorded row matches. For every original sheet, counts filled task rows and confirms
report rows + removed duplicates add up. Exit code 0 = all good, 1 = mismatch.
"""
import json, os, re, sys
from openpyxl import load_workbook


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip() if s is not None else ""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    report = os.path.abspath(sys.argv[1])
    data = json.load(open(report + ".json", encoding="utf-8"))
    s = data["summary"]
    problems, books = [], {}

    def sheet(fname):
        if fname not in books:
            books[fname] = load_workbook(os.path.join(s["folder"], fname), data_only=True).worksheets[0]
        return books[fname]

    infos = {i["file"]: i for i in s["sheets"]}
    for x in data["rows"] + data["duplicates"]:
        i = infos[x["file"]]
        got = norm(sheet(x["file"]).cell(x["row"], i["task_col"]).value)
        if got != x["task"]:
            problems.append(f'{x["file"]} {x["row"]}행: 원본 "{got}" ≠ 보고서 "{x["task"]}"')

    for f, i in infos.items():
        if not i.get("task_col"):
            problems.append(f"{f}: 업무 칸을 못 찾아 통째로 빠짐")
            continue
        ws = sheet(f)
        src = sum(1 for r in range(i["header_row"] + 1, ws.max_row + 1) if norm(ws.cell(r, i["task_col"]).value))
        used = sum(1 for x in data["rows"] + data["duplicates"] if x["file"] == f)
        if src != used:
            problems.append(f"{f}: 원본 업무 {src}줄인데 보고서에 {used}줄")

    rep = load_workbook(report, data_only=True)["팀원별"]
    if rep.max_row - 1 != len(data["rows"]):
        problems.append(f'보고서 「팀원별」 {rep.max_row - 1}줄 ≠ 기록 {len(data["rows"])}줄')

    total_src = len(data["rows"]) + len(data["duplicates"])
    result = {"ok": not problems, "source_rows": total_src, "report_rows": len(data["rows"]),
              "duplicates_removed": len(data["duplicates"]), "problems": problems}
    print(json.dumps(result, ensure_ascii=False, indent=1))
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
