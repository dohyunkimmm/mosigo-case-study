# MOSIGO Strategy Case Study

https://mosigo-case-study.vercel.app/

병원동행 서비스 MOSIGO를 기반으로 작성한 **전략기획·IT 서비스 기획·PM 케이스 스터디**입니다. 서비스 데모를 복제하거나 화면을 삽입하지 않습니다. 원본은 [별도 링크](https://mosigo-nine.vercel.app/)로만 제공합니다.

## 핵심 구성

- 프로젝트 근거와 시장 조사 범위
- 고객 역할·Job Story, 예약 방식별 전략 대안 비교
- 사용자 여정·IA·권한/예외 정책·인수 기준과 실제 코드·테스트 근거
- 직접 제공형·중개형의 사업성 시나리오와 민감도 계산기
- 실행 우선순위, 단계별 산출물·통과 조건, QA·KPI·퍼널 측정 설계
- 사업화 의사결정과 최근 IT기획·전략기획·PM 공고 역량 대응

**판단 자료의 구분:** ‘원본 구현·테스트’, ‘팀 조사’, ‘후속 전략 분석’, ‘검증 계획’을 나눠 표현합니다. 전략 대안 비교와 게이트 통과 기준은 당시 팀의 공식 의사결정·실행 결과가 아닌 후속 검토안입니다.

**원본 증거:** 공개 [예약 API](https://github.com/dohyunkimmm/mosigo/blob/main/src/api/bookings.js), [공유 권한 테스트](https://github.com/dohyunkimmm/mosigo/blob/main/tests/share-write-policy.test.js), [운영 화면 테스트](https://github.com/dohyunkimmm/mosigo/blob/main/tests/operations.test.js), [실기기 QA 계획](https://github.com/dohyunkimmm/mosigo/blob/main/docs/DEVICE-QA-RUNBOOK.md)을 연결합니다.

콘텐츠 구성은 필요에 따라 조정합니다. 본문 섹션 수를 목표치로 고정하지 않습니다.

## 채용공고 근거

2026.07.30~10.30 게시 기준으로 사람인에 기재된 IT기획·전략기획·PM 사례를 참고했습니다. 세부 요구 역량과 원문 링크는 케이스 스터디 마지막 부분에 표시합니다.

- [비트컴퓨터 · 헬스케어 신사업 기획·PM (10.18)](https://www.saramin.co.kr/api/jobs/job/content?rec_idx=55321685)
- [가디언에이아이 · PM/PO (08.11)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54715612)
- [엑스커머스 · 서비스기획 (08.26)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54856049)
- [에이치알그룹 · 서비스기획 PM (08.26)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54856895)
- [씨엠티엑스 · 전략기획 (08.03)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54633762)
- [에이치이엠파마 · 전략기획 (08.14)](https://m.saramin.co.kr/job-search/view?rec_idx=54747109)
- [어댑티브 · PM/전략기획 (08.04)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54646531)

표본 7개 공고를 확인한 것이며 전체 직무 요구 역량이나 우대항목의 빈도 통계는 아닙니다. 근무 경력, Figma·Excel·PowerPoint 숙련, 실제 고객 인터뷰·GA4 운영·실무 리딩 등 입증되지 않은 역량은 포트폴리오에서 보유 실적으로 주장하지 않습니다.

## 증빙과 한계

- 원본 코드·README: https://github.com/dohyunkimmm/mosigo
- 전략기획 원본 기록: https://app.notion.com/p/40821460c934818581dcfa22dfc3cbef
- 경쟁 앱 7종·리뷰 118건은 교육 당시 팀 조사 범위입니다. 원문별 수치 검증은 별도입니다.
- 현재는 실병원 예약·실결제·의료 판단이 없는 프로토타입입니다.
- 수익성·KPI·실행 게이트는 후속 검토용 가정과 설계입니다. 실적이 아닙니다.
- 원본의 자동 테스트와 QA 기록은 참고하되, 실기기 사용성 검증·운영 성과로 혼동하지 않습니다.

## 디자인

Pretendard Variable · Tossface 이모지. [Pretendard](https://github.com/orioncactus/pretendard) / [Tossface·라이선스](https://github.com/toss/tossface/blob/main/LICENSE). HTML 정적 사이트로 빌드 과정 없이 배포합니다.

원본 MOSIGO GitHub·Vercel 프로젝트는 수정하지 않았습니다. Case Study의 데모 링크는 원본 프로덕션 주소로 연결되므로 원본 배포 업데이트를 그대로 방문할 수 있습니다. 케이스 스터디 분석 내용은 검증을 거쳐 별도로 갱신합니다.
