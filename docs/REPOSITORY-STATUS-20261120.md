# MOSIGO `main` 목록·문서 정합성 점검 (2026-11-20)

## 후속 운영 배포·미반영 후보 처리 (2026-11-20)

- [문서 동기화 PR #193](https://github.com/dohyunkimmm/mosigo-case-study/pull/193)은 Site QA와 PRD Evidence QA 성공 후 `main` [`31d9dda`](https://github.com/dohyunkimmm/mosigo-case-study/commit/31d9ddad2a9eced2b847c0a0857ce54fcea2d5ce)로 병합됐습니다. Vercel 운영 배포 `dpl_7bmqdcSgvuvDfPJqUcSSEcWH81rE`의 상태는 `READY / production / main`, 연결 커밋은 정확히 `31d9dda`입니다.
- [PR #185](https://github.com/dohyunkimmm/mosigo-case-study/pull/185)는 **2026-11-20 미병합 종료**했습니다. 구 자동 생성본 HEAD `d9a045940bb7ce4ef8712d1c3b5add42c04f06f3`, PPTX blob `c40c42a510cdb16f86395b43701befe383df2067`입니다. 생성 당시 기반 PPTX blob `b2021df0344fdd0dd1c074733b4fe0fe29519a95`와 최신 `main` blob `2fa0e3ccf953d0e6a58f956df73b044f5fa99da8`이 서로 다릅니다.
- 후속 병합된 [#184](https://github.com/dohyunkimmm/mosigo-case-study/pull/184)에서 PPTX·PDF·미리보기 원본을 교체했으며, [#188](https://github.com/dohyunkimmm/mosigo-case-study/pull/188)에서 PPTX·PDF·미리보기를 다시 변경하고 **Site QA, PRD QA, 모바일 QA 및 문서 생성/변환 검사에 성공**했습니다. 따라서 오래된 PR의 바이너리를 현재 `main`에 덮어쓰지 않습니다. **두 바이너리의 텍스트·화면·바이트 동등성은 검증되지 않았습니다.**
- 종료 직후 **열린 PR은 0건**입니다. `automation/ppt-preview-44210022466-1` 원본 브랜치가 남아 있음을 확인했고, 자동 태그 보존·참조 삭제 Actions는 아직 성공 확인이 되지 않았습니다. `archive/closed/YYYYMMDD/pr-185/...` 보존 태그 확인 전 브랜치 수를 정리 완료로 표기하지 않습니다.
- 이후 이 후속 문서 수정이 `main`에 병합되면 새로운 배포 커밋의 운영 일치 여부는 다시 검증합니다. 아래의 #185 '열린 PR 1건' 문장은 **정리 전 초기 점검 기록**입니다.

## 점검 기준과 현재 목록

- 점검 원본: [`main` `96ecc32d`](https://github.com/dohyunkimmm/mosigo-case-study/commit/96ecc32d87b729cffba7a2ea99ebea17c045df1e). GitHub 재귀 트리는 `truncated=false`였습니다.
- 점검 직전 **파일 185개·디렉터리 10개**, 루트 파일 9개·최상위 폴더 5개. 이 문서 1개를 추가하는 동기화 변경이 반영되면 **파일 186개·디렉터리 10개**가 됩니다.
- 동기화 후 파일 분포: `.github/` 26, `assets/` 5, `docs/` 5(과거 점검 4개 + 이 문서), `downloads/` 93(최상위 9 + WebP 미리보기 84), `qa/` 48, 루트 9.
- 원본 트리에서 **동일 Git blob SHA 파일 0쌍**. 확정된 임시·중복 삭제 대상은 없습니다. `decision-memos.html`·`forecast.html`·`materials.html`은 기존 링크 호환용이므로 보존합니다.
- [`docs/history/`](history/)의 2026-10~11월 점검 문서는 **과거 스냅샷**입니다. README의 184개 파일·열린 PR 0건(2026-11-14)도 당시 기록입니다.

## 최근 반영 내용과 자료

- 2026-11-14 [통합 PR #178](https://github.com/dohyunkimmm/mosigo-case-study/pull/178)로 사업기획서 19쪽, 서비스기획 발표자료 11장, IR 12장과 같은 출처 PDF에서 렌더한 WebP **84개**를 정합성 검증 후 반영했습니다.
- 이후 2026-11-17~19의 [PR #181~#192](https://github.com/dohyunkimmm/mosigo-case-study/pulls?q=is%3Apr+is%3Amerged)에는 중복 본문 정리, 제휴 계산기의 공급 상한·입력 정의·손익분기 검증, 자료 뷰어의 문서별 페이지 제목·공유/복원, 모바일·iOS Safari QA 보수와 모바일 PDF 이미지 갱신이 반영됐습니다. 현재 HTML·XLSX·PPTX·PDF의 내용을 과거 브랜치로 되돌리지 않습니다.
- 재무와 지표의 수치는 **실적이 아닌 사업 시뮬레이션 가정**으로 표기합니다. 공식 서비스 저장소 [`mosigo`](https://github.com/dohyunkimmm/mosigo)는 이 문서 정리 범위 밖입니다.

## 미반영 후보 및 보존 결정

- 점검 시 열린 PR은 [**#185: 발표자료 PPTX 자동 생성본**](https://github.com/dohyunkimmm/mosigo-case-study/pull/185) **1건**입니다. `automation/ppt-preview-44210022466-1`이 `main` 대비 **ahead 1 / behind 8**이며, 병합 가능 판정은 `mergeable=false`입니다. 변경 파일은 `downloads/mosigo_report.pptx` 1개로, 자동 변환 바이너리의 **문구·렌더·편집 가능성 동등성 검증은 미완료**입니다. 필수 Site/PRD QA 성공을 확인하지 못했으므로 **병합하거나 중복으로 단정해 종료하지 않습니다**.
- `fix/pilot-review-criteria`, `review/document-audit-20261117`, `review/mosigo-opening-copy`는 최신 `main`과 갈라진 보존·검토 브랜치입니다. 일부 고유 커밋이 있으므로 현재 트리 비교만으로 삭제·병합하지 않습니다. 점검 시 원격 브랜치는 `main`을 포함해 **5개**입니다.
- 기존 생성 PR 29건의 2026-11-14 보존·정리는 완료 기록으로 유지하되, 이후 새로 생긴 #185까지 적체 0건이라고 표현하지 않습니다.

## 검사와 보류 범위

- 최신 `main` SHA `96ecc32d`의 [모바일 Safari 엔진 QA #44498361286](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/44498361286)는 **성공**했습니다.
- [Site QA #44496228242](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/44496228242)는 직전 커밋 `4a28257d`, [PRD Evidence QA #44314857502](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/44314857502)는 이전 커밋 `c2b02446` 기준 성공입니다. 이를 **최신 HEAD의 모든 QA 통과**로 확대 해석하지 않습니다.
- 이번 문서 동기화 PR의 필수 검사와 **Vercel 운영 배포 SHA 일치**는 아직 확인하지 않았습니다. 원본 PDF/PPTX/XLSX, 계산식, WebP 미리보기, 호환 경로와 역사 자료는 변경하지 않습니다.
