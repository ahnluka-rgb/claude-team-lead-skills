"""Harder practice data: blank first row + merged header + dates + emoji status, English headers with
two sheets, and Excel percent cells. Run: python make_hard_sample.py -> sample/까다로운_주간보고/"""
import datetime, os, shutil, sys
from openpyxl import Workbook

sys.stdout.reconfigure(encoding="utf-8")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "까다로운_주간보고")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)

wb = Workbook(); ws = wb.active; ws.title = "11월1주"
ws["A2"], ws["C2"], ws["D2"] = "업무 내용", "진행 상황", "완료 예정일"
ws.merge_cells("A2:B2")
for r, (t, st, due) in enumerate([("거래처 연말 인사 메일", "✅", datetime.date(2026, 11, 2)),
                                  ("신규 거래처 계약서 검토", "⏳", datetime.date(2026, 11, 6)),
                                  ("사무실 프린터 교체 견적", "❌", None)], 3):
    ws.cell(r, 1, t); ws.cell(r, 3, st); ws.cell(r, 4, due)
wb.save(os.path.join(D, "2026-11 주간보고_강과장.xlsx"))

wb = Workbook(); ws = wb.active; ws.title = "45주차"
ws.append(["Task", "Status", "Due", "Note"])
ws.append(["Price list update", "Done", "11/3", ""])
ws.append(["Catalog photo shoot", "WIP", "11/5", "half done"])
ws.append(["Supplier contract renewal", "Blocked", "11/7", "waiting for legal"])
old = wb.create_sheet("44주차")
old.append(["Task", "Status"]); old.append(["Old task from last week", "Done"])
wb.save(os.path.join(D, "서주임_week45.xlsx"))

wb = Workbook(); ws = wb.active
ws.append(["할 일", "진행률", "비고"])
for t, p in [("반품 송장 정리", 1), ("재고 엑셀 정리", 0.5), ("연말 사은품 포장", 0)]:
    ws.append([t, p, ""]); ws.cell(ws.max_row, 2).number_format = "0%"
wb.save(os.path.join(D, "오사원.xlsx"))
print("hard sample ready:", len(os.listdir(D)), "sheets ->", D)
