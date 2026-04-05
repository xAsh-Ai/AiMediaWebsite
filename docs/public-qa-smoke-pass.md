# Public QA Smoke Pass

`Issue #10` 의 목적은 현재 정적 퍼블릭 MVP를 실제 public URL로 배포할 준비를 끝내고, 핵심 경로를 smoke pass 수준에서 확인하는 것이다.

## Local Route Check

Vercel 라우팅과 동일한 기준으로 아래 명령으로 로컬 preview를 띄운다.

```bash
cd /Users/mac/project/AiMediaWebsite
vercel dev --listen 127.0.0.1:4173
```

## Core Routes

| Route | 목적 |
| --- | --- |
| `/` | 홈, 핵심 CTA, latest briefs / weekly / public MVP surface 진입점 |
| `/briefs` | 듀얼 트랙 브리프 허브 |
| `/categories` | 카테고리 탐색 허브 |
| `/tools` | 툴 아카이브 허브 |
| `/weekly` | 주간 운영 데스크 |
| `/weekly/checklist` | practical checklist |
| `/newsletter` | retention surface |
| `/about` | 편집 기준 / 신뢰 surface |
| `/contact` | feedback / correction surface |

## Smoke Pass Checklist

- 모든 핵심 경로가 200으로 열린다.
- 상단 내비게이션에서 현재 페이지가 올바르게 표시된다.
- footer 링크가 `briefs / weekly / newsletter / about / contact` 세트를 유지한다.
- 홈 CTA가 `newsletter / about / contact` 로 연결된다.
- 주요 페이지에서 CSS / JS / 폰트 경로가 깨지지 않는다.
- 모바일 폭에서도 메뉴 토글과 주요 버튼이 접근 가능하다.

## Notes

- preview URL 검증은 배포 직후 PR 코멘트 또는 작업 로그에 남긴다.
- `favicon`, social metadata, crawlability polish는 `Issue #11` 범위다.
