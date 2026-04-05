# 문서 진입점 동기화 — 실행 프롬프트

아래 블록 전체를 복사해 에이전트(또는 채팅)에 붙여 넣는다. 목적은 **README 부재·CLAUDE 미갱신·AGENTS 중복**을 한 번에 정리하는 것이다.

---

## 복사용 프롬프트

```
역할: 이 저장소의 문서 진입점을 최신 코드/문서 상태와 맞춘다.

워크스페이스 루트: /Users/mac/project/AiMediaWebsite

해야 할 일 (순서대로, 생략 금지):

1) 저장소 구조 파악
   - 루트의 index.html, briefs/, categories/, tools/, weekly/, assets/, docs/ 를 확인한다.
   - /Users/mac/project/AiMediaWebsite/docs/manual-publishing-workflow.md 내용을 읽고, README에 반영할 한 줄 요약을 뽑는다.

2) README.md 생성 (루트)
   - 파일 경로: /Users/mac/project/AiMediaWebsite/README.md
   - 포함할 것:
     - 프로젝트 한 줄 (AiMediaWebsite.md 첫 섹션과 정합)
     - GitHub 저장소 URL: https://github.com/xAsh-Ai/AiMediaWebsite
     - 로컬에서 정적 사이트 미리보기 방법 (예: `python3 -m http.server` 또는 `npx serve` 중 하나를 고정해 서술)
     - 문서 링크 표 또는 목록 (절대 경로로):
       - 제품 기획: /Users/mac/project/AiMediaWebsite/AiMediaWebsite.md
       - 수동 발행 절차: /Users/mac/project/AiMediaWebsite/docs/manual-publishing-workflow.md
       - ICP·인터뷰 스크립트: /Users/mac/project/AiMediaWebsite/docs/icp-outreach-scripts.md
       - 설계(office-hours): /Users/mac/.gstack/projects/aimediawebsite/mac-unknown-design-20260405-112043.md
     - 현재 MVP 단계 설명 2~4문장: 기획서의 “엔진·백오피스” 장기 목표와, 지금은 **수동 브리프·정적 HTML 셸**로 검증 중이라는 관계를 명시한다.

3) CLAUDE.md 갱신
   - 파일 경로: /Users/mac/project/AiMediaWebsite/CLAUDE.md
   - 기존 Project / Skill routing 섹션은 유지한다.
   - `## Project` 아래에 `## Documentation` (또는 `## Docs`) 섹션을 추가한다.
   - 위 README와 동일한 문서 링크를 절대 경로로 나열하고, 짧게 한 줄씩 역할을 붙인다.
   - 정적 사이트 핵심 경로를 추가한다: `/Users/mac/project/AiMediaWebsite/index.html`, 브리프 허브 `/Users/mac/project/AiMediaWebsite/briefs/index.html`.

4) AGENTS.md 정리
   - 파일 경로: /Users/mac/project/AiMediaWebsite/AGENTS.md
   - 현재 내용이 CLAUDE.md와 완전 중복이면, AGENTS.md는 **에이전트 전용 한 페이지**로 줄인다:
     - 첫 줄에 “자세한 프로젝트 맥락은 CLAUDE.md 참조”
     - CLAUDE.md 절대 경로 링크
     - 이 저장소에서 에이전트가 지켜야 할 규칙만 3~5줄 (예: 수동 발행 시 manual-publishing-workflow 준수, 공식 소스 권위 등은 manual 문서 인용)
   - 중복을 제거해 유지보수 부담을 없앤다.

5) 검증
   - README에 깨진 링크나 존재하지 않는 경로를 넣지 않는다.
   - 변경 후 `git diff`로 변경 파일만 확인한다.

6) 커밋
   - 메시지 예: `docs: add README and sync CLAUDE/AGENTS entry points`
   - 사용자가 원하면 push까지 하되, 원격은 사용자 확인 후.

제약: 새 기능 코드나 HTML 디자인 변경은 하지 않는다. 문서 파일만 추가·수정한다.
```

---

## 완료 기준 (체크리스트)

- [ ] `/Users/mac/project/AiMediaWebsite/README.md` 존재
- [ ] `CLAUDE.md`에 Documentation 섹션과 정적 사이트 경로
- [ ] `AGENTS.md`가 CLAUDE와 무의미 중복이 아님
- [ ] MVP 단계(기획 vs 현재 구현)가 한 문단으로라도 설명됨

## 버전

- 2026-04-05: 초안 작성
