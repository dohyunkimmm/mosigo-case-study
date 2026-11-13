# MOSIGO | 병원 동행 서비스 신사업 기획

## 현재 저장소 상태 · 2026-11-14

- 조회 기준: `main` [`aba60ed8`](https://github.com/dohyunkimmm/mosigo-case-study/commit/aba60ed89cf3a667b64b65730e40e8df02c1a264). GitHub 재귀 트리는 **파일 164개·디렉터리 10개**(루트 파일 9개, 최상위 폴더 5개)이며 Git blob SHA가 같은 파일은 **0쌍**입니다. `downloads/` 직접 파일 **9개**(사업기획서 PDF·HTML·PPTX, 서비스기획 PDF·PPTX, IR PDF·PPTX, PRD HTML, 재무 XLSX), `downloads/previews/` WebP **84개**를 확인했습니다.
- [PR #164](https://github.com/dohyunkimmm/mosigo-case-study/pull/164)의 19장 사업기획서 PPTX와 자료 탭 다운로드 연결을 필수 Site QA·PRD Evidence QA 통과 후 병합했습니다. 원본 PDF·HTML과 기존 미리보기 경로는 유지합니다. **PPTX는 PDF 페이지를 슬라이드로 변환한 배포본**이며, 도형·문장별 편집 가능 원본이라는 뜻은 아닙니다.
- 조회 시 열린 PR은 **31건**(자동 생성 PR 29건 + 수동 검토 PR 2건)입니다. 자동 생성 PR 29건은 병합·중복 여부를 별도 비교해야 하며, 브랜치만 존재하는 것으로 처리하거나 일괄 삭제하지 않습니다. 수동 검토 [#142](https://github.com/dohyunkimmm/mosigo-case-study/pull/142)는 초안으로 `main`과 충돌하고 이전 Site QA·PPT 미리보기 생성 검사가 실패했습니다. PRD의 측정 정의 등 일부 내용은 후속 `main`에 반영되어 있어 전체 바이너리를 재병합하지 않습니다. [#106](https://github.com/dohyunkimmm/mosigo-case-study/pull/106)은 이전 소개 문구가 최신 화면 구조와 충돌합니다. 두 PR은 재검토 전 미병합 상태로 보존합니다.
- 점검 시 원격 브랜치 **32개**(`main` 1, 열린 PR 브랜치 2, `automation/*` 29)입니다. 이 문서 갱신용 브랜치와 후속 Actions 실행으로 개수는 바뀔 수 있습니다. 자동 생성 브랜치는 PR 처리 여부·원본 HEAD·보존 태그 검증 없이 일괄 삭제하지 않습니다.
- 최신 `main` 기준 **병합 직전** Site QA [#43424076762](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43424076762)는 성공, 모바일 엔진 QA [#43424075602](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43424075602)는 과거 뷰어 선택자 `#doc-pdf-save`를 찾지 못해 실패했습니다. 현행 `#doc-expand`·페이지 링크·페이지 라벨을 검사하도록 [`qa/mobile-browser.mjs`](qa/mobile-browser.mjs)를 동기화하며, **변경 이후 QA 성공과 최신 운영 배포 SHA 일치는 별도 확인 대상**입니다.
- 명백한 임시 확장자 파일·SHA 중복은 발견하지 못했습니다. 호환 페이지, 84개 미리보기, 문서 생성 스크립트, `qa/ir-deck-source/` 및 다운로드 원본은 참조·복원 경로를 보호하기 위해 삭제하지 않습니다. 아래 11월 3~11일 기록은 **당시의 점검 이력**이며 현행 수량은 이 절을 우선합니다.


## 2026-11-11 저장소 클렌징 완료

- [정리 PR #100](https://github.com/dohyunkimmm/mosigo-case-study/pull/100)을 **필수 Site QA와 PRD Evidence QA 통과 후** [`b0769d3`](https://github.com/dohyunkimmm/mosigo-case-study/commit/b0769d371ceddb646d56ed9fdb3b2d53c9bffc0c)으로 병합했습니다. PR 검사 [Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43044653761)·[PRD QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43044653757)가 모두 성공했습니다.
- [일회성 정리 실행 #43045002028](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43045002028) **성공**. 종료된 자동 생성 PR #72·#73·#75·#83·#89·#91·#95·#96·#97의 원본 HEAD SHA **9개**를 `archive/20261111/reviewed/pr-*/` 태그로 각각 보존·재조회한 다음 브랜치 참조를 삭제했습니다. **태그 9개 모두 원본 SHA 일치**, 작업 직후 원격 브랜치는 `main` **1개**입니다.
- 11월 11일 정리 완료 시 기존 공개 자료는 **최상위 다운로드 8개·WebP 미리보기 84개**를 유지합니다. 본 최종 정리 PR에서 완료된 일회성 워크플로만 제거하면 `main`은 **파일 163개·디렉터리 10개**(루트 파일 9개·최상위 폴더 5개)입니다. 같은 내용의 Git blob 중복은 점검 시 없었으며, `index.html`, 호환용 HTML, 원본 PDF/PPTX/XLSX, PRD·미리보기 및 `qa/` 생성기는 삭제하지 않았습니다.
- 사용 완료된 `.github/workflows/retire-legacy-branches-20261111.yml`과 과거 일회성 `retire-net-zero-staging` 작업만 정리합니다. **병합 PR의 SHA 태그 선보존·브랜치 회수 자동화**는 `.github/workflows/archive-merged-pr-branches.yml`에 계속 유지합니다.
- GitHub 실행기의 Ubuntu 패키지 서버 DNS 오류를 피하기 위해 Site QA가 Playwright Chromium을 직접 설치하고 PDF 검사에는 conda-forge Poppler 도구를 사용하게 했습니다. **사이트 브라우저·Lighthouse·문서 텍스트/서체·재무자료 QA 기준은 유지**했습니다. 이 기록은 운영 Vercel 배포의 최신 커밋 일치를 별도로 입증하지 않습니다.

## 2026-11-11 `main` 파일·문서 동기화 (초기 점검 기록)

- 기준 커밋: [`12549ad`](https://github.com/dohyunkimmm/mosigo-case-study/commit/12549ad9e2f535808342d6a8cd6939ce1dbf4c7b). 재귀 트리 **파일 163개·디렉터리 10개**(루트 파일 9개·최상위 폴더 5개). 동일 Git blob SHA인 파일 **0쌍**. 기존 기록의 **160개 파일**은 2026-11-09의 스냅샷으로 현행 수량이 아닙니다.
- `downloads/`에는 최상위 원본·게시 파일 **8개**와 `previews/`의 **WebP 84개**가 유지됩니다. 19쪽 사업기획서, 11장 발표자료, 12장 IR 및 XLSX·PRD의 공개 경로는 변경하지 않습니다.
- [#93](https://github.com/dohyunkimmm/mosigo-case-study/pull/93)(상단 소개 정리), [#94](https://github.com/dohyunkimmm/mosigo-case-study/pull/94)(웹·문서 중복 문구 정리), [#98](https://github.com/dohyunkimmm/mosigo-case-study/pull/98)(재생성 PDF/PPTX·미리보기 반영)은 모두 `main`에 병합됐습니다.
- 미병합 종료된 자동 생성 [#95](https://github.com/dohyunkimmm/mosigo-case-study/pull/95)·[#96](https://github.com/dohyunkimmm/mosigo-case-study/pull/96)·[#97](https://github.com/dohyunkimmm/mosigo-case-study/pull/97)의 변경 파일 **10·11·8개, 총 29개**는 각각 [#98](https://github.com/dohyunkimmm/mosigo-case-study/pull/98) 및 현재 `main`의 **같은 경로·Git blob SHA와 전부 일치**합니다. 따라서 이 3건의 산출물은 추가 병합할 필요가 없습니다. 점검 시 열린 PR은 **0건**입니다.
- [`main` Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43025171713)와 [모바일 Safari 엔진 QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/43025171640)가 성공했습니다. 운영 Vercel 배포가 `12549ad`와 정확히 일치하는지는 **별도 미확인**이며, 아래 11월 9일 배포 기록을 현재 상태로 해석하지 않습니다.
- **초기 점검 당시** `main` 외 `automation/*` 브랜치 9개가 남아 있었고, 보존·정리 전에는 삭제하지 않았습니다. 이후 원본 HEAD와 보관 태그 9개를 전부 대조하고 정리했으므로 **현재 상태는 상단 클렌징 완료 기록**을 우선합니다. 원본 다운로드·84개 미리보기·`qa/` 생성기·호환 리디렉션은 유지했습니다.


## 2026-11-09 Vercel 운영 배포 기준 확인 (과거 스냅샷)

- 2026-11-09 조회 시점의 마지막 Vercel 운영 배포 **READY**는 [`feb114f`](https://github.com/dohyunkimmm/mosigo-case-study/commit/feb114f8a6380747fcc63ef8b539933f39b7548e)([배포 기록](https://vercel.com/dohyunkimm/mosigo-case-study/F2h3HLnYN2rv56b6p4SxjnYUjqQL)), 같은 조회 시점 GitHub `main`은 [`8d77935`](https://github.com/dohyunkimmm/mosigo-case-study/commit/8d77935eeae7ce7eeb8de436ba7fdd6b64f89f93)입니다. **당시 `main` SHA의 새 운영 배포 확인은 미완료**입니다. 같은 날짜 Vercel GitHub 상태 검사에서는 미리보기 배포 횟수 제한 오류가 관측됐습니다.
- 두 커밋의 GitHub Compare 변경 파일은 **`.github/workflows/ppt-preview.yml`, `qa/style-presentation.py`, `README.md` 3개뿐**입니다. 공개 `index.html`, `assets/`, `downloads/` 파일 변경은 **0개**이므로 현재 확인 가능한 공개 보고서·다운로드 콘텐츠 차이는 없습니다. 그렇더라도 점검 시점의 `main` 배포가 성공했다고 표시하지 않습니다.
- 검증된 [PPT 미리보기 반복 생성 방지 #84](https://github.com/dohyunkimmm/mosigo-case-study/pull/84)의 변경은 자동 문서 생성 과정에 적용됐고, GitHub Actions [재실행 #42571940810](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42571940810)에서 원본 PPTX·동일한 11쪽 PDF 유지 및 **추가 자동 생성 PR 없음**을 확인했습니다. 새 운영 배포는 배포 제한 해제 후 `main` 커밋 일치 여부와 [Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions)를 별도로 확인해야 합니다.

**포트폴리오:** https://mosigo-case-study.vercel.app/

개인이 작성한 **MOSIGO 병원 동행 서비스 신사업 기획 프로젝트**입니다. 자녀 대리 예약의 사업 기회를 조사하고, 시장·고객·공급 조건, 사업모델·수익성, 단계별 검증과 투자 판단을 정리했습니다. 서비스기획·PRD는 사업 전략을 서비스 요구사항으로 구체화한 **추가 산출물**입니다.

## 신사업 기획 관점

핵심 내용은 **시장 기회와 목표 고객 검토 → 사업모델·진입 전략 비교 → 공급·손익 분석 → 단계별 사업화 판단**입니다. 초기 월 완료 199건과 경제적 손익분기점 1,082건은 실제 성과가 아닌 사업기획 산정 가정입니다. 조건부 기존 사업자 제휴 검증을 우선안으로 제시합니다. [제품 요구사항 정의서(PRD)](downloads/mosigo_prd_delivery.html)는 보조 산출물로서 사용자 여정·화면 정책·R-01~R-06 요구사항을 담습니다. 내부 기술 QA·UAT 기록은 공개 포트폴리오에 포함하지 않습니다.

## 제출용 구성

- MOSIGO의 문제 정의·시장 기회 및 고객 가치
- 고객 세분화, 경쟁·대안 비교와 자녀 대리 예약 전략
- TAM–SAM–SOM 산출 논리, 가격·상품 전략
- AS-IS/TO-BE 비교, 사용자 여정·요구사항·권한·예외 정책·인수 기준과 Service Blueprint
- 직접 제공형·중개형 거래액·공헌이익 민감도, 가정 고정비를 적용한 손익분기점(BEP) 예시
- 우선순위·게이트·KPI·QA·UAT, AI 적용 조건과 제휴형 제한 검증 전략
- MOSIGO 사업화 의사결정과 향후 검증

## 파일·폴더 색인

GitHub의 메인 목록은 **보고서 페이지 / 첨부 자료 / 자동 생성 미리보기 / 품질 검증**으로 구분합니다. 기존 배포 경로는 유지합니다.

| 위치 | 역할 |
| --- | --- |
| [`index.html`](index.html) | 공개 보고서 메인 페이지(9개 장), 문서 탭·사업성 계산기 |
| [`assets/`](assets/) | 페이지 스타일·스크립트·공유 이미지·스마트폰 아이콘 |
| [`downloads/`](downloads/) | 사업기획서·발표자료·IR Deck·계산 파일(현재 최상위 9개) |
| [`downloads/previews/`](downloads/previews/) | 사업기획서 19쪽·발표자료 11장·IR Deck 12장의 일반/소형 WebP(총 84개) |
| [`qa/`](qa/) | 현행 품질 검증·문서 생성 스크립트와 IR 원본 조각. 내부 기술 검증 부록·상세 실행 증빙은 공개 저장소에서 제외 |
| [`docs/history/`](docs/history/) | 과거 브랜치·저장소·폰트 점검 기록 4건. 당시 기준의 스냅샷으로, 현행 운영 상태는 아래 안내를 우선 확인 |
| [`.github/workflows/`](.github/workflows/) | 품질 검증과 문서·이미지 생성 자동화 |
| [`.github/scripts/`](.github/scripts/) | 자동 생성 문서가 `main` 직접 푸시 대신 검토용 PR을 만들도록 하는 공용 게시 스크립트 |
| [`decision-memos.html`](decision-memos.html) · [`forecast.html`](forecast.html) · [`materials.html`](materials.html) | 과거 링크 호환용 페이지. 현재 보고서의 의사결정·사업성·첨부 자료 위치로 연결 |

**첨부 자료 원본과 게시본:** [사업기획서 HTML](downloads/mosigo_business_plan_20261031.html) · [사업기획서 PDF](downloads/mosigo_business_plan_20261031.pdf) · [사업기획서 PPTX](downloads/mosigo_business_plan.pptx) · [발표자료 PPTX](downloads/mosigo_report.pptx) · [발표자료 미리보기 PDF](downloads/mosigo_report_preview.pdf) · [IR Deck PPTX](downloads/MOSIGO_IR_Investment_Review_12slides.pptx) · [IR Deck PDF](downloads/MOSIGO_IR_Investment_Review_12slides.pdf) · [계산 파일 XLSX](downloads/mosigo_model.xlsx).

2026-11-03 당시의 파일 정합성 점검 기록은 [과거 점검 문서](docs/history/repository-audit-20261103.md)에 보존합니다. **2026-11-09 당시 GitHub `main` 재귀 트리 기준 파일 160개·디렉터리 10개**(루트 파일 9개·최상위 폴더 5개)입니다. 위 문서·미리보기 수량은 이 정리 시점 기준이며, 이후 변경 때 재검증해야 합니다.

## 2026-11-09 `main` 목록 및 생성 산출물 동기화 (과거 기록)

- 최신 [`main` `5409063`](https://github.com/dohyunkimmm/mosigo-case-study/commit/54090635c2068c6dbf9c4c408b146f0009acc3e0)의 잘리지 않은 재귀 트리는 **160개 파일·10개 디렉터리**(루트 파일 9개·최상위 폴더 5개)입니다. 앞선 159개 파일 수는 11월 8일 당시 스냅샷입니다. 동일 Git blob SHA 중복은 발견하지 못했으며, 정적 진입점과 호환용 HTML, 원본 PPTX/PDF/XLSX, 84개 미리보기 및 `qa/` 생성 도구는 참조 확인 전 제거하지 않습니다.
- **산출물 반영 완료:** 자동 생성 [#72](https://github.com/dohyunkimmm/mosigo-case-study/pull/72)·[#73](https://github.com/dohyunkimmm/mosigo-case-study/pull/73)의 원본 Git blob SHA 그대로 PDF 2개·PPTX 1개를 새 검토용 [#82](https://github.com/dohyunkimmm/mosigo-case-study/pull/82)로 통합했습니다. 보호된 `main`의 필수 QA 및 문서 변환 검사 통과 후 [`feb114f`](https://github.com/dohyunkimmm/mosigo-case-study/commit/feb114f8a6380747fcc63ef8b539933f39b7548e)로 병합됐으며 원본 PR 2건은 중복 방지를 위해 미병합 종료했습니다. 공개 경로 및 기존 WebP 미리보기는 유지했습니다.
- **반복 생성 방지:** 재생성 PR [#83](https://github.com/dohyunkimmm/mosigo-case-study/pull/83)은 동일 화면·본문의 바이너리 재저장 문제로 미병합 종료하고, [#84](https://github.com/dohyunkimmm/mosigo-case-study/pull/84)([`e3f5277`](https://github.com/dohyunkimmm/mosigo-case-study/commit/e3f527780259f36292196e0ad231ca496e692df5))에서 이미 정규화된 PPTX 바이트 유지와 11쪽 PDF 추출 텍스트·22개 WebP 동일성 확인 시 기존 PDF를 보존하도록 개선했습니다. 해당 PR의 필수 QA·문서 변환은 성공했습니다. Vercel 미리보기는 **무료 배포 횟수 제한**으로 실패했으며 이를 사이트 QA 통과와 혼동하지 않습니다.
- 해당 시점 `main`의 Site QA·PRD Evidence QA·모바일 Safari 엔진 QA·네이티브 iOS Safari 시뮬레이터 QA는 성공 기록이 있었습니다. 이는 **당시 두 생성 PR의 산출물 검사 완료**를 의미하지 않았으며, 이후 변경 반영은 위 2026-11-11 현황을 우선합니다. 생성 PR의 최신 검사와 PDF/PPT 문서 일치 결과를 확인한 다음 별도로 반영해야 합니다.
- 연계 [mosigo 앱 저장소](https://github.com/dohyunkimmm/mosigo)의 열린 [#88 Blob 보존/복구 이슈](https://github.com/dohyunkimmm/mosigo/issues/88)는 본 보고서의 완료 항목이 아닙니다. 로컬 폴더의 명백한 임시/동일 파일은 검출되지 않았으므로 기존 공개 경로와 다운로드 파일은 그대로 보존합니다.

## 자료의 구분

- **작성 주체:** 개인 단독 신사업 기획 프로젝트.
- **프로젝트 근거:** MOSIGO의 기존 경쟁 앱 7종·리뷰 118건 조사 기록, 서비스 흐름·19개 모달/상태 화면, 예약·복구·공유 구현 범위. 보고서의 개인 분석과 조사·구현 원자료의 출처를 구분합니다.
- **검증 가정:** 시장 규모, 제품·운영 설계, 가격·원가, 사업모델·수익성, KPI와 실행 게이트는 확인된 결과와 기획 가설을 구분해 서술합니다.
- **데모·구현 원본:** [MOSIGO 서비스 데모](https://mosigo-nine.vercel.app/) 링크 1개만 포트폴리오에 표시합니다. [MOSIGO 앱 소스 저장소](https://github.com/dohyunkimmm/mosigo)는 시연 UI·예약 API를, 이 저장소는 신사업 기획·사업성 자료와 추가 서비스기획·PRD 문서를 별도로 관리합니다. 데모 페이지와 임베드는 이 보고서에 포함하지 않습니다.
- **자료 바로보기:** 사업화 의사결정까지 읽은 뒤 주요 산출물인 사업기획서 PDF 19쪽과 보조 발표자료 11장·IR Deck 12장을 탭으로 볼 수 있습니다. PRD는 별도 추가 자료로 연결하며 PPTX·PDF 내려받기도 제공합니다.
- **IR 예산 가정:** 8주 제한 검증의 현금 집행 상한은 기존 월 현금 고정비 200만 원 × 2개월 = 400만 원으로 단순 산정했습니다. P0 80만·P1 120만·P2 200만 원은 신규 단계별 배분 가정이며, 인력 기회비용 400만 원은 별도입니다. 일회성 구축·보험·법무·추가 판촉·환불비와 외부 투자유치 금액·기업가치는 포함하지 않았습니다. 실제 투자유치·고객 실적을 의미하지 않습니다.
- **채용공고:** 사람인 IT기획·전략기획·PM 공고의 담당업무·자격요건·우대사항은 작성·품질 검토 과정에서만 참고합니다. 포트폴리오 사이트에는 회사명·채용공고 링크·역량 대조표를 노출하지 않습니다.

콘텐츠 구성은 분석 목적에 맞춰 조정하며 섹션 수를 고정하지 않습니다. 원본 MOSIGO 앱 저장소와 배포는 이 작업에서 수정하지 않습니다.

## 표기 기준과 검증 자동화

- 기존 프로젝트 자료의 **19개 대화창**과 연결된 데모의 **30개 상태 기반 화면**은 서로 다른 범위·집계 단위입니다. 직접 비교하거나 합산하지 않습니다.
- 재무 시나리오·민감도 결과는 사업 운영 실적이 아닌 **가정 모형**입니다. 취소 증가에 따른 추가 지원·환불 비용은 별도 검증 대상입니다.
- GitHub Actions **Site QA**는 `main`을 대상으로 하는 모든 PR에서 로컬 브라우저·문서·Lighthouse 검사를 수행하고, main 변경·매주 월요일 오전 9시(한국 시간)·수동 실행에서는 운영 배포 HTML 버전 일치와 실서비스 측정까지 검증합니다. 두 환경에서 반응형·계산기·다운로드(PDF 헤더·종료 표식, Office 파일 서명 포함)·자바스크립트 비활성 모드를 검사합니다.
- PPT 미리보기 PDF는 원본 PPTX 변경 시 자동 갱신하며, `Site QA`는 문서 탭 전환과 배포 PDF 형식을 검사합니다.
- 로컬 및 운영 배포의 화면 캡처·Lighthouse 보고서는 GitHub Actions 실행 기록의 산출물로 보관합니다. 운영 배포의 Lighthouse 점수는 CI 환경의 합성 측정값으로 실제 사용자 경험 데이터(CrUX/RUM)가 아닙니다.

## 공개 저장소 운영 및 브랜치 보호 (2026-11-08)

- **운영 기준:** 저장소는 **공개(Public)** 상태이며 `main`은 **`protected=true`**입니다. [Ruleset `Protect main`](https://github.com/dohyunkimmm/mosigo-case-study/settings/rules/26795565)이 `Active`로 적용되어 브랜치 **삭제·강제 푸시를 차단**하고, **PR을 통한 병합과 두 필수 QA 검사**를 요구합니다.
- **PR 필수 설정 완료:** 문서 생성 작업 6개는 `main`에 직접 푸시하지 않고, 변경된 산출물이 있을 때 `automation/*` 작업 브랜치와 검토용 PR을 생성하도록 전환했습니다. `browser-and-lighthouse`, `prd-trace-and-product-tests`는 **모든 PR에서 실행되는 필수 GitHub Actions 검사**로 지정됐습니다. 서버 측 Ruleset에서 PR 필수·필수 검사 설정을 확인했습니다.
- **자동 생성 PR 운영:** 사용자는 [Actions → General](https://github.com/dohyunkimmm/mosigo-case-study/settings/actions)에서 GitHub Actions의 PR 생성 허용 옵션을 활성화했다고 확인했습니다. 자동 생성 PR [#72](https://github.com/dohyunkimmm/mosigo-case-study/pull/72)·[#73](https://github.com/dohyunkimmm/mosigo-case-study/pull/73)은 직접 확인했으나 승인 대기로 필수 검사 실행이 차단됐습니다. 생성 파일 자체는 별도 GitHub App 검토 PR [#82](https://github.com/dohyunkimmm/mosigo-case-study/pull/82)에서 **바이트 동일성을 보존하고 필수 QA를 새로 통과한 뒤 `main`에 반영**됐습니다. 원본 자동 PR은 미병합 종료했습니다. `GITHUB_TOKEN`이 생성한 PR은 검사를 실행하려면 관리자의 **Approve workflows to run** 승인이 필요할 수 있으며, 자동 승인·자동 병합은 사용하지 않습니다.
- **워크플로 갱신:** 생성 소스가 변경되면 자동으로 재생성하며, 워크플로 파일만 변경했다면 불필요한 동시 재생성을 피하기 위해 해당 Actions의 `Run workflow`를 `main`에서 수동 실행합니다.
- **검증 범위:** 생성 PR은 필수 QA 검사를 통과한 후 사람이 병합합니다. 사이트·PRD 운영 HTML 및 XLSX/PDF/PPTX는 [운영 Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42479802507)에서 검증했습니다. 규칙 적용은 GitHub API로 직접 확인했으며, 실제 자동 생성 PR 게시·승인은 최초 실행 시 확인해야 합니다.
- **과거 기록:** [#15](https://github.com/dohyunkimmm/mosigo-case-study/issues/15)의 비공개 시절 제약과 `docs/history/`의 `protected=false` 표기는 당시 상태를 설명한 것입니다. 현재 보호 상태의 근거로 사용하지 않습니다.

## 2026-11-08 후속 정리 검증

- [PR #64](https://github.com/dohyunkimmm/mosigo-case-study/pull/64): 자동 생성 산출물 6종을 `main` 직접 푸시 대신 검토용 PR로 게시하도록 전환했습니다. 필수 검사 `browser-and-lighthouse`, `prd-trace-and-product-tests`가 모든 PR을 검사하며 [GitHub Ruleset](https://github.com/dohyunkimmm/mosigo-case-study/settings/rules/26795565)에서 강제 적용됩니다.
- [PR #66](https://github.com/dohyunkimmm/mosigo-case-study/pull/66)과 [정리 Actions #42481462073](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42481462073): 병합 이력 및 정확한 SHA를 확인한 브랜치를 포함해 **25개를 `archive/20261108/` 태그로 먼저 보존하고 원격 브랜치 참조를 삭제**했습니다. 성공 후 일회성 정리 워크플로도 제거했습니다.
- 병합된 후속 PR 브랜치가 쌓이지 않도록 `.github/workflows/archive-merged-pr-branches.yml`에서 원본 SHA 보존·검증·참조 정리를 자동화했습니다. 이는 `main`을 강제 변경하지 않으며 포크·열린 PR·SHA 불일치가 있을 때 삭제하지 않습니다.
- 과거 V03 PDF 임시 전송 브랜치는 9개 고유 커밋을 보유했지만 최종 Git 트리가 기존 `main` 조상과 정확히 같음을 확인했습니다. [자동 정리 #42482370425](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42482370425)에서 원본 SHA를 태그로 보존한 뒤 삭제했고, [이슈 #67](https://github.com/dohyunkimmm/mosigo-case-study/issues/67)을 완료 처리했습니다.
- [자동 생성 PR 실제 검증 #42482370491](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42482370491): `GITHUB_TOKEN`으로 배포되지 않는 QA 파일을 담은 [봇 PR #69](https://github.com/dohyunkimmm/mosigo-case-study/pull/69)를 실제 생성하고 정확한 SHA·PR 존재를 확인했습니다. 테스트 PR은 **병합하지 않고 종료**했고 원본 SHA를 `archive/verification/` 태그로 보존한 뒤 테스트 브랜치를 삭제했습니다. 성공한 일회성 검사 워크플로도 제거했습니다. 이는 봇 PR 생성 권한 검증이며, 향후 생성 PR의 **필수 QA 실행 승인**은 사용자가 요청받을 수 있습니다.
- [병합 브랜치 자동 보존 #42482371028](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42482371028) 성공. 정리 후 원격 브랜치 목록은 `main` **1개**입니다.
- [Actions 실행기 오류 #55](https://github.com/dohyunkimmm/mosigo-case-study/issues/55)는 후속 모바일 Safari·Site QA·PRD QA의 실제 작업 실행 성공을 확인하고 종료했습니다. 원본 MOSIGO [Blob 보존 이슈 #88](https://github.com/dohyunkimmm/mosigo/issues/88)은 운영 데이터 독립 소유권·만료/복구 검증이 끝나지 않아 별개로 열려 있습니다.

## 기술

Pretendard Variable · 정적 HTML로 독립 배포합니다. 9개 장은 요약을 우선 보여주고 상세는 선택해 열 수 있습니다.

- **아이콘:** 토스페이스 공식 스마트폰 글리프를 정적 PNG로 사용합니다. [토스페이스 저작권 및 사용조건](https://toss.im/tossface/copyright). 대용량 이모지 웹폰트를 방문자에게 전달하지 않습니다.

## 2026-11-07 저장소 클렌징·QA 기록

- [PR #38](https://github.com/dohyunkimmm/mosigo-case-study/pull/38): 현행 문서 뷰어와 맞지 않는 Chromium·모바일·iOS Safari QA 선택자를 교체하고 미사용 검색 색인 생성 코드/CSS 일부를 정리. 기존 문서·미리보기·URL을 보존.
- [PR #39](https://github.com/dohyunkimmm/mosigo-case-study/pull/39): 병합된 작업 브랜치 13개를 원본 SHA와 PR 상태 확인 후 `archive/20261107/` 태그로 보존하고 브랜치 참조만 회수. [정리 Actions](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42331192554) 성공, 점검 직후 원격 브랜치는 `main`만 남았음.
- [Site QA PR #38](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42330700286) 및 [PR #39](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42331017120) 통과. [병합된 코드의 Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42330886274)는 첫 실행에서 합성 Lighthouse 모바일 성능 83점(기준 90점)으로 실패한 뒤 **기준을 바꾸지 않고 재실행에 성공**함.
- [모바일 엔진 QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42330886270) 및 [네이티브 iOS Safari 시뮬레이터 QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42330886263) 통과. 시뮬레이터 QA는 실제 iPhone 실기기 통과를 의미하지 않음.
- 과거 일회성 브랜치 정리 워크플로는 완료로 인해 제거하며, 후속 정리용 워크플로는 본인 파일 변경이 `main`에 병합될 때만 실행되고 다른 변경에는 반응하지 않도록 제한.
- 2026-11-07 당시에는 `protected=false`였으나, 2026-11-08부터 위 `Protect main` 규칙이 적용됨. 과거 저장소·브랜치 보존 검증은 사용자 데이터, Vercel Blob, 실제 실기기와 별개의 범위임.
