# MOSIGO `main` 목록·문서 정합성 점검 (2026-11-20~25)

## 2026-11-25 최종 배포 검증 및 재생성 중복 방지

- [#207](https://github.com/dohyunkimmm/mosigo-case-study/pull/207)은 Site·PRD·모바일·PPT 변환 QA 통과 후 [`2c4711b`](https://github.com/dohyunkimmm/mosigo-case-study/commit/2c4711bc27364dba25b361e2c03af666118eed30)로 병합됐다. 병합 후 [Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545683236), [모바일 QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545683353), [PPT 변환](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545683277), [모바일 미리보기](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545683435), [문서 텍스트 추출](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545683219)은 성공했다.
- Vercel 운영 [배포 기록](https://vercel.com/dohyunkimm/mosigo-case-study/jVy9bBCxkJj3LEPnggvd9rS8A5mj)은 READY / production / main이며 SHA가 `2c4711b`와 정확히 일치한다. 이 기록은 해당 시점의 배포 증거다.
- #201·#202 원본 HEAD를 보존 태그로 검증하고 구 브랜치와 임시 검증 브랜치를 [정리 실행](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545561555)에서 제거했다.
- [#208](https://github.com/dohyunkimmm/mosigo-case-study/pull/208)은 아티팩트 14987322064와 14990734320의 ZIP SHA-256을 대조한 뒤 비교했다. PPTX 내부 72개 경로 및 모든 압축 해제 데이터가 동일했고 72개 ZIP 저장 시각만 달랐다. PDF와 22개 WebP도 바이트가 동일하여 미병합 종료했다. 원본 HEAD는 보존 태그 확인 전 삭제하지 않는다.
- 재발 방지: PPTX 편집 단계 직후 원본과 새 ZIP의 중복 없는 경로 집합 및 모든 내부 바이트가 정확히 일치할 때만 원본 파일 바이트를 복구한다. 실제 XML·미디어 등 변경은 그대로 검토 대상으로 유지한다. 파일 수 185개 및 공개 경로는 유지하며 이번 변경의 QA·병합·배포는 별도 검증한다.

## 2026-11-25 후속 동기화 · 최신 생성 자료 검증

- 정리 [PR #206](https://github.com/dohyunkimmm/mosigo-case-study/pull/206)은 Site QA·PRD Evidence QA 통과 후 [`9d19d19`](https://github.com/dohyunkimmm/mosigo-case-study/commit/9d19d1971bc44579cfd150ac5b1e3be6729a9d57)로 병합됐다. 재귀 트리 파일 **185개·디렉터리 10개**를 재확인했다. Vercel 운영 배포 [dpl_97GkPEDKSVBTuS83BKKA2qc2ocD5](https://vercel.com/dohyunkimm/mosigo-case-study/97GkPEDKSVBTuS83BKKA2qc2ocD5)는 READY / production / main, 연결 SHA는 정확히 `9d19d19`이다.
- [최신 PPT 변환 실행](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45535733339)의 55866a3 기준 아티팩트 14987322064를 내려받아 ZIP SHA-256과 24개 허용 경로를 확인했다. [검증 실행 #45545355670](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45545355670)에서 기존 편집용 11장 슬라이드의 모든 텍스트(표 포함)와 일치함을 확인했으며, PDF·WebP 파일 형식 검증과 변경 16개 경로의 리뷰 브랜치 게시에 성공했다.
- 최신 모바일 생성 아티팩트 14984407652의 사업기획서 WebP 38개는 현행 main과 모두 동일 blob SHA다. 이전 #201의 7개 및 #202의 8개 변경 경로는 모두 이번 최신 산출물에 포함된다. 이전 생성본과의 바이트 동등성을 주장하지 않는다.
- 이번 변경은 서비스기획 PPTX·PDF·WebP 14개 및 현황 문서 2개만 동기화한다. 사업기획서·IR·재무 모델 및 본문은 유지하며 신규 PR의 필수 QA, 병합, 운영 배포 SHA는 별도로 확인한다. 아래 기록은 점검 시점별 스냅샷이다.

## 최신 점검 (2026-11-25)

- 점검 기준: [`main` `55866a3`](https://github.com/dohyunkimmm/mosigo-case-study/commit/55866a332141dd9ce729bc9cee58b86c83aa0427), 재귀 트리 `truncated=false`. 파일 **186개·디렉터리 10개**, 루트 파일 9개·최상위 폴더 5개. 분포: `.github/` 26, `assets/` 5, `docs/` 5, `downloads/` 93(공개 파일 9 + WebP 84), `qa/` 48, 루트 9. 동일 blob SHA 중복 및 명백한 임시 확장자 파일 없음.
- [#200](https://github.com/dohyunkimmm/mosigo-case-study/pull/200)·[#203](https://github.com/dohyunkimmm/mosigo-case-study/pull/203)·[#204](https://github.com/dohyunkimmm/mosigo-case-study/pull/204)·[#205](https://github.com/dohyunkimmm/mosigo-case-study/pull/205) 반영: 본문·발표자료 중복 표현 및 정보 밀도 개선, 사업기획서 9·10·18·19쪽 재배치, 손익 모델 안내 간결화. 기준 HEAD의 [Site QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45535733406), [모바일 Safari QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45535733393), [PPT 미리보기 변환](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45535733339), [문서 텍스트 추출](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45535733279) 성공. PRD QA는 직전 `6a65fed`의 [실행](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45531078125) 성공 기록으로 구분한다.
- 열린 생성 PR 2건: [#201](https://github.com/dohyunkimmm/mosigo-case-study/pull/201) 모바일 미리보기 7개, [#202](https://github.com/dohyunkimmm/mosigo-case-study/pull/202) PPTX/PDF/미리보기 8개. 두 브랜치 모두 ahead 1 / behind 3, 각 변경 경로의 blob은 현재 main과 모두 다르다. Site/PRD QA는 `action_required`([#201 Site](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45525259659), [#202 Site](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/45525270452)). 후속 #203~205에서 원본 및 일부 동일 미리보기 경로가 변경됐으므로 구 생성물을 덮어쓰지 않는다. 최신 원본 기준 재생성 결과와 내용·렌더를 대조하기 전 병합/종료하지 않는다.
- 점검 시 원격 브랜치 6개(main, 자동 생성 2개, 수동 검토 3개), 일반 열린 이슈 0건. `fix/pilot-review-criteria`(ahead 3/behind 53), `review/document-audit-20261117`(3/22, 비교 변경 파일 없음), `review/mosigo-opening-copy`(1/67)는 고유 이력의 검토·보존 대상으로 유지한다.
- 완료된 일회성 `.github/workflows/archive-final-four-generated-prs.yml`은 #135·139·153·154의 원본 HEAD와 `archive/closed/20261114/pr-*/automation/*` 태그 4개가 정확히 일치함을 11월 25일 재확인했고 기존 브랜치가 없으므로 제거한다. 대응 Python 스크립트와 감사 이력 및 일반 보존 자동화는 유지한다. 이 변경 반영 시 예상 파일 **185개·디렉터리 10개**(`.github/` 25, 나머지 동일).
- 기존 다운로드·호환 경로·본문·사업 가정·원본 PPTX/PDF/XLSX·WebP 및 QA 기준을 유지한다. 문서 정리 PR의 필수 검사와 최신 Vercel 운영 배포 SHA 일치는 별도 검증한다.

---

아래는 2026-11-20 당시 점검 및 후속 운영 배포 기록입니다.

## 후속 운영 배포·미반영 후보 처리 (2026-11-20)

- [문서 동기화 PR #193](https://github.com/dohyunkimmm/mosigo-case-study/pull/193)은 Site QA와 PRD Evidence QA 성공 후 `main` [`31d9dda`](https://github.com/dohyunkimmm/mosigo-case-study/commit/31d9ddad2a9eced2b847c0a0857ce54fcea2d5ce)로 병합됐습니다. Vercel 운영 배포 `dpl_7bmqdcSgvuvDfPJqUcSSEcWH81rE`의 상태는 `READY / production / main`, 연결 커밋은 정확히 `31d9dda`입니다.
- [PR #185](https://github.com/dohyunkimmm/mosigo-case-study/pull/185)는 **2026-11-20 미병합 종료**했습니다. 구 자동 생성본 HEAD `d9a045940bb7ce4ef8712d1c3b5add42c04f06f3`, PPTX blob `c40c42a510cdb16f86395b43701befe383df2067`입니다. 생성 당시 기반 PPTX blob `b2021df0344fdd0dd1c074733b4fe0fe29519a95`와 최신 `main` blob `2fa0e3ccf953d0e6a58f956df73b044f5fa99da8`이 서로 다릅니다.
- 후속 병합된 [#184](https://github.com/dohyunkimmm/mosigo-case-study/pull/184)에서 PPTX·PDF·미리보기 원본을 교체했으며, [#188](https://github.com/dohyunkimmm/mosigo-case-study/pull/188)에서 PPTX·PDF·미리보기를 다시 변경하고 **Site QA, PRD QA, 모바일 QA 및 문서 생성/변환 검사에 성공**했습니다. 따라서 오래된 PR의 바이너리를 현재 `main`에 덮어쓰지 않습니다. **두 바이너리의 텍스트·화면·바이트 동등성은 검증되지 않았습니다.**
- **SHA 태그 보존·브랜치 정리 완료:** [검증 Actions #44688351175](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/44688351175) **성공**. `archive/closed/20261120/pr-185/automation/ppt-preview-44210022466-1`의 Git ref가 PR 원본 SHA `d9a045940bb7ce4ef8712d1c3b5add42c04f06f3`와 일치함을 재조회했습니다. 동일 SHA에 있던 `automation/ppt-preview-44210022466-1` 브랜치 참조는 삭제됐고, 기존 검토 브랜치 3개(`fix/pilot-review-criteria`, `review/document-audit-20261117`, `review/mosigo-opening-copy`)는 보존했습니다. 종료된 PR #185 재병합은 하지 않았습니다. 이 정리 PR에서는 완료된 일회성 `.github/workflows/archive-pr-185-once.yml`을 제거합니다.
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
