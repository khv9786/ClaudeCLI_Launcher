import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import subprocess

NAME_PLACEHOLDER = '명칭 입력'
NAME_PLACEHOLDER_FG = '#777777'
NAME_NORMAL_FG = '#ffffff'


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
    config = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}
    if 'paths' not in config:
        # 구버전(project_path 단일 경로) 설정 마이그레이션
        legacy = config.get('project_path', '')
        config['paths'] = [{'name': '', 'path': legacy}] if legacy else []
        config.pop('project_path', None)
    return config


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
        self.rows = []

        self._build_ui()
        self._center_window()

    def _build_ui(self):
        outer = tk.Frame(self.root, bg='#1e1e1e', padx=18, pady=14)
        outer.pack(fill='both', expand=True)

        tk.Label(outer, text='프로젝트 경로', bg='#1e1e1e', fg='#cccccc',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')

        self.rows_container = tk.Frame(outer, bg='#1e1e1e')
        self.rows_container.pack(fill='x', pady=(4, 10))

        paths = self.config.get('paths', [])
        if paths:
            for item in paths:
                self._add_row(item.get('path', ''), item.get('name', ''), resize=False)
        else:
            self._add_row(resize=False)

        tk.Button(
            outer, text='+ 추가', command=lambda: self._add_row(),
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', padx=8, cursor='hand2'
        ).pack(anchor='w')

        sep = tk.Frame(outer, height=1, bg='#3a3a3a')
        sep.pack(fill='x', pady=(10, 10))

        tk.Button(
            outer, text='저장', command=self._save,
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', cursor='hand2', padx=8
        ).pack(fill='x')

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'+{(sw - w) // 2}+{(sh - h) // 2}')

    def _resize_window(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.root.geometry('')
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def _add_row(self, path='', name='', resize=True):
        row_frame = tk.Frame(self.rows_container, bg='#1e1e1e')
        row_frame.pack(fill='x', pady=(0, 6))

        row = {'frame': row_frame}
        row['path_var'] = tk.StringVar(value=path)
        row['name_var'] = tk.StringVar(value=name)

        path_entry = tk.Entry(
            row_frame, textvariable=row['path_var'], width=40,
            font=('Segoe UI', 9), bg='#2d2d2d', fg='#ffffff',
            insertbackground='white', relief='flat', bd=4
        )
        path_entry.pack(side='left', fill='x', expand=True)

        tk.Button(
            row_frame, text='찾아보기', command=lambda: self._browse(row),
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', padx=8, cursor='hand2'
        ).pack(side='left', padx=(6, 0))

        name_entry = tk.Entry(
            row_frame, textvariable=row['name_var'], width=14,
            font=('Segoe UI', 9), bg='#2d2d2d', fg='#ffffff',
            insertbackground='white', relief='flat', bd=4
        )
        name_entry.pack(side='left', padx=(6, 0))

        row['name_placeholder_active'] = False

        def _name_focus_in(event, row=row, entry=name_entry):
            if row['name_placeholder_active']:
                row['name_placeholder_active'] = False
                row['name_var'].set('')
                entry.config(fg=NAME_NORMAL_FG)

        def _name_focus_out(event, row=row, entry=name_entry):
            if not row['name_var'].get().strip():
                row['name_placeholder_active'] = True
                row['name_var'].set(NAME_PLACEHOLDER)
                entry.config(fg=NAME_PLACEHOLDER_FG)

        name_entry.bind('<FocusIn>', _name_focus_in)
        name_entry.bind('<FocusOut>', _name_focus_out)

        if not name:
            row['name_placeholder_active'] = True
            row['name_var'].set(NAME_PLACEHOLDER)
            name_entry.config(fg=NAME_PLACEHOLDER_FG)

        tk.Button(
            row_frame, text='▶ 실행', command=lambda: self._run(row),
            font=('Segoe UI', 9, 'bold'), bg='#0078d4', fg='white',
            relief='flat', cursor='hand2', padx=6
        ).pack(side='left', padx=(6, 0))

        tk.Button(
            row_frame, text='삭제', command=lambda: self._remove_row(row),
            font=('Segoe UI', 9), bg='#3a3a3a', fg='#cccccc',
            relief='flat', padx=6, cursor='hand2'
        ).pack(side='left', padx=(6, 0))

        self.rows.append(row)
        if resize:
            self._resize_window()

    def _remove_row(self, row):
        row['frame'].destroy()
        self.rows.remove(row)
        if not self.rows:
            self._add_row()
        else:
            self._resize_window()

    def _browse(self, row):
        current = row['path_var'].get()
        initial = current if os.path.isdir(current) else os.path.expanduser('~')
        chosen = filedialog.askdirectory(initialdir=initial, title='프로젝트 폴더 선택')
        if chosen:
            row['path_var'].set(os.path.normpath(chosen))

    def _save(self):
        paths = []
        invalid = []
        for row in self.rows:
            path = row['path_var'].get().strip()
            if not path:
                continue
            name = '' if row['name_placeholder_active'] else row['name_var'].get().strip()
            if not os.path.isdir(path):
                invalid.append(name or path)
                continue
            paths.append({'name': name, 'path': path})
        self.config['paths'] = paths
        save_config(self.config)
        if invalid:
            messagebox.showwarning(
                '경고',
                '다음 경로는 유효하지 않아 저장되지 않았습니다:\n' + '\n'.join(invalid)
            )
        else:
            messagebox.showinfo('저장 완료', '경로가 저장되었습니다.')

    def _run(self, row):
        path = row['path_var'].get().strip()
        if not path:
            messagebox.showwarning('경고', '프로젝트 경로를 입력해주세요.')
            return
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
