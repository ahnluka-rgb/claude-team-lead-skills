---
name: backup
description: 프로젝트 폴더를 GitHub 비공개 저장소에 백업하거나, 다른 PC에서 불러온다. 비밀번호·키·개인정보 파일은 올리지 않는다. "백업해줘", "깃허브에 올려줘", "백업 불러와줘" 라고 할 때 사용. / Backs up a project folder to a private GitHub repo (and restores it), never committing secrets.
---

# 백업 — GitHub 비공개 저장소

## 준비물
- `git`, GitHub CLI `gh` (설치 뒤 `gh auth login` 한 번).

## 규칙 (절대 지킬 것)
- 저장소는 항상 **private**. 공개로 만들거나 바꾸지 않는다.
- 비밀번호·API 키·로그인 세션·손님/직원 개인정보·매출 같은 내부자료는 **원본을 커밋하지 않는다.** `.gitignore` 에 넣는다.
- `git push --force` 로 덮어쓰지 않는다.

## 백업해줘
1. **처음이면**(`.git` 없음) 아래 「처음 설정」 먼저.
2. **진행 상황 남기기**: 이번 대화에서 이 프로젝트를 작업했다면, 프로젝트 `CLAUDE.md` 의 `## 진행 상황` 을 갱신한다 — 마지막 작업(날짜, 3~6줄) / 다음 할 일 / 정한 것. 다른 PC의 새 대화가 이것만 읽고 이어 갈 수 있게. 비밀 값·개인정보는 쓰지 않는다.
3. **안전 검사**: `git add -A` 뒤 올라갈 파일에 비밀이 없는지 본다.
   ```bash
   git diff --cached --name-only
   git diff --cached | grep -inE "api[_-]?key|secret|password|token|BEGIN (RSA|OPENSSH) PRIVATE KEY|sk-[a-z0-9]{20}" | head
   ```
   걸리는 게 있으면 커밋하지 말고(`git reset`) 사용자에게 보여 준 뒤 `.gitignore` 에 넣는다. 테스트용 가짜 값이면 그렇다고 설명한다.
4. 바뀐 게 있으면 `git commit -m "백업: YYYY-MM-DD HH:mm"` → `git push`. 없으면 "변경 없음".
   - push 가 거절되면(다른 PC가 먼저 올림): `git pull --no-rebase` 로 받아 합친다. 충돌이 나면 양쪽 내용을 살려 합치고, 한쪽을 버려야 하면 사용자에게 먼저 묻는다.
5. 한 줄로 보고 (커밋됨 / 변경 없음).

## 처음 설정
1. 민감 파일 찾기: `.env*`, `*.pem`, `*.key`, 토큰·쿠키 json, 코드에 박힌 키, 개인정보·내부자료. 애매하면 사용자에게 묻는다.
2. `.gitignore`: 위 민감 파일 + 빌드·캐시(node_modules, .venv, dist, build, __pycache__ 등) + `*.bak`.
3. `git init -b main` → 안전 검사 → 첫 커밋.
4. `gh repo create <폴더이름> --private --source . --push`

## 비밀 파일도 백업하고 싶다면
원본은 올리지 말고 암호화한 사본만 올린다. 예: `age`·`7-Zip(AES-256)` 으로 잠근 파일을 `.vault/` 에 두고 그 폴더만 커밋. 비밀번호를 잃으면 복구할 수 없다는 점을 사용자에게 꼭 알린다. 비밀번호는 대화창으로 받지 않는다.

## 백업 불러와줘 (다른 PC에서 이어서)
1. 폴더가 없으면 `gh repo clone <이름>`. 있으면 `git status` 로 커밋 안 된 변경을 확인 → 있으면 "먼저 백업할까요?" 묻고, 없으면 `git pull`.
2. 의존성 안내: package.json → `npm install`, requirements.txt → 가상환경 만들고 `pip install -r requirements.txt`.
3. `CLAUDE.md` 의 `## 진행 상황` 을 읽고 어디서부터 이어 갈지 한 줄로 말한다.
