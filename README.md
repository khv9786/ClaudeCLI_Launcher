# ClaudeCLI Launcher

지정한 프로젝트 경로에서 Claude CLI를 터미널로 자동 실행하는 Windows 런처입니다.

## 사용법

1. `dist/ClaudeLauncher.exe` 실행
2. **찾아보기** 버튼으로 프로젝트 폴더 선택 (또는 경로 직접 입력)
3. **저장** — 경로를 기억합니다 (다음 실행 시 자동 로드)
4. **▶ Claude 실행** — 해당 경로에서 CMD 창이 열리고 `claude` 명령이 실행됩니다

## 요구사항

- Windows 10/11
- [Claude CLI](https://docs.anthropic.com/ko/docs/claude-cli) 설치 및 PATH 등록

## EXE 직접 빌드

Python 환경에서 아래 명령으로 재빌드할 수 있습니다.

```bash
pip install pillow pyinstaller
python build_exe.py
```

빌드 결과물은 `dist/ClaudeLauncher.exe`에 생성됩니다.
