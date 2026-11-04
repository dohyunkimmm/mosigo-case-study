# MOSIGO Case Study 저장소 정합성 점검 (2026-11-03)

## 점검 기준

- 대상: `dohyunkimmm/mosigo-case-study`의 `main`.
- 기준 커밋: `018f4f2c515fc1b4ff115a47ff29f4ae9f322eec` (2026-11-03 09:25 KST).
- GitHub API의 재귀 트리, README, `index.html`, 자산 스크립트, 문서 미리보기, 브랜치/PR, GitHub Actions 결과를 대조했다.
- 이 점검은 **GitHub에 올라온 파일과 배포 QA 기록**의 대조다. 사용자 로컬 PC의 미커밋 파일은 검사할 수 없다.

## 메인 파일·폴더

| 범위 | 파일 수 | 점검 |
| --- | ---: | --- |
| 루트 | 7 | `index.html`, `README.md`, `.gitignore`, `favicon.svg`, 기존 URL 호환 HTML 3개 |
| `.github/workflows/` | 13 | 기존 자동화는 유지 |
| `assets/` | 4 | CSS·JS·공유 이미지·토스페이스 이미지 |
| `downloads/` 최상위 | 7 | PDF 3개, PPTX 2개, XLSX 1개, HTML 1개 |
| `downloads/previews/` | 80 | 사업기획서 34개, 발표자료 22개, IR 24개 |
| `qa/` 바로 아래 | 18 | 검증 및 문서 생성 스크립트·기록 |
| `qa/ir-deck-source/` | 5 | IR 생성 워크플로에서 복원하는 Base64/Brotli 소스 조각 |
| **합계** | **134** | 디렉터리 7개 별도 |

- Git 트리에서 **동일 blob SHA를 공유하는 중복 파일은 0개**다. 같은 디자인이나 유사한 이름이 중복 콘텐츠라는 뜻은 아니다.
- `index.html`의 메인 목차 9개는 각각 대응 섹션 ID를 갖는다. 직접 참조하는 저장소 내부 정적 경로에서 없는 파일을 발견하지 않았다.
- `index.html`의 문서 탭 설정은 사업기획서 17쪽, 발표자료 11장, IR Deck 12장이다. 각 쪽/장마다 일반 및 소형 WebP가 한 쌍씩 있어 총 **80개 모두 존재**한다.
- `decision-memos.html` → `/#decision`, `forecast.html` → `/#business`, `materials.html` → `/#attachments`는 기존 URL 호환을 위한 파일이므로 삭제하지 않는다.
- `qa/ir-deck-source/0*.txt`는 [IR Deck 생성 워크플로](../.github/workflows/ir-deck.yml)의 복원 입력이다. 랜덤한 문자열처럼 보이지만 생성 과정에서 쓰이므로 삭제하지 않는다.

## 검증 실행 상태

- [Site QA (run 41552752510)](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/41552752510): 기준 `main` 커밋에서 **success** (2026-11-03).
- [Mobile Safari engine and font QA (run 41552752466)](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/41552752466): 동일 커밋에서 **success**.
- 배포 HTML의 GitHub 버전 일치 검사는 `Site QA`에 포함된다. 독립적인 수동 실기기 시험을 완료했다는 뜻은 아니다.

## 아직 main에 반영되지 않았거나 후속 판단이 필요한 항목

1. **[PR #18 — 운영 예외 README](https://github.com/dohyunkimmm/mosigo-case-study/pull/18)**: 2026-11-03 확인 시 `open`, `merged=false`. `main`과 비교 시 고유 커밋 3개, `main` 뒤처짐 85개이며 GitHub가 `mergeable=false`를 반환했다. README에 무료·비공개 저장소의 main 보호 미적용과 보완 QA 절차 6줄을 추가하는 변경이다. 미반영 문서이므로 최신 main에 맞춰 검토 후 별도 처리해야 한다. 현재 자료·다운로드 누락은 아니다.
2. **잔여 QA 브랜치 `chore/qa-static-route-coverage-20261101`**: 연결된 [PR #17](https://github.com/dohyunkimmm/mosigo-case-study/pull/17)은 병합됐다. 브랜치 참조는 남아 있고 `main` 대비 ahead 3 / behind 94다. 최신 `main`의 QA 스크립트는 이후에도 변경됐으므로 과거 브랜치를 그대로 다시 병합하거나, 검토 없이 삭제하지 않는다.
3. **잔여 PR 브랜치 `docs/free-private-repo-qa-exception-20261101`**: PR #18의 작업 브랜치다. PR이 열려 있는 동안 삭제하지 않는다.
4. **기존 브랜치 정리 기록**: [2026-10-31 보존·정리 문서](branch-retirement-20261031.md)는 14개 아카이브 태그 보존 및 당시 `main` 단일 브랜치 상태를 기록한다. 이는 당시 스냅샷으로, 2026-11-03 현재 브랜치 개수가 1개라는 뜻이 아니다.

## 후속 반영 경위 (2026-11-03)

- [PR #19](https://github.com/dohyunkimmm/mosigo-case-study/pull/19)의 README 파일·폴더 색인 및 본 점검 기록은 `d7b71904fd08da00e07a213db286d9f5bcfc67e9`로 `main`에 병합됐다.
- 원본 [PR #18](https://github.com/dohyunkimmm/mosigo-case-study/pull/18)은 이전 브랜치의 `Site QA / browser-and-lighthouse`에서 실패했다([run 41292993495](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/41292993495)). 따라서 이전 브랜치의 전체 변경·문서 상태를 그대로 병합하지 않는다.
- PR #18에 남았던 운영 안내 6줄은 **현재 `main` 기반의 새 작업에서 README에 다시 반영**했다. 해당 새 PR의 QA 성공·병합 여부와 기존 PR #18의 종료 상태는 GitHub PR 기록을 기준으로 확인한다.
- `main` 브랜치의 보호 설정은 GitHub API에서 `protected=false`로 확인했다. 무료·비공개 제약에 대한 실행 절차는 별도 운영 지침이며 GitHub의 서버 측 푸시 차단을 의미하지 않는다.
- 과거 QA·정리 브랜치는 참조가 남아 있더라도 **현재 `main`에 필요한 내용이 누락됐다는 증거가 아니다**. 보존 태그/HEAD 확인 없이 삭제하거나 다시 병합하지 않는다.

## 이번 정리의 경계

- README에 **메인 페이지, 파일·폴더, 다운로드 원본/게시본**을 빠르게 찾을 수 있는 색인을 추가했다.
- 존재하지 않는 첨부 링크나 누락된 미리보기 파일은 발견되지 않아 PDF/PPTX/XLSX/WebP를 재생성하거나 이동하지 않았다.
- 보고서 본문, 배포 경로, 제품 저장소, 생성 워크플로, 과거 보관 태그·브랜치 이력은 수정하지 않았다.
- 열린 PR과 잔여 브랜치는 **미반영·잔여 작업으로 기록**하되, 충돌 가능성/복원 가능성 확인 없이 강제 병합하거나 삭제하지 않았다.

---

## 2026-11-04 후속 점검 · 최신 메인과 병합 브랜치

> 위 2026-11-03 기록은 당시 스냅샷으로 보존합니다. 아래 내용의 조회 기준 `main`은 `6fb8ee2d9ca9787fdc467ba9a4676dc58a3fc721`입니다. 이번 문서 변경과 이후 자동화 실행은 별도 후속 사건입니다.

- 재귀 트리: **136개 파일·7개 디렉터리**(11월 3일 기록: 134개 파일·7개 디렉터리). 동일 blob SHA를 쓰는 파일 **0개**이며, 기존 9개 보고서 섹션·문서 미리보기 80개·호환 URL은 보존 대상입니다.
- 열린 PR **0개**. 기존 [PR #18](https://github.com/dohyunkimmm/mosigo-case-study/pull/18)은 병합 없이 종료됐으며, 필요한 운영 안내는 후속 [PR #20](https://github.com/dohyunkimmm/mosigo-case-study/pull/20)으로 반영됐습니다.
- 원격 브랜치 **3개**: `main`, `design/case-study-visual-qa-20261103`, `fix/mosigo-editorial-slide-layout-20261104`. 뒤의 두 브랜치는 각각 [PR #23](https://github.com/dohyunkimmm/mosigo-case-study/pull/23)·[PR #24](https://github.com/dohyunkimmm/mosigo-case-study/pull/24)로 병합됐지만 현재 `main`과 분기되어 있습니다. 이전 내용을 재병합하지 않습니다.
- 두 원본 HEAD는 각각 `667c68f52e80700942f886ec39da800a34748d56`, `039a6f104c71e4974a56a1ddf2c71d0ca1e2be36`입니다. 정리 시 **PR 병합 여부·원본 HEAD 동일성·열린 PR 부재**를 재검증하고 원본 SHA의 `archive/20261104/` 태그가 존재함을 확인한 뒤에만 브랜치 ref를 삭제합니다. 한 항목이라도 불일치하면 해당 브랜치는 보존합니다.
- 현행 `main` 직전 커밋 `89d867a`의 [Site QA #41739650533](https://github.com/dohyunkimmm/mosigo-case-study/actions/runs/41739650533)·모바일 Safari QA는 성공했습니다. 이후 자동생성 IR Deck 게시 커밋 `6fb8ee2` **그 자체에 연결된 Site QA 실행은 조회되지 않았습니다**. 따라서 이번 정리 PR에서 검증하고, 병합된 `main`의 Site QA·배포 일치 결과도 별도 확인해야 합니다.
- 비공개 저장소의 `main`은 `protected=false`입니다. QA 선행 병합 절차가 서버 측 강제 보호를 제공하는 것처럼 표현하지 않습니다.
- 이 점검은 저장소 원격 상태·워크플로 기록만 확인합니다. 실제 모바일 기기 실측이나 로컬 미커밋 파일 검사를 주장하지 않습니다.
