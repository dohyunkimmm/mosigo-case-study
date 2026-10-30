# MOSIGO — Strategy Case Study

기존 MOSIGO 서비스의 문제 정의, 사업성 가정, 전략적 판단과 검증 계획을 설명하는 **독립형 케이스 스터디**입니다.

- **케이스 스터디:** https://mosigo-case-study.vercel.app/
- **최신 서비스 데모:** https://mosigo-nine.vercel.app/
- **원본 저장소:** https://github.com/dohyunkimmm/mosigo
- **원본 전략기획 자료:** https://app.notion.com/p/40821460c934818581dcfa22dfc3cbef

## 프로젝트 관계

| 목적 | GitHub | Vercel |
| --- | --- | --- |
| 실제 MOSIGO 데모 | `dohyunkimmm/mosigo` | `mosigo` |
| 전략기획 포트폴리오 | `dohyunkimmm/mosigo-case-study` | `mosigo-case-study` |

두 저장소와 배포는 독립적입니다. 케이스 스터디 배포나 수정이 원본 서비스 소스를 변경하지 않습니다.

## 최신 데모 연동 범위

1. **실제 서비스 화면:** 케이스 스터디의 '최신 서비스 데모' 섹션은 `https://mosigo-nine.vercel.app/`를 iframe으로 표시합니다. 따라서 원본 MOSIGO의 같은 주소에 새 버전이 배포되면, 케이스 스터디 방문자가 새로고침할 때 최신 화면을 보게 됩니다. 임베딩을 제한하는 브라우저/사이트 정책이 있는 경우를 위해 '새 창에서 열기' 링크도 제공합니다.
2. **원본 업데이트 메타데이터:** 브라우저가 공개 GitHub API `repos/dohyunkimmm/mosigo/commits/main`과 `raw.githubusercontent.com/dohyunkimmm/mosigo/main/VERSION`을 읽어 `main`의 최근 커밋 날짜·단축 SHA와 소스 버전을 표시합니다. 호출이 실패하면 GitHub 변경 이력 링크로 안내합니다. 이 정보는 **원본 저장소 기준**이며 Production 배포 완료 또는 수동 QA 통과를 뜻하지 않습니다.
3. **전략 콘텐츠:** 시장·고객·재무·KPI·리스크 문장은 **자동으로 다시 작성하지 않습니다**. 원본의 기능 변경과 실제 검증 결과를 확인한 후 이 저장소에서 편집합니다. 실적이나 성공을 임의로 만들지 않습니다.

별도의 토큰, GitHub Actions, 새 Vercel 환경변수 없이 작동합니다. 두 Vercel 프로젝트 모두 GitHub `main`에 대한 자동 배포가 활성화되어 있습니다.

## 디자인 및 접근성

- **본문·제목 폰트:** [Pretendard Variable](https://github.com/orioncactus/pretendard) 동적 서브셋 웹폰트. 미로딩 시 OS 시스템 폰트로 폴백.
- **이모지 아이콘:** [Tossface](https://github.com/toss/tossface) 공식 웹폰트(원본 유지, CDN 호출); [라이선스](https://github.com/toss/tossface/blob/main/LICENSE) 준수. 미로딩 시 시스템 이모지 폴백.
- **인터랙션:** 본문 건너뛰기, 목차 현재 위치, 모바일/넓게 보기 전환(`aria-pressed`), 키보드 포커스 표시, 모션 감소 설정, 모바일 카드 1열/표 가로 스크롤, 설명적 iframe 제목 및 대체 외부 링크.

## 실행과 주의사항

`index.html`을 열면 됩니다. 빌드 과정이 없습니다. 다만 버전·커밋 정보 조회는 온라인 연결과 공개 GitHub API 접근이 필요합니다.

교육 프로젝트에서 분석한 경쟁 앱 7종·리뷰 118건은 원본 조사 범위이며, 원문을 별도로 검증해 재집계한 결과는 아닙니다. 매출, 수요, 원가, 수수료, 사용성 지표와 후속 실행 계획은 가정·제안으로 구분합니다. 실제 의료 서비스·병원 예약·의료 판단·실결제 기능은 제공하지 않습니다.

## QA 체크포인트

- 데스크톱/모바일 목차와 모든 `#` 링크가 실제 섹션에 이동하는지 확인
- 최신 데모 iframe 또는 새 창 링크를 통해 MOSIGO 최신 서비스에 접근 가능한지 확인
- GitHub `main` 변경 정보/버전 로딩 실패 시 안내가 적절한지 확인
- 브라우저에서 Pretendard·Tossface 웹폰트 로딩 및 폴백 확인
- 320/375/768/1280px에서 텍스트 겹침, 가로 스크롤, 대비, 키보드 탐색 확인
- 시나리오 계산기 초기화 및 슬라이더 수치·문구 확인
