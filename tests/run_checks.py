"""Run all script checks (no Claude needed). Usage: python tests/run_checks.py"""
import datetime, json, os, subprocess, sys, tempfile
from openpyxl import Workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WR = os.path.join(ROOT, "skills", "weekly-report")
PY = sys.executable
fails = []
sys.stdout.reconfigure(encoding="utf-8")


def run(*args):
    p = subprocess.run([PY, *args], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return p.returncode, p.stdout


def expect(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


print("[weekly-report] practice data")
exp = json.load(open(os.path.join(ROOT, "tests", "expected.json"), encoding="utf-8"))["weekly_report"]
with tempfile.TemporaryDirectory() as tmp:
    run(os.path.join(WR, "sample", "make_sample.py"))
    src = os.path.join(WR, "sample", "팀원_주간보고")
    out = os.path.join(tmp, "report.xlsx")
    code, txt = run(os.path.join(WR, "scripts", "merge.py"), src, "-o", out)
    s = json.loads(txt)
    expect(code == 0, "merge.py runs")
    expect(s["people"] == exp["people"] and s["tasks"] == exp["tasks"], f'5명·15건 (got {s["people"]}·{s["tasks"]})')
    expect(s["status"] == exp["status"], f'상태 개수 {s["status"]}')
    expect(s["duplicates"] == exp["duplicates"], "중복 1줄 제거")
    expect(sorted(x.split(":")[0] for x in s["late"]) == exp["late_people"], "지연·막힘 3건")
    code, txt = run(os.path.join(WR, "scripts", "check.py"), out)
    expect(code == 0 and json.loads(txt)["ok"], "check.py: 원본과 대조 0건 틀림")

print("[weekly-report] odd formats")
with tempfile.TemporaryDirectory() as tmp:
    d = os.path.join(tmp, "in")
    os.makedirs(d)
    wb = Workbook(); ws = wb.active
    ws["A1"] = "10월 4주 업무"
    for c, h in enumerate(["번호", "작업 내용", "진척", "기한"], 1):
        ws.cell(3, c, h)
    for r, row in enumerate([[1, "견적 비교표", "50%", datetime.date(2026, 10, 30)],
                             [2, "사은품 발주", "보류", None], [3, "", "", None], [4, "세금계산서 발행", "끝", None]], 4):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v)
    wb.save(os.path.join(d, "김과장 주간보고 최종.xlsx"))
    wb = Workbook(); ws = wb.active
    ws.append(["진척도 체크", "결과"]); ws.append(["포장재 샘플", "완료"])
    wb.save(os.path.join(d, "윤사원.xlsx"))
    out = os.path.join(tmp, "r.xlsx")
    code, txt = run(os.path.join(WR, "scripts", "merge.py"), d, "-o", out)
    s = json.loads(txt)
    expect(s["status"] == {"진행": 1, "지연·막힘": 1, "완료": 1}, f'%·보류·끝 읽기 {s["status"]}')
    expect(any(p["file"] == "윤사원.xlsx" and p.get("problem") for p in s["problems"]), "모르는 칸은 문제로 알림")
    code, _ = run(os.path.join(WR, "scripts", "check.py"), out)
    expect(code == 1, "빠진 파일이 있으면 check.py 가 실패")
    code, txt = run(os.path.join(WR, "scripts", "merge.py"), d, "-o", out, "--map", "진척도 체크=task,결과=status")
    code2, _ = run(os.path.join(WR, "scripts", "check.py"), out)
    expect(json.loads(txt)["tasks"] == 4 and code2 == 0, "--map 으로 고치면 통과")

print("[weekly-report] hard sample (merged header, emoji, English, 2 sheets, percent cells)")
with tempfile.TemporaryDirectory() as tmp:
    run(os.path.join(WR, "sample", "make_hard_sample.py"))
    out = os.path.join(tmp, "h.xlsx")
    code, txt = run(os.path.join(WR, "scripts", "merge.py"), os.path.join(WR, "sample", "까다로운_주간보고"), "-o", out)
    s = json.loads(txt)
    expect(s["people"] == 3 and s["tasks"] == 9, f'3명·9건 (got {s["people"]}·{s["tasks"]})')
    expect(s["status"] == {"완료": 3, "진행": 3, "지연·막힘": 2, "예정": 1}, f'✅⏳❌·Done/WIP/Blocked·100%/50%/0% {s["status"]}')
    expect(not any(p["unmapped"] for p in s["problems"]), "모든 칸을 읽음")
    expect(any("첫 시트" in p.get("note", "") for p in s["problems"]), "시트가 여러 개면 알려 줌")
    code, _ = run(os.path.join(WR, "scripts", "check.py"), out)
    expect(code == 0, "check.py 통과")

print("[meeting-notes] verify.py")
MN = os.path.join(ROOT, "skills", "meeting-notes")
tr = os.path.join(MN, "sample", "주간회의_1103.txt")
ex = os.path.join(MN, "sample", "주간회의_1103.expected.json")
code, txt = run(os.path.join(MN, "scripts", "verify.py"), tr, os.path.join(ROOT, "tests", "fixtures", "notes_good.json"), "--expected", ex)
expect(code == 0 and json.loads(txt)["score"]["actions"] == "6/6", "맞는 회의록은 통과 (할 일 6/6)")
code, txt = run(os.path.join(MN, "scripts", "verify.py"), tr, os.path.join(ROOT, "tests", "fixtures", "notes_bad.json"), "--expected", ex)
pr = " ".join(json.loads(txt)["problems"])
expect(code == 1 and "수요일" in pr and "11월 5일" in pr, "지어낸 마감 2개를 잡음")
expect(pr.count("함정") == 2, "함정 2개(뒤집힌 결정·농담 담당)를 잡음")
tr2 = os.path.join(MN, "sample", "거래처미팅준비_1105.txt")
ex2 = os.path.join(MN, "sample", "거래처미팅준비_1105.expected.json")
code, txt = run(os.path.join(MN, "scripts", "verify.py"), tr2, os.path.join(ROOT, "tests", "fixtures", "notes2_good.json"), "--expected", ex2)
expect(code == 0, "두 번째 회의(담당 바뀜·마감 미정) 실제 결과가 통과")

print("\nALL OK" if not fails else f"\n{len(fails)} FAILED")
sys.exit(1 if fails else 0)
