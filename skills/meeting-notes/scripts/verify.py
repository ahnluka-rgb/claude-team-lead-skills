"""Verify meeting notes JSON against the transcript (no made-up owners, dates or lines).

Usage:
  python verify.py <transcript.txt> <notes.json> [--expected <expected.json>]

notes.json shape:
  {"decisions": [{"text": "...", "lines": [12]}],
   "actions":   [{"task": "...", "owner": "이름 or 미정", "due": "말한 그대로 or 미정", "lines": [4, 5]}],
   "open":      [{"text": "...", "lines": [14]}],
   "next_agenda": ["..."]}
Exit 0 = every item is backed by its lines (and matches expected, if given).
"""
import json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
exp_path = args[args.index("--expected") + 1] if "--expected" in args else None
lines = open(args[0], encoding="utf-8").read().splitlines()
notes = json.load(open(args[1], encoding="utf-8"))
problems, n = [], len(lines)


def ev(item, label):
    ls = item.get("lines") or []
    bad = [l for l in ls if not isinstance(l, int) or not 1 <= l <= n]
    if not ls or bad:
        problems.append(f"{label}: 근거 줄 번호가 없거나 범위 밖 {ls}")
        return ""
    return "\n".join(lines[l - 1] for l in ls)


for k in ("decisions", "actions", "open"):
    if not isinstance(notes.get(k), list):
        problems.append(f'"{k}" 목록이 없음')

for i, d in enumerate(notes.get("decisions", []), 1):
    ev(d, f"결정 {i}")
for i, a in enumerate(notes.get("actions", []), 1):
    text = ev(a, f"할 일 {i}")
    owner, due = (a.get("owner") or "").strip(), (a.get("due") or "").strip()
    if not owner or not due:
        problems.append(f'할 일 {i}: 담당·마감은 비우지 말고 모르면 "미정"')
    if text and owner and owner != "미정" and owner not in text:
        problems.append(f'할 일 {i}: 담당 "{owner}" 가 근거 줄에 없음 (지어냈을 수 있음)')
    if text and due and due != "미정":
        toks = [t for t in re.split(r"[\s,()/·]+", due) if len(t) >= 2 and t not in ("까지", "전까지", "안에", "중으로")]
        if toks and not any(t.rstrip("까지") in text for t in toks):
            problems.append(f'할 일 {i}: 마감 "{due}" 이 근거 줄에 없음 (지어냈을 수 있음)')
for i, o in enumerate(notes.get("open", []), 1):
    ev(o, f"미정 {i}")

score = None
if exp_path:
    exp = json.load(open(exp_path, encoding="utf-8"))
    dec_txt = [d.get("text", "") for d in notes.get("decisions", [])]
    hit_d = sum(any(any(k in t for k in e["keywords"]) for t in dec_txt) for e in exp["decisions"])
    hit_a, acts = 0, notes.get("actions", [])
    for e in exp["actions"]:
        if any(a.get("owner") == e["owner"] and any(k in a.get("task", "") for k in e["keywords"]) for a in acts):
            hit_a += 1
        else:
            problems.append(f'빠진 할 일: {e["owner"]} — {e["keywords"][0]}')
    open_txt = " ".join(o.get("text", "") for o in notes.get("open", []))
    hit_o = sum(any(k in open_txt for k in ks) for ks in exp["open"])
    for t in exp["traps"]:
        if "decision_must_not_match" in t and any(re.search(t["decision_must_not_match"], x) for x in dec_txt):
            problems.append(f'함정에 걸림: {t["why"]}')
        if "action_owner_for" in t:
            kw, who = t["action_owner_for"]
            if any(kw in a.get("task", "") and a.get("owner") != who for a in acts):
                problems.append(f'함정에 걸림: {t["why"]}')
        if "action_due_must_be_undecided" in t:
            kw = t["action_due_must_be_undecided"][0]
            if any(kw in a.get("task", "") and not re.search(r"미정|다시 정|추후|내일", a.get("due", "")) for a in acts):
                problems.append(f'함정에 걸림: {t["why"]}')
    extra = max(0, len(acts) - len(exp["actions"]))
    score = {"decisions": f'{hit_d}/{len(exp["decisions"])}', "actions": f'{hit_a}/{len(exp["actions"])}',
             "open": f'{hit_o}/{len(exp["open"])}', "extra_actions": extra}

print(json.dumps({"ok": not problems, "score": score, "problems": problems}, ensure_ascii=False, indent=1))
sys.exit(0 if not problems else 1)
