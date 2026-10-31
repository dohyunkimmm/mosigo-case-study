# 원격 브랜치 보존·정리 기록 (2026-10-31)

저장소: `dohyunkimmm/mosigo-case-study`

아래 브랜치는 2026-10-31 기준 main과 비교했습니다. 브랜치를 단순 삭제하지 않고 **원래 HEAD 커밋을 같은 이름의 `archive/20261031/...` 태그로 보존한 다음** 브랜치 참조만 삭제하도록 자동화합니다.

| 기존 브랜치 | 삭제 전 고유 커밋 수 | 보존 태그 | HEAD SHA |
| --- | ---: | --- | --- |
| `business-plan/new-20261031` | 10 | `archive/20261031/business-plan/new-20261031` | `0ca22c4d4d5d94bdf67bce86d4f2ce6339e6d5a0` |
| `case-study/add-notion-original-business-plan-20261031` | 4 | `archive/20261031/case-study/add-notion-original-business-plan-20261031` | `16304489641a0e1d97022e34b1c6e884d6ea9e70` |
| `case-study/notion-plan-jd-decision-20261031` | 1 | `archive/20261031/case-study/notion-plan-jd-decision-20261031` | `a13833c30030f93d94cd8960d7509edeaf954d7d` |
| `chore/qa-repo-cleanup-20261031` | 4 | `archive/20261031/chore/qa-repo-cleanup-20261031` | `a2699be376676667c828ea35a2c8bd0f40f0354b` |
| `portfolio/decision-memos-20261030` | 4 | `archive/20261031/portfolio/decision-memos-20261030` | `be50960538e7b0d380e6b8c524060da8cef93e4e` |
| `portfolio/forecast-management-20261030` | 8 | `archive/20261031/portfolio/forecast-management-20261030` | `5f8d1fa575f1bae0f1b3bcb60f866cb3a43245f0` |
| `portfolio/independent-materials-20261030` | 6 | `archive/20261031/portfolio/independent-materials-20261030` | `fda9bc9d237a0cfa1285830701b36f0fa933180b` |
| `portfolio/inline-analysis-20261030` | 1 | `archive/20261031/portfolio/inline-analysis-20261030` | `dfa84fcd761354d7d198ee4dbb80228247229f36` |
| `portfolio/native-downloads-20261030` | 1 | `archive/20261031/portfolio/native-downloads-20261030` | `030b461cf6f65e2c515794ae65fa32ead56b9b12` |
| `portfolio/report-pager-20261030` | 1 | `archive/20261031/portfolio/report-pager-20261030` | `efad5ede811a40e874b6617682d83d6d9fdc64d9` |
| `qa/mosigo-business-plan-approved-fixes-20261031` | 3 | `archive/20261031/qa/mosigo-business-plan-approved-fixes-20261031` | `d21ceb594ca13978111aefd704971fd41995f4d4` |
| `test/case-study-table-count-20261031` | 1 | `archive/20261031/test/case-study-table-count-20261031` | `6c7b235a5a940b289fef00dee541091c2a0b8eae` |

## 안전 조건

- 정리 직전 HEAD가 위 SHA와 정확히 같지 않으면 삭제하지 않습니다.
- 열린 PR이 있으면 삭제하지 않습니다.
- 보존 태그 생성 뒤 같은 SHA임이 검증되지 않으면 삭제하지 않습니다.
- `main`, 제품 파일, 과거 커밋 자체는 삭제하지 않습니다.
- 복원할 때는 `archive/20261031/<기존 브랜치>` 태그에서 새 브랜치를 만들 수 있습니다.
- 태그로 보존했다고 해서 미병합 코드를 현재 `main`에 적용하는 것은 아닙니다.
- 작업 로그는 GitHub Actions **Retire audited branches (one time)**에서 확인합니다.
