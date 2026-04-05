# AiMediaWebsite

공식 업데이트 소스를 수집하고, 이를 실무 영향 중심의 해설 콘텐츠로 변환한 뒤, 검수 후 발행하는 도메인 확장형 콘텐츠 운영 플랫폼.

GitHub: https://github.com/xAsh-Ai/AiMediaWebsite

## Local Preview

저장소 루트에서 아래 명령으로 정적 사이트를 미리 볼 수 있다.

```bash
cd <repository-root>
python3 -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 연다.

## Vercel Preview Deploy

현재 퍼블릭 MVP는 정적 HTML 사이트로 운영되므로, preview 배포는 Vercel 기준으로 가장 단순하게 처리한다.

```bash
cd <repository-root>
vercel deploy -y
```

배포 전제:
- `vercel whoami` 가 성공해야 한다.
- 배포 설정은 루트의 [`vercel.json`](./vercel.json) 을 기준으로 한다.
- preview 배포를 기본값으로 두고, production 배포는 별도 판단 후 진행한다.

## Public QA Smoke Pass

퍼블릭 QA는 preview URL을 직접 두드리는 방식보다, 로컬에서 Vercel 라우팅을 재현한 뒤 핵심 경로를 점검하는 흐름을 기본으로 둔다.

```bash
cd <repository-root>
vercel dev --listen 127.0.0.1:4173
```

확인할 핵심 경로:
- `/`
- `/briefs`
- `/categories`
- `/tools`
- `/weekly`
- `/weekly/checklist`
- `/newsletter`
- `/about`
- `/contact`

세부 체크리스트는 [`docs/public-qa-smoke-pass.md`](./docs/public-qa-smoke-pass.md) 를 따른다.

## Documents

| 문서 | 경로 | 역할 |
| --- | --- | --- |
| 제품 기획 | `./AiMediaWebsite.md` | 제품 정의, IA, 운영 엔진과 백오피스의 장기 방향을 정리한 기획서 |
| 수동 발행 절차 | `./docs/manual-publishing-workflow.md` | 인터뷰로 검증된 수동 브리프를 먼저 발행해 MVP를 검증하고, 자동 수집·자동 발행 엔진은 아직 만들지 않는 절차 |
| 엔진 v0 소스 모델 | `./docs/engine-source-registry.md` | 공식 소스 레지스트리, normalize-layer 계약, config와 code의 경계를 정의한 첫 엔진 문서 |
| 초기 소스 레지스트리 | `./engine/source-registry.json` | OpenAI, Anthropic, Cursor, Vercel, Supabase의 초기 공식 소스 인벤토리 |
| 엔진 v0 리뷰/발행 모델 | `./docs/engine-review-publishing-workflow.md` | 상태 모델, 리뷰 룰, publish artifact 관계, 수동/자동 경계를 정의한 워크플로우 문서 |
| 초기 리뷰 룰셋 | `./engine/review-rules.json` | approval 이전에 반드시 통과해야 하는 최소 리뷰 규칙 |
| 초기 상태 모델 | `./engine/workflow-state.json` | `content_job`, `article`, `review_log`, `channel_package`의 상태와 전이 정의 |
| 퍼블릭 웹 기본값 | `./docs/public-web-basics.md` | canonical, robots, sitemap, favicon, social metadata 같은 public-web 기본 정책 |
| ICP·인터뷰 스크립트 | `./docs/icp-outreach-scripts.md` | 초기 ICP 검증과 인터뷰 진행에 쓰는 스크립트와 응답 인사이트 |
| 설계(office-hours) | `external local note` | 구조와 방향성을 보완하는 설계 메모. 현재 레포 바깥 로컬 초안이라 저장소에서는 직접 열리지 않는다. |

## MVP Stage

장기적으로 이 프로젝트는 소스 수집, 정규화, 검수, 발행을 아우르는 운영 엔진과 백오피스를 핵심 자산으로 두는 구조를 목표로 한다. 하지만 현재 단계에서는 그 엔진을 바로 구현하지 않고, 인터뷰로 검증한 수동 브리프 워크플로우와 정적 HTML 셸로 문제-해결 적합성을 먼저 확인하고 있다. 즉 지금의 사이트는 완성형 제품이라기보다, 장기적인 운영 플랫폼 가설을 빠르게 검증하기 위한 MVP 표면이다.
