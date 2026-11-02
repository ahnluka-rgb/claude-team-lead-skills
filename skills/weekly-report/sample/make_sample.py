"""Practice data: 5 team members of a fictional office-supply company, each with their own sheet format.
Run: python make_sample.py  -> creates sample/팀원_주간보고/*.xlsx (all names invented)."""
import os, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
from openpyxl import Workbook
from openpyxl.styles import Font

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "팀원_주간보고")
shutil.rmtree(A, ignore_errors=True)
os.makedirs(A)

people = {
    "박대리": dict(cols=["업무", "상태", "마감", "비고"], rows=[
        ["볼펜 불량 원인 확인 (공급사 회신)", "완료", "10/24", "잉크 배합 문제, 교환 500개"],
        ["11월 재고 실사 양식", "완료", "10/27", "품목 412개"],
        ["거래처 미수금 정리", "진행중", "10/31", "3곳 남음"],
        ["볼펜 불량 원인 확인 (공급사 회신)", "완료", "10/24", ""],      # duplicate row on purpose
    ]),
    "이주임": dict(cols=["날짜", "한 일", "진행", "다음 주"], rows=[
        ["2026-10-21", "신학기 기획전 상세페이지 시안 2종", "80%", "할인율 확정 후 수정"],
        ["2026-10-23", "복사용지 견적 3곳 수집", "100%", "비교표 작성"],
        ["2026-10-24", "인스타 기획전 예고 게시물", "늦어짐", "디자인 외주 회신 대기"],   # delay written differently
    ]),
    "최사원": dict(cols=["구분", "내용", "상태"], rows=[
        ["거래처", "한빛오피스 결제 지연 통화", "진행"],
        ["거래처", "미래필기 신규 단가표 받기", "완료"],
        ["내부", "택배 박스 재고 주문", "지연"],
    ]),
    "정대리": dict(cols=["No", "업무명", "완료여부", "막힌 점"], rows=[
        [1, "B2B 견적 요청 응대 7건", "O", ""],
        [2, "카탈로그 가격표 갱신", "X", "단가 3% 인상 반영 대기"],
        [3, "반품 입고 검수", "O", ""],
    ]),
    "한사원": dict(cols=["업무", "상태", "메모"], rows=[
        ["상품 사진 20컷 보정", "완료", ""],
        ["쇼핑몰 상품명 정리 (오타 수정)", "진행중", "절반 완료"],
        ["고객 문의 답변 템플릿", "시작 전", "다음 주 착수"],
    ]),
}
for i, (name, d) in enumerate(people.items()):
    wb = Workbook()
    ws = wb.active
    ws.title = "이번주" if i % 2 else "Sheet1"
    r0 = 1
    if name in ("이주임", "정대리"):          # some people put a title row on top
        ws.cell(1, 1, f"{name} 주간 업무 (10/20~10/24)").font = Font(bold=True)
        r0 = 3
    for c, h in enumerate(d["cols"], 1):
        ws.cell(r0, c, h).font = Font(bold=True)
    for r, row in enumerate(d["rows"], r0 + 1):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v)
    fname = [f"{name}_주간업무.xlsx", f"주간보고_{name}_1024.xlsx", f"{name} 이번주.xlsx", f"{name}-weekly.xlsx", f"주간_{name}.xlsx"][i]
    wb.save(os.path.join(A, fname))

print("sample ready:", len(os.listdir(A)), "sheets ->", A)
