"""
build_exe.py
  1. claude 아이콘.png → claude_icon.ico 변환
  2. PyInstaller로 EXE 빌드
"""

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH = os.path.join(BASE_DIR, 'claude 아이콘.png')
ICO_PATH = os.path.join(BASE_DIR, 'claude_icon.ico')
SCRIPT   = os.path.join(BASE_DIR, 'claude_launcher.py')
DIST_DIR = os.path.join(BASE_DIR, 'dist')


def convert_png_to_ico():
    from PIL import Image
    img = Image.open(PNG_PATH).convert('RGBA')
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icons = [img.resize(s, Image.LANCZOS) for s in sizes]
    icons[0].save(ICO_PATH, format='ICO', sizes=sizes,
                  append_images=icons[1:])
    print(f'[OK] ICO 생성: {ICO_PATH}')


def build():
    if not os.path.exists(PNG_PATH):
        sys.exit(f'[ERROR] 아이콘 파일 없음: {PNG_PATH}')

    convert_png_to_ico()

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        f'--icon={ICO_PATH}',
        f'--add-data={ICO_PATH};.',   # 작업표시줄 아이콘용 ICO 번들
        '--name=ClaudeLauncher',
        '--distpath', DIST_DIR,
        '--workpath', os.path.join(BASE_DIR, 'build_tmp'),
        '--specpath', BASE_DIR,
        SCRIPT,
    ]
    print('[BUILD]', ' '.join(cmd))
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        sys.exit('[ERROR] PyInstaller 빌드 실패')

    exe = os.path.join(DIST_DIR, 'ClaudeLauncher.exe')
    if os.path.exists(exe):
        print(f'\n[DONE] EXE 생성 완료:\n  {exe}')
    else:
        print('[ERROR] EXE 파일을 찾을 수 없습니다.')


if __name__ == '__main__':
    build()
