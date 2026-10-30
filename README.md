# 개인 Strategy Case Study · 병원동행 신사업

https://mosigo-case-study.vercel.app/

**개인이 독립적으로 작성한 전략기획·IT기획·PM 케이스 스터디**입니다. 병원동행 시장을 대상으로 고객 문제, 사업 기회, 제품·운영 구조, 수익모델, KPI와 실행 의사결정을 분석합니다.

## 출처와 작성 범위

- **Case Study 작성 주체: 개인 1명.** 본문의 전략 선택, 시장규모 산출 논리, 가격·수익모델 비교, 서비스 블루프린트, 우선순위·KPI·검증 계획은 독립 분석 결과입니다.
- **직무 분석 근거: 2026.07.30~10.30 사람인 채용공고 7건.** 각 공고의 담당업무·자격요건·우대사항을 읽고 필요한 분석 산출물과 연결합니다.
- **사례 자료: 기존 MOSIGO 기록.** 경쟁 앱 7종·리뷰 118건 조사 범위, 가입~재예약 흐름, 19개 모달·상태 화면, 예약·복구·공유 및 운영 화면의 구현 사실을 사례 근거로만 사용합니다. 기존 프로젝트와 본 독립 Case Study의 작성 주체를 혼동하지 않습니다.
- **MOSIGO 연결:** [데모 링크](https://mosigo-nine.vercel.app/) **1개만 유지**하며 페이지를 복제하거나 임베드하지 않습니다. 원본 데모 파일과 저장소는 수정하지 않습니다.

## 본문

1. 문제·시장 기회와 분석 범위
2. 시장조사 인사이트, TAM–SAM–SOM 산출 로직
3. 고객·이해관계자별 Job Story
4. 대안 비교와 고객·제품 전략
5. IA·정책·예외, Service Blueprint
6. 가격·상품 전략과 거래액·공헌이익 민감도 계산기
7. 우선순위·실행 게이트·승인 판단
8. 이벤트·KPI·QA·UAT 설계
9. 최종 사업화 판단과 채용 역량 대응

섹션 수는 고정하지 않습니다. 자료의 중복을 줄이고 필요에 따라 조정합니다.

## 사람인 채용공고 근거

- [비트컴퓨터 · 헬스케어 신사업 기획/PM (2026.10.18)](https://www.saramin.co.kr/api/jobs/job/content?rec_idx=55321685): 사업기회 발굴, 사업성·우선순위·제품 추진 여부
- [가디언에이아이 · PM/PO (2026.08.11)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54715612): 프로세스·IA·정책·예외조건·인수 기준
- [엑스커머스 · 서비스기획 (2026.08.26)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54856049): PRD, BM, KPI, QA, 퍼널·GA4 분석
- [에이치알그룹 · 서비스기획 PM (2026.08.26)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54856895): 서비스·정책 문서, PM 업무
- [씨엠티엑스 · 전략기획 (2026.08.03)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54633762): 산업 리서치, 데이터 분석, 전략 보고
- [에이치이엠파마 · 전략기획 (2026.08.14)](https://m.saramin.co.kr/job-search/view?rec_idx=54747109): 손익·BEP, Feasibility Study, KPI
- [어댑티브 · PM/전략기획 (2026.08.04)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=54646531): PM, 과제 실행·관리

이는 일부 공고의 **정성적 요구 역량 비교**입니다. 경력·자격 보유나 실제 운영 성과를 자동으로 입증하는 자료는 아닙니다.

## 자료의 해석

- 원본 MOSIGO 조사 수치와 교육 당시 산출물은 기존 자료의 범위입니다. 본 Case Study가 같은 조사·개발을 새로 혼자 수행했다고 기술하지 않습니다.
- 기존 사업기획서의 평균 이용 횟수, 건당 가격, 기본 동행·차량 동행·구독료는 **사업 시나리오 가정**입니다.
- TAM/SAM 원자료와 실제 지역별 공급·이용자 전환·원가는 확정되지 않아 무근거 시장 규모나 수익 실적을 생성하지 않습니다.
- 정책, KPI, 실험 게이트와 서비스 블루프린트는 개인의 전략 설계안이며 실제 의료 서비스를 운영했다는 의미가 아닙니다.

## 디자인·배포

Pretendard Variable · Tossface. [Pretendard](https://github.com/orioncactus/pretendard), [Tossface 라이선스](https://github.com/toss/tossface/blob/main/LICENSE). 독립 HTML 정적 사이트입니다.
