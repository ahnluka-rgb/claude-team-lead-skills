# claude-team-lead-skills

**코드 모르는 팀장이 회사에서 진짜 쓰는 Claude 스킬.** 숫자는 코드가 세고, 결과는 자동으로 검사합니다.
Claude skills a non-developer team lead actually uses at work. Scripts do the counting, and every result is checked automatically.

[한국어](#한국어) · [English](#english)

> ⚠️ 있는 그대로 공개합니다. **질문·요청에는 답하지 않습니다.** 고쳐 쓰는 건 자유예요(MIT).
> Provided as-is. **No support, no issue replies.** Fork and adapt freely (MIT).

---

## 한국어

### 설치 (한 줄)
Claude 코드에서:
```
/plugin marketplace add ahnluka-rgb/claude-team-lead-skills
/plugin install team-lead@claude-team-lead-skills
```
그다음 평소처럼 말로 부르면 됩니다. 예: "팀원_주간보고 폴더 주간보고 한 장으로 합쳐 줘"

### 들어 있는 스킬
| 스킬 | 하는 일 | 이렇게 부르세요 |
|---|---|---|
| **weekly-report** | 팀원마다 양식이 다른 주간보고 엑셀 여러 개 → 한 장. 원본과 자동 대조 | "주간보고 합쳐 줘" |
| **meeting-notes** | 회의 받아쓰기 → 결정·할 일(담당·마감)·미정. 모든 항목에 근거 줄 번호, 지어낸 담당·날짜 자동 검사 | "회의록 정리해 줘" |
| **daily-log** | 노션 업무 표 → 업무일지(아침 계획·저녁 보고·주간·월간). 처음엔 노션 표를 직접 만들어 줌 | "업무일지 세팅해 줘" → "오늘 업무일지 써 줘" |
| 덤: token-saver · ux-writing · backup | 사용량 아끼기 점검표 · 화면 문구 다듬기 · GitHub 비공개 백업 | "사용량 아껴서 해 줘" 등 |

### 실제로 돌려 본 결과 (2026-11-02)
플러그인을 설치한 뒤 새 빈 폴더에서 평소 말투로 한 번씩 부탁했습니다(`claude -p`, Sonnet). 연습 자료마다 3번씩 실행했고, 결과는 정답표로 채점했습니다. 연습 자료는 모두 가짜 회사 자료입니다.

| 스킬 · 연습 자료 | 맞힌 것 (3번 모두) | 검사 | 1회 시간 · 비용 |
|---|---|---|---|
| 주간보고 · 기본 양식 5개 | 5명 · 15건 · 중복 1줄 · 지연 3건 | 원본 16줄 대조 틀린 줄 0 | 약 20초 · 약 0.17달러 |
| 주간보고 · 까다로운 양식 3개 (합친 칸·✅⏳❌·영어·시트 2개·퍼센트) | 3명 · 9건 · 지연 2건 | 원본 9줄 대조 틀린 줄 0 | 약 23초 · 약 0.17달러 |
| 회의록 · 주간회의 33줄 | 결정 3 · 할 일 6 · 미정 2, 함정 2개 피함 | 지어낸 담당·마감 0 | 약 38초 · 약 0.20달러 |
| 회의록 · 미팅 준비 21줄 | 결정 2 · 할 일 4 · 미정 2, 함정 2개 피함 | 지어낸 담당·마감 0 | 약 35초 · 약 0.20달러 |
| 업무일지 · 노션 표 2개 | 아침판: 오늘 할 일 2 · 밀린 일 1 · 진행 중 1 · 다가오는 일 1 | 노션에 저장 확인 | 1번만 시험 |

함정은 이런 것들입니다.
- "텀블러로 가죠" 했다가 나중에 "보류"로 뒤집은 결정
- "제가 할게요, 농담이고"처럼 농담으로 한 담당
- 휴가 때문에 바뀐 담당자
- "날짜는 내일 다시 정해요"처럼 아직 안 정한 마감(날짜를 지어내면 실패)

처음 시험에서 회의록 3번 중 2번이 검사 단계를 건너뛰었습니다. 그래서 스킬을 고친 뒤 다시 3번 돌렸고, 3번 모두 검사까지 했습니다. 업무일지는 노션 커넥터 대신 노션 API로 시험했습니다.

자동 검사 코드(`tests/run_checks.py`, 19개 항목)는 깃허브에서 윈도우·맥·리눅스로 매번 돌아갑니다.

### 연습해 보기
- 주간보고: `skills/weekly-report/sample/make_sample.py` 를 실행하면 가짜 팀원 엑셀 5개가 생깁니다.
- 회의록: `skills/meeting-notes/sample/주간회의_1103.txt`
- 처음이라면 [이틀 설치 계획표](START_HERE.md)를 따라 하세요.

### 준비물
Python 3.9 이상이 필요합니다. 주간보고는 `pip install openpyxl` 도 해야 하고, 업무일지는 Claude 의 Notion 커넥터 연결이 필요합니다.

### 영상으로 보기
유튜브 **안루카의 AI결재함** — 「클로드 왕초보 교실」 재생목록: https://www.youtube.com/playlist?list=PLYnMquSD8WaY

---

## English

### Install
In Claude Code:
```
/plugin marketplace add ahnluka-rgb/claude-team-lead-skills
/plugin install team-lead@claude-team-lead-skills
```

### Skills
| Skill | What it does |
|---|---|
| **weekly-report** | Merges team members' weekly Excel sheets (each in a different format) into one report. A script does the counting, and `check.py` verifies every row against the originals. |
| **meeting-notes** | Turns a transcript into decisions, action items (owner and due date) and open questions. Every item cites line numbers, and `verify.py` rejects any owner or date that isn't in those lines. |
| **daily-log** | Builds daily, weekly and monthly work logs from a Notion task database, and creates the two databases on first run. |
| extras | token-saver checklist, ux-writing review, private GitHub backup |

### Tested (2026-11-02)
I installed the plugin and ran `claude -p` (Sonnet) in fresh folders with plain requests, 3 runs per sample set.
- weekly-report: 3/3 correct on both the basic and the tricky sample sets, with 0 rows mismatched against the originals.
- meeting-notes: 3/3 full marks on two transcripts, with every trap avoided and no owners or dates invented.
- daily-log: the morning log was correct on a test Notion workspace.

Skill bodies are written in Korean. Claude reads them fine and answers in your language. Sample data is from a fictional company.

## License
MIT
