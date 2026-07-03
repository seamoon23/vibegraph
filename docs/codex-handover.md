# Codex Handover

## Project

vibegraph

## Project Root

```text
C:\codex\app\vibegraph
```

## Goal

아이디어·작업 흐름·프롬프트·실행 단계를 그래프/트리 형태로 관리하는 개인 생산성 프로젝트.

## Current Situation

- 기존 app 하위 대화 vibeGraph__upgrade는 이 프로젝트로 요약만 이관한다.
- 앞으로는 C:\codex\app\vibegraph 폴더만 프로젝트 루트로 사용한다.

## Do Not Touch

```text
C:\codex\app
C:\codex\app\AiPacer
C:\codex\app\BlockObbyMvp
C:\codex\app\niceQR
C:\codex\app\PocketGallery
C:\codex\app\sonsapps
C:\codex\app\sontube
C:\codex\app\vibegraph
```

단, 위 목록 중 현재 프로젝트 폴더만 수정 가능하다.

## Migration Note

이 문서는 기존에 `C:\codex\app` 상위 프로젝트 또는 이름이 섞인 Codex 프로젝트에서 진행된 대화를 정리하고, 앞으로 실제 프로젝트 폴더 기준으로 새로 시작하기 위한 인계 문서다.

## Next Tasks

- [ ] 현재 라우트/화면 구조 확인
- [ ] 그래프/트리 데이터 모델 정리
- [ ] MVP 범위와 후속 플러그인 구조 분리
- [ ] README와 실행 명령 정리

## First Prompt For New Codex Chat

```text
이 프로젝트 루트는 C:\codex\app\vibegraph 입니다.

상위 C:\codex\app 폴더와 형제 프로젝트는 수정하지 마세요.
작업 전 pwd, git status, 주요 폴더 구조를 먼저 확인하세요.
그다음 현재 프로젝트 상태와 수정 대상 파일 목록을 제안해 주세요.

현재 목표:
아이디어·작업 흐름·프롬프트·실행 단계를 그래프/트리 형태로 관리하는 개인 생산성 프로젝트.
```
