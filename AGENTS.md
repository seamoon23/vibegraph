# AGENTS.md

## Project Identity

- Project: vibegraph
- Root: `C:\codex\app\vibegraph`
- Goal: 아이디어·작업 흐름·프롬프트·실행 단계를 그래프/트리 형태로 관리하는 개인 생산성 프로젝트.

## Hard Rules

- 이 프로젝트 루트 밖의 파일은 수정하지 않는다.
- `C:\codex\app` 상위 폴더를 프로젝트 루트로 간주하지 않는다.
- 형제 프로젝트 폴더를 읽거나 수정하지 않는다. 필요한 경우 먼저 사용자에게 확인한다.
- 작업 전 반드시 현재 경로, Git 상태, 주요 파일 구조를 확인한다.
- 큰 변경 전에는 수정 대상 파일 목록과 변경 계획을 먼저 제시한다.
- 불필요한 리팩토링, 포맷팅, 대규모 파일 이동을 하지 않는다.
- 잠금 파일은 실제 의존성 변경이 있을 때만 수정한다.
- 비밀키, 토큰, 계정 정보, 개인 정보는 코드나 문서에 저장하지 않는다.

## Start Checklist

```powershell
pwd
git status
Get-ChildItem -Force
```

## Preferred Workflow

1. 현재 구조와 실행 방식을 요약한다.
2. 수정 대상 파일 목록을 제안한다.
3. 작은 단위로 변경한다.
4. 변경 후 실행/빌드/테스트 결과를 요약한다.
5. 다음 작업 후보를 짧게 제안한다.

## Commit Policy

- 사용자가 명시하기 전에는 커밋/푸시하지 않는다.
- 커밋 전에는 `git diff` 요약을 제공한다.
- 커밋 메시지는 작업 의도가 드러나게 작성한다.

## Project Notes

- 기존 app 하위 대화 vibeGraph__upgrade는 이 프로젝트로 요약만 이관한다.
- 앞으로는 C:\codex\app\vibegraph 폴더만 프로젝트 루트로 사용한다.
