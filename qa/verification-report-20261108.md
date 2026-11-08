# MOSIGO QA 검증 기록 · 2026-11-08

## 대상과 경계
- 대상: MOSIGO 서비스기획·PRD 포트폴리오와 연결된 MOSIGO 프로토타입.
- 제품 테스트 기준 커밋: [978ef8bc](https://github.com/dohyunkimmm/mosigo/commit/978ef8bc2e00e772a5a5ddad87584bb97451e4cb).
- 본 문서는 자동화 검사와 화면·문서 검증 기록입니다. 실제 고객 UAT, 의료기관 예약, 결제, 현장 매니저 배정·인수 승인을 뜻하지 않습니다.

## 확인된 검증
| 영역 | 확인 결과 | 증빙 |
| --- | --- | --- |
| 제품 Node 자동 테스트 | 176건 통과 / 실패 0건 | [PRD Evidence QA](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42447455997) |
| 소스 구조 점검 | 통과 | 같은 실행의 `source-audit.log` |
| 실운영 API 읽기 전용 스모크 | 1회차 통과, 기록 생성·수정 없음 | 같은 실행의 `live-smoke.log` |
| PRD 문서 | R-01~06(6개), TC(11개), UAT 계획(5개·미실시) 검증 | [PRD 브라우저 스크립트](./prd-browser.mjs) |
| PRD 반응형 | 320·390·768·1440px 검사 모두 통과 | [Site QA 실행 기록](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/42447004496) |
| 사업기획서·발표자료·IR | PDF 19·11·12쪽 및 Pretendard 포함 확인 | 같은 Site QA 실행의 로그 |
| 문서 뷰어/반응형 | 브라우저 자동화의 탭 전환·미리보기·기본 동작 검사 | [사이트 검사 스크립트](./smoke.mjs) |

## 발견·수정한 문제
1. PRD의 정상 용어인 '수용 기준'을 금지 문구로 취급하던 문서 QA 검사 오탐을 정정.
2. 간결화된 SOM 설명과 11장 발표자료의 최신 문구를 검사 조건에 반영.
3. PDF 17쪽은 시각적으로 정상이나 텍스트 추출 순서가 제목과 부제목을 섞어 추출하므로, 제목은 HTML 원본에서, 부제목은 PDF에서 대조.
4. 손익 비교 영역 작은 설명 글자의 색 대비 약 4.39:1 문제를 CSS 글자색 조정으로 약 4.98:1로 개선(WCAG AA 최소 4.5:1).
5. PRD 화면 브라우저 검증 스크립트를 추가해 작은 화면의 가로 넘침·긴 표 스크롤·QA/UAT 표기를 검사.

## 미검증·승인 범위
- 실제 고객/운영자 UAT 5개 시나리오는 미실시. 참여자·결과·서명 없음.
- 실제 병원 예약·결제·매니저 배정·운영 계약·의료정보 처리와 현장 인수는 미구현 또는 별도 검증.
- 배포 시각·기기·네트워크에 따라 Lighthouse 점수는 달라질 수 있습니다. 성능 점수는 합성 측정값입니다.

최종 CI 성공 여부는 [Site QA 워크플로](https://github.com/dohyunkimmm/mosigo-case-study/actions/workflows/site-qa.yml)의 해당 커밋 검사 기록으로 판단합니다. 검사 코드 변경 자체를 QA 통과로 간주하지 않습니다.
