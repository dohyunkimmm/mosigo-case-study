# MOSIGO 미병합 브랜치 검토 기록 (2026-10-31)

## 범위

- 저장소: `dohyunkimmm/mosigo-case-study`
- 대상: `main` 외 11개 원격 브랜치, 열린 PR, 사업기획서 HTML/PDF 및 모바일 미리보기 자동화
- 방법: 브랜치별 `main...branch` 비교, 핵심 파일의 버전 대조, 현재 `main`의 페이지·QA 기능 확인
- **주의:** 브랜치에 미병합 커밋이 있다는 사실은 곧 배포 누락을 의미하지 않는다. 로컬 PC의 미커밋 파일은 GitHub API로 확인하지 못한다.

## 검토 결과

| 분류 | 브랜치 | main 대비 미병합 커밋 | 처리 |
|---|---|---:|---|
| 사업기획서 초안 | `business-plan/new-20261031` | 10 | 기존 작성 기준·PDF 생성 방식을 현행 17쪽 본문과 비교. 당시 날짜 표기와 오래된 렌더러는 복원하지 않음 |
| 승인된 사업기획서 수정 | `qa/mosigo-business-plan-approved-fixes-20261031` | 3 | **유효한 가격 구분 2곳만 복원**. 나머지 구버전 템플릿·날짜 및 문서 구조는 복원하지 않음 |
| 이전 Case Study | `case-study/add-notion-original-business-plan-20261031`, `case-study/notion-plan-jd-decision-20261031` | 4 / 1 | 현행 Case Study의 단일 페이지 구성 유지; 옛 PDF 첨부를 무단 복원하지 않음 |
| 과거 다중 페이지 포트폴리오 | `portfolio/decision-memos-20261030`, `portfolio/forecast-management-20261030`, `portfolio/independent-materials-20261030`, `portfolio/inline-analysis-20261030`, `portfolio/native-downloads-20261030`, `portfolio/report-pager-20261030` | 4 / 8 / 6 / 1 / 1 / 1 | 예전 별도 페이지의 핵심 항목은 현재 `/#decision`, `/#business`, `/#attachments`로 통합. 기존 URL 세 개는 호환 리디렉션을 유지 |
| 과거 테스트 변경 | `test/case-study-table-count-20261031` | 1 | 현행 `qa/smoke.mjs`가 더 많은 반응형·문서·시뮬레이터 검사를 수행하므로 옛 테스트로 되돌리지 않음 |

## 실제 반영한 누락

1. `downloads/mosigo_business_plan_20261031.html`: **기본 동행 3만 원대(상품 가정)**와 **평균 40,000원(손익 비교용)**을 구분.
2. 동일 원본의 손익표: `상품가` → `손익 비교용 평균 이용가`.
3. `qa/check-document-design.py`: 원본과 게시 PDF에서 두 구분이 유지되는지 자동 점검.
4. `.github/workflows/business-plan-pdf.yml`: PDF 생성과 동시에 17쪽의 모바일 WebP 미리보기(일반/소형 총 34개)를 함께 갱신. GitHub Actions 봇 커밋이 별도의 푸시 트리거를 실행하지 않을 수 있는 문제 예방.

## 처리하지 않은 작업

- 위 11개 오래된 브랜치를 일괄 병합하거나 삭제하지 않음.
- 기존 제품 데모 `mosigo-nine.vercel.app`에 변경 없음.
- 옛 가격 가정·디자인·분리형 포트폴리오 구조를 현재 운영본에 덮어씌우지 않음.
- 원격 브랜치 비교만으로 로컬 미커밋 변경이 없다고 판단하지 않음.

이 기록은 검토 시점의 스냅샷이다. 작업을 보관하려는 목적이 아니라면 브랜치 삭제 여부는 별도로 결정해야 한다.
