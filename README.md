# AiMediaWebsite

공식 업데이트 소스를 수집하고, 이를 실무 영향 중심의 해설 콘텐츠로 변환한 뒤, 검수 후 발행하는 도메인 확장형 콘텐츠 운영 플랫폼.

GitHub: https://github.com/xAsh-Ai/AiMediaWebsite

## Local Preview

저장소 루트에서 아래 명령으로 정적 사이트를 미리 볼 수 있다.

```bash
cd /Users/mac/project/AiMediaWebsite
python3 -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 연다.

## Documents

| 문서 | 경로 | 역할 |
| --- | --- | --- |
| 제품 기획 | `/Users/mac/project/AiMediaWebsite/AiMediaWebsite.md` | 제품 정의, IA, 운영 엔진과 백오피스의 장기 방향을 정리한 기획서 |
| 수동 발행 절차 | `/Users/mac/project/AiMediaWebsite/docs/manual-publishing-workflow.md` | 인터뷰로 검증된 수동 브리프를 먼저 발행해 MVP를 검증하고, 자동 수집·자동 발행 엔진은 아직 만들지 않는 절차 |
| ICP·인터뷰 스크립트 | `/Users/mac/project/AiMediaWebsite/docs/icp-outreach-scripts.md` | 초기 ICP 검증과 인터뷰 진행에 쓰는 스크립트와 응답 인사이트 |
| 설계(office-hours) | `/Users/mac/.gstack/projects/aimediawebsite/mac-unknown-design-20260405-112043.md` | 구조와 방향성을 보완하는 설계 메모 |

## MVP Stage

장기적으로 이 프로젝트는 소스 수집, 정규화, 검수, 발행을 아우르는 운영 엔진과 백오피스를 핵심 자산으로 두는 구조를 목표로 한다. 하지만 현재 단계에서는 그 엔진을 바로 구현하지 않고, 인터뷰로 검증한 수동 브리프 워크플로우와 정적 HTML 셸로 문제-해결 적합성을 먼저 확인하고 있다. 즉 지금의 사이트는 완성형 제품이라기보다, 장기적인 운영 플랫폼 가설을 빠르게 검증하기 위한 MVP 표면이다.
