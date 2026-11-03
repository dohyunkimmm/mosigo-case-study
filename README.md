# MOSIGO 전략기획 보고서 · Strategy Case Study

**포트폴리오:** https://mosigo-case-study.vercel.app/

개인이 단독 작성한 **MOSIGO 병원동행 서비스의 전략기획 보고서**입니다. MOSIGO를 다른 사업과 분리해 소개하는 문서가 아니라, 해당 서비스의 고객 문제부터 시장·제품·수익모델·실행 전략을 분석한 결과물입니다.

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
| [`downloads/`](downloads/) | 사업기획서·발표자료·IR Deck·계산 파일(최상위 7개) |
| [`downloads/previews/`](downloads/previews/) | 사업기획서 17쪽·발표자료 11장·IR Deck 12장의 일반/소형 WebP(총 80개) |
| [`qa/`](qa/) | 점검·문서 생성 스크립트, 검토 기록, IR 원본 복원용 압축 조각 |
| [`.github/workflows/`](.github/workflows/) | 품질 검증과 문서·이미지 생성 자동화 |
| [`decision-memos.html`](decision-memos.html) · [`forecast.html`](forecast.html) · [`materials.html`](materials.html) | 과거 링크 호환용 페이지. 현재 보고서의 의사결정·사업성·첨부 자료 위치로 연결 |

**첨부 자료 원본과 게시본:** [사업기획서 HTML](downloads/mosigo_business_plan_20261031.html) · [사업기획서 PDF](downloads/mosigo_business_plan_20261031.pdf) · [발표자료 PPTX](downloads/mosigo_report.pptx) · [발표자료 미리보기 PDF](downloads/mosigo_report_preview.pdf) · [IR Deck PPTX](downloads/MOSIGO_IR_Investment_Review_12slides.pptx) · [IR Deck PDF](downloads/MOSIGO_IR_Investment_Review_12slides.pdf) · [계산 파일 XLSX](downloads/mosigo_model.xlsx).

파일 존재·참조·미리보기 개수와 별도 미반영 항목은 [2026-11-03 저장소 정합성 점검](qa/repository-audit-20261103.md)에 기록했습니다.

## 자료의 구분

- **작성 주체:** 개인 단독 Strategy Case Study.
- **프로젝트 근거:** MOSIGO의 기존 경쟁 앱 7종·리뷰 118건 조사 기록, 서비스 흐름·19개 모달/상태 화면, 예약·복구·공유 구현 범위. 보고서의 개인 분석과 조사·구현 원자료의 출처를 구분합니다.
- **검증 가정:** 시장 규모, 제품·운영 설계, 가격·원가, 사업모델·수익성, KPI와 실행 게이트는 확인된 결과와 기획 가설을 구분해 서술합니다.
- **데모:** [MOSIGO 서비스 데모](https://mosigo-nine.vercel.app/) 링크 1개만 있습니다. 데모 페이지와 임베드는 이 보고서에 포함하지 않습니다.
- **자료 바로보기:** 사업기획서 PDF 17쪽, 기존 발표자료 11장, 실무형 IR Deck 12장을 탭으로 전환해 읽을 수 있습니다. PPTX·PDF 내려받기도 제공합니다.
- **IR 예산 가정:** 8주 제한 검증의 현금 집행 상한은 기존 월 현금 고정비 200만 원 × 2개월 = 400만 원으로 단순 산정했습니다. P0 80만·P1 120만·P2 200만 원은 신규 단계별 배분 가정이며, 인력 기회비용 400만 원은 별도입니다. 일회성 구축·보험·법무·추가 판촉·환불비와 외부 투자유치 금액·기업가치는 포함하지 않았습니다. 실제 투자유치·고객 실적을 의미하지 않습니다.
- **채용공고:** 사람인 IT기획·전략기획·PM 공고의 담당업무·자격요건·우대사항은 작성·품질 검토 과정에서만 참고합니다. 포트폴리오 사이트에는 회사명·채용공고 링크·역량 대조표를 노출하지 않습니다.

콘텐츠 구성은 분석 목적에 맞춰 조정하며 섹션 수를 고정하지 않습니다. 원본 MOSIGO 앱 저장소와 배포는 이 작업에서 수정하지 않습니다.

## 표기 기준과 검증 자동화

- 기존 프로젝트 자료의 **19개 대화창**과 연결된 데모의 **30개 상태 기반 화면**은 서로 다른 범위·집계 단위입니다. 직접 비교하거나 합산하지 않습니다.
- 재무 시나리오·민감도 결과는 사업 운영 실적이 아닌 **가정 모형**입니다. 취소 증가에 따른 추가 지원·환불 비용은 별도 검증 대상입니다.
- GitHub Actions **Site QA**는 `main`을 대상으로 하는 모든 PR에서 로컬 브라우저·문서·Lighthouse 검사를 수행하고, main 변경·매주 월요일 오전 9시(한국 시간)·수동 실행에서는 운영 배포 HTML 버전 일치와 실서비스 측정까지 검증합니다. 두 환경에서 반응형·계산기·다운로드(PDF 헤더·종료 표식, Office 파일 서명 포함)·자바스크립트 비활성 모드를 검사합니다.
- PPT 미리보기 PDF는 원본 PPTX 변경 시 자동 갱신하며, `Site QA`는 문서 탭 전환과 배포 PDF 형식을 검사합니다.
- 로컬 및 운영 배포의 화면 캡처·Lighthouse 보고서는 GitHub Actions 실행 기록의 산출물로 보관합니다. 운영 배포의 Lighthouse 점수는 CI 환경의 합성 측정값으로 실제 사용자 경험 데이터(CrUX/RUM)가 아닙니다.

## 기술

Pretendard Variable · 정적 HTML로 독립 배포합니다. 9개 장은 요약을 우선 보여주고 상세는 선택해 열 수 있습니다.

- **아이콘:** 토스페이스 공식 스마트폰 글리프를 정적 PNG로 사용합니다. [토스페이스 저작권 및 사용조건](https://toss.im/tossface/copyright). 대용량 이모지 웹폰트를 방문자에게 전달하지 않습니다.
