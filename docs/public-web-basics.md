# Public Web Basics

`Issue #11` 의 목적은 퍼블릭 MVP를 공개 가능한 정적 사이트처럼 보이게 만드는 최소한의 웹 기본값을 닫는 것이다.

## Canonical Posture

- canonical base URL은 현재 public deploy 기준인 `https://aimedia-deploy.vercel.app` 를 사용한다.
- clean URL을 기준으로 canonical을 쓴다.
- 홈은 `/`, 나머지 페이지는 `/briefs`, `/weekly/checklist` 같은 최종 public path를 canonical로 가진다.
- 커스텀 도메인이 붙으면 canonical, `robots.txt`, `sitemap.xml`, OG 이미지 절대 URL을 함께 교체한다.

## Crawlability

- `robots.txt` 는 현재 public MVP 전체를 `Allow: /` 로 둔다.
- `sitemap.xml` 은 현재 퍼블릭 surface 11개 페이지를 포함한다.
- 아직 검색 성장 실험 단계가 아니므로, 우선순위는 색인 차단이 아니라 깨지지 않는 기본 발견 가능성 확보에 둔다.

## Social Metadata

- 모든 퍼블릭 페이지는 title, description, canonical, OG, Twitter card를 가진다.
- 홈과 일반 안내 페이지는 `assets/brand/og-default.svg` 를 사용한다.
- 브리프 템플릿 성격의 페이지는 `assets/brand/og-brief.svg` 를 사용한다.
- 현재는 정적 SVG share card를 쓰고, 추후 커스텀 도메인 또는 실사용 공유 로그가 쌓이면 PNG 카드로 확장할 수 있다.

## Icon Assets

- 루트에 `favicon.svg`, `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` 를 둔다.
- HTML head에서는 icon, shortcut icon, apple touch icon, manifest를 모두 루트 기준으로 연결한다.
- 이 구성이 들어가면 브라우저 기본 `/favicon.ico` 요청도 404 없이 처리된다.
