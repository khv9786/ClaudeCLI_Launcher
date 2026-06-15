import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import subprocess


def resource_path(name):
    """PyInstaller 번들 시 _MEIPASS, 개발 시 스크립트 디렉토리에서 리소스 탐색."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


def get_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'claude_launcher_config.json')


def load_config():
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'project_path': ''}


def save_config(config):
    with open(get_config_path(), 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def launch_claude(path):
    if not os.path.isdir(path):
        messagebox.showerror('오류', f'경로가 올바르지 않습니다:\n{path}')
        return False
    # cwd=path 로 작업 디렉토리를 직접 지정 → 따옴표 파싱 문제 없음
    subprocess.Popen('start cmd /k claude', shell=True, cwd=path)
    return True


class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Claude 실행기')
        self.root.resizable(False, False)

        self.config = load_config()
        self.path_var = tk.StringVar(value=self.config.get('project_path', ''))

        self._build_ui()
        self._center_window()

    def _build_ui(self):
        outer = tk.Frame(self.root, bg='#1e1e1e', padx=18, pady=14)
        outer.pack(fill='both', expand=True)

        tk.Label(outer, text='프로젝트 경로', bg='#1e1e1e', fg='#cccccc',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')

        path_frame = tk.Frame(outer, bg='#1e1e1e')
        path_frame.pack(fill='x', pady=(4, 10))

        self.path_entry = tk.Entry(
            path_frame, textvariable=self.path_var, width=52,
            font=('Segoe UI', 9), bg='#2d2d2d', fg='#ffffff',
            insertbackground='white', relief='flat', bd=4
        )
        self.path_entry.pack(side='left', fill='x', expand=True)

        tk.Button(
            path_frame, text='찾아보기', command=self._browse,
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', padx=8, cursor='hand2'
        ).pack(side='left', padx=(6, 0))

        sep = tk.Frame(outer, height=1, bg='#3a3a3a')
        sep.pack(fill='x', pady=(0, 10))

        btn_frame = tk.Frame(outer, bg='#1e1e1e')
        btn_frame.pack(fill='x')

        tk.Button(
            btn_frame, text='저장', command=self._save, width=8,
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', cursor='hand2'
        ).pack(side='left')

        tk.Button(
            btn_frame, text='▶  Claude 실행', command=self._run, width=16,
            font=('Segoe UI', 9, 'bold'), bg='#0078d4', fg='white',
            relief='flat', cursor='hand2', padx=4
        ).pack(side='right')

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'+{(sw - w) // 2}+{(sh - h) // 2}')

    def _browse(self):
        current = self.path_var.get()
        initial = current if os.path.isdir(current) else os.path.expanduser('~')
        chosen = filedialog.askdirectory(initialdir=initial, title='프로젝트 폴더 선택')
        if chosen:
            self.path_var.set(os.path.normpath(chosen))

    def _save(self):
        path = self.path_var.get().strip()
        self.config['project_path'] = path
        save_config(self.config)
        messagebox.showinfo('저장 완료', '경로가 저장되었습니다.')

    def _run(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning('경고', '프로젝트 경로를 입력해주세요.')
            return
        self.config['project_path'] = path
        save_config(self.config)
        if launch_claude(path):
            self.root.iconify()


if __name__ == '__main__':
    root = tk.Tk()
    root.configure(bg='#1e1e1e')
    # 창 및 작업표시줄 아이콘 설정
    try:
        root.iconbitmap(resource_path('claude_icon.ico'))
    except Exception:
        pass
    app = App(root)
    root.mainloop()
