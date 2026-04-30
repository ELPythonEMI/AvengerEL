import sys, os, subprocess, platform, time
import ctypes
import ctypes.wintypes as wt

 
APP_NAME    = "AvengerEL"
APP_AUTHOR  = "realizzato da ELpythonEMI"
APP_VERSION = "1.0"


def find_chrome():
    os_name = platform.system()
    if os_name == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    elif os_name == "Darwin":
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    else:
        paths = [
            "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser", "/usr/bin/chromium",
        ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def get_screen_size():
    if platform.system() == "Windows":
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    else:
        try:
            result = subprocess.run(["xdpyinfo"], capture_output=True, text=True, timeout=3)
            for line in result.stdout.splitlines():
                if "dimensions:" in line:
                    dims = line.split()[1]
                    w, h = dims.split("x")
                    return int(w), int(h)
        except Exception:
            pass
        return 1920, 1080


def get_all_chrome_hwnds():
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    found = []

    def enum_cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if "Google Chrome" in title or "Chrome" in title:
            rect = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if (rect.right - rect.left) > 400 and (rect.bottom - rect.top) > 300:
                found.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return found


def position_window(hwnd, x, y, w, h):
    user32 = ctypes.windll.user32
    user32.ShowWindow(hwnd, 9)
    user32.MoveWindow(hwnd, x, y, w, h, True)


def launch_chrome_window(chrome, url, x, y, w, h):
    return subprocess.Popen([
        chrome, "--new-window",
        f"--window-position={x},{y}",
        f"--window-size={w},{h}",
        url
    ])


def wait_for_new_chrome_window(hwnds_before, max_attempts=20, delay=1.0):
    for attempt in range(max_attempts):
        time.sleep(delay)
        current = set(get_all_chrome_hwnds())
        new_hwnds = current - set(hwnds_before)
        if new_hwnds:
            print(f"  Nuova finestra trovata (tentativo {attempt+1})")
            return list(new_hwnds)[0]
    return None


def force_move_linux(pid, x, y, w, h, max_attempts=20, delay=1.0):
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(
                ["xdotool", "search", "--pid", str(pid), "--onlyvisible"],
                capture_output=True, text=True, timeout=3
            )
            wids = [wid for wid in result.stdout.strip().split() if wid]
            if wids:
                for wid in wids:
                    subprocess.run(["xdotool", "windowsize", wid, str(w), str(h)], timeout=2)
                    subprocess.run(["xdotool", "windowmove", wid, str(x), str(y)], timeout=2)
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False


def close_chrome_windows(hwnd_list):
    WM_CLOSE = 0x0010
    user32 = ctypes.windll.user32
    for hwnd in hwnd_list:
        if hwnd:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)


def show_divider_and_toggle(
    screen_w, screen_h,
    thickness=18, offset=0,
    chrome_hwnds=None,
    chrome_exe=None,
    url_bottom_left="chrome://newtab",
    url_bottom_right="chrome://newtab",
    x_left=0, w_left=None,
    x_right=None, w_right=None,
    h_divider_v=30,
):
    try:
        import tkinter as tk
        import threading

        if chrome_hwnds is None:
            chrome_hwnds = []
        if w_left is None:
            w_left = screen_w // 2
        if x_right is None:
            x_right = screen_w // 2
        if w_right is None:
            w_right = screen_w - x_right

 
        bar_visible    = [True]
        h_bar_visible  = [False]
        split_active   = [False]
        all_hwnds      = list(chrome_hwnds)
        bottom_hwnds   = [None, None]
        h_bar_win      = [None]

        H_DIVIDER  = 18
        half_h_top = screen_h // 2 - H_DIVIDER // 2
        y_bottom   = screen_h // 2 + H_DIVIDER // 2
        h_bottom   = screen_h - y_bottom

 
        bar = tk.Tk()
        bar.title(f"⚡ {APP_NAME} — {APP_AUTHOR}")
        bar.overrideredirect(True)
        bar.attributes("-topmost", True)
        bar.configure(bg="#1a1a1a")
        x_pos = (screen_w // 2) - (thickness // 2) + offset
        bar.geometry(f"{thickness}x{screen_h}+{x_pos}+0")
        canvas = tk.Canvas(bar, width=thickness, height=screen_h,
                           bd=0, highlightthickness=0, bg="#1a1a1a")
        canvas.pack(fill="both", expand=True)
        canvas.create_rectangle(0, 0, thickness, screen_h, fill="#05043a", outline="")
        cx = thickness // 2
        canvas.create_line(cx, 0, cx, screen_h, fill="#e0e0e0", width=1)

    
        canvas.create_text(
            cx, screen_h // 2,
            text=f"⚡ {APP_NAME}",
            fill="#e0e0e0",
            font=("Segoe UI", 8, "bold"),
            angle=90
        )

 
        def create_h_bar():
            hw = tk.Toplevel(bar)
            hw.overrideredirect(True)
            hw.attributes("-topmost", True)
            hw.configure(bg="#1a1a1a")
            y_h = screen_h // 2 - H_DIVIDER // 2
            hw.geometry(f"{screen_w}x{H_DIVIDER}+0+{y_h}")
            hc = tk.Canvas(hw, width=screen_w, height=H_DIVIDER,
                           bd=0, highlightthickness=0, bg="#05043a")
            hc.pack(fill="both", expand=True)
            hc.create_line(0, H_DIVIDER // 2, screen_w, H_DIVIDER // 2,
                           fill="#e0e0e0", width=1)
            return hw

  
        def toggle_bar():
            if bar_visible[0]:
                bar.withdraw(); bar_visible[0] = False
                btn_toggle.config(text="◼  Mostra barra", bg="#2d5a27")
            else:
                bar.deiconify(); bar.attributes("-topmost", True)
                bar_visible[0] = True
                btn_toggle.config(text="◻  Nascondi barra", bg="#5a2727")

    
        def toggle_h_bar():
            hw = h_bar_win[0]
            if hw is None: return
            if h_bar_visible[0]:
                hw.withdraw(); h_bar_visible[0] = False
                btn_h_toggle.config(text="◼  Mostra H-barra", bg="#2d5a27")
            else:
                hw.deiconify(); hw.attributes("-topmost", True)
                h_bar_visible[0] = True
                btn_h_toggle.config(text="◻  Nascondi H-barra", bg="#1a4a6a")

 
        def toggle_split():
            if not split_active[0]:
                # ── ATTIVA ×4 ──────────────────────────────────────────
                split_active[0] = True
                btn_split.config(state="disabled", text="⏳  Apertura…", bg="#444")

                def _open():
                    hwnd_l, hwnd_r = (all_hwnds + [None, None])[:2]
                    if hwnd_l: position_window(hwnd_l, x_left,  0, w_left,  half_h_top)
                    if hwnd_r: position_window(hwnd_r, x_right, 0, w_right, half_h_top)

                    os_name = platform.system()
                    if os_name == "Windows":
                        hb = get_all_chrome_hwnds()
                        launch_chrome_window(chrome_exe, url_bottom_left,
                                             x_left, y_bottom, w_left, h_bottom)
                        hwnd_bl = wait_for_new_chrome_window(hb)
                        if hwnd_bl:
                            position_window(hwnd_bl, x_left, y_bottom, w_left, h_bottom)
                            bottom_hwnds[0] = hwnd_bl
                            all_hwnds.append(hwnd_bl)

                        hb2 = get_all_chrome_hwnds()
                        launch_chrome_window(chrome_exe, url_bottom_right,
                                             x_right, y_bottom, w_right, h_bottom)
                        hwnd_br = wait_for_new_chrome_window(hb2)
                        if hwnd_br:
                            position_window(hwnd_br, x_right, y_bottom, w_right, h_bottom)
                            bottom_hwnds[1] = hwnd_br
                            all_hwnds.append(hwnd_br)

                    elif os_name == "Linux":
                        pl = launch_chrome_window(chrome_exe, url_bottom_left,
                                                  x_left, y_bottom, w_left, h_bottom)
                        time.sleep(2.5)
                        force_move_linux(pl.pid, x_left, y_bottom, w_left, h_bottom)

                        pr = launch_chrome_window(chrome_exe, url_bottom_right,
                                                  x_right, y_bottom, w_right, h_bottom)
                        time.sleep(2.5)
                        force_move_linux(pr.pid, x_right, y_bottom, w_right, h_bottom)
                    else:
                        launch_chrome_window(chrome_exe, url_bottom_left,
                                             x_left, y_bottom, w_left, h_bottom)
                        time.sleep(1.5)
                        launch_chrome_window(chrome_exe, url_bottom_right,
                                             x_right, y_bottom, w_right, h_bottom)

                    bar.after(0, _after_open)

                def _after_open():
                    hw = create_h_bar()
                    h_bar_win[0] = hw
                    h_bar_visible[0] = True
                    btn_h_toggle.config(state="normal",
                                        text="◻  Nascondi H-barra", bg="#1a4a6a")
                    btn_split.config(state="normal",
                                     text="⬛  Torna a ×2", bg="#6a3a00")

                threading.Thread(target=_open, daemon=True).start()

            else:
           
                split_active[0] = False

                close_chrome_windows([h for h in bottom_hwnds if h])
                for h in bottom_hwnds:
                    if h and h in all_hwnds:
                        all_hwnds.remove(h)
                bottom_hwnds[0] = None
                bottom_hwnds[1] = None

                if h_bar_win[0]:
                    try: h_bar_win[0].destroy()
                    except: pass
                    h_bar_win[0] = None
                    h_bar_visible[0] = False

                hwnd_l, hwnd_r = (all_hwnds + [None, None])[:2]
                if hwnd_l: position_window(hwnd_l, x_left,  0, w_left,  screen_h)
                if hwnd_r: position_window(hwnd_r, x_right, 0, w_right, screen_h)

                btn_h_toggle.config(state="disabled",
                                    text="◻  Nascondi H-barra", bg="#1a4a6a")
                btn_split.config(text="➕  Dividi ×4", bg="#1a4a6a")

 
        def exit_all(e=None):
            close_chrome_windows(all_hwnds)
            time.sleep(0.3)
            bar.destroy()
            os._exit(0)
 
        BTN_H = 38; GAP = 4
        W_TOGGLE = 160; W_SPLIT = 140; W_H_TOGGLE = 170; W_CLOSE = 38
        total_w = W_TOGGLE + GAP + W_SPLIT + GAP + W_H_TOGGLE + GAP + W_CLOSE
        panel_x = screen_w - total_w - 12
        panel_y = screen_h - BTN_H - 12

        panel = tk.Toplevel(bar)
        panel.overrideredirect(True)
        panel.attributes("-topmost", True)
        panel.geometry(f"{total_w}x{BTN_H}+{panel_x}+{panel_y}")
        panel.configure(bg="#1e1e1e")

        cur_x = 0
        btn_toggle = tk.Button(panel, text="◻  Nascondi barra",
            bg="#5a2727", fg="white", activebackground="#7a3737", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2",
            command=toggle_bar)
        btn_toggle.place(x=cur_x, y=0, width=W_TOGGLE, height=BTN_H); cur_x += W_TOGGLE

        tk.Frame(panel, bg="#444444", width=GAP, height=BTN_H).place(x=cur_x, y=0); cur_x += GAP

        btn_split = tk.Button(panel, text="➕  Dividi ×4",
            bg="#1a4a6a", fg="white", activebackground="#2a6a9a", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2",
            command=toggle_split)
        btn_split.place(x=cur_x, y=0, width=W_SPLIT, height=BTN_H); cur_x += W_SPLIT

        tk.Frame(panel, bg="#444444", width=GAP, height=BTN_H).place(x=cur_x, y=0); cur_x += GAP

        btn_h_toggle = tk.Button(panel, text="◻  Nascondi H-barra",
            bg="#1a4a6a", fg="white", activebackground="#2a6a9a", activeforeground="white",
            font=("Segoe UI", 9, "bold"), relief="flat", bd=0, cursor="hand2",
            state="disabled", command=toggle_h_bar)
        btn_h_toggle.place(x=cur_x, y=0, width=W_H_TOGGLE, height=BTN_H); cur_x += W_H_TOGGLE

        tk.Frame(panel, bg="#444444", width=GAP, height=BTN_H).place(x=cur_x, y=0); cur_x += GAP

        btn_close = tk.Button(panel, text="✕",
            bg="#8b0000", fg="white", activebackground="#cc0000", activeforeground="white",
            font=("Segoe UI", 12, "bold"), relief="flat", bd=0, cursor="hand2",
            command=exit_all)
        btn_close.place(x=cur_x, y=0, width=W_CLOSE, height=BTN_H)
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg="#cc0000"))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg="#8b0000"))

        bar.bind("<Escape>", exit_all)
        panel.bind("<Escape>", exit_all)
        bar.mainloop()

    except Exception as ex:
        print(f"Barra divisoria non disponibile: {ex}")


def main():
    url_left         = sys.argv[1] if len(sys.argv) > 1 else "chrome://newtab"
    url_right        = sys.argv[2] if len(sys.argv) > 2 else url_left
    url_bottom_left  = sys.argv[3] if len(sys.argv) > 3 else "chrome://newtab"
    url_bottom_right = sys.argv[4] if len(sys.argv) > 4 else "chrome://newtab"

    chrome = find_chrome()
    if not chrome:
        print("ERRORE: Google Chrome non trovato. Installalo e riprova.")
        sys.exit(1)

    screen_w, screen_h = get_screen_size()
    half_w = screen_w // 2

    divider_thickness = 30
    extra = 150

    half_left  = half_w - divider_thickness // 4 + extra
    x_right    = half_w + divider_thickness // 4 + extra
    half_right = screen_w - x_right

    print(f"""
╔══════════════════════════════════════════════════════╗
║        ⚡  {APP_NAME}  ⚡  Chrome Window Manager        ║
║              {APP_AUTHOR}              ║
╠══════════════════════════════════════════════════════╣
║  Schermo rilevato : {screen_w}x{screen_h}
║  Finestra sinistra: 0 -> {half_left}px
║  Finestra destra  : {x_right} -> {screen_w}px
║  Divisore centrale: {divider_thickness}px
║  URL basso-sx     : {url_bottom_left}
║  URL basso-dx     : {url_bottom_right}
╚══════════════════════════════════════════════════════╝
""")

    os_name = platform.system()
    hwnd_left = hwnd_right = None

    if os_name == "Windows":
        hwnds_before_left = get_all_chrome_hwnds()
        print(f"[SINISTRA] Avvio Chrome -> {url_left}")
        launch_chrome_window(chrome, url_left, 0, 0, half_left, screen_h)
        print("[SINISTRA] Attendo la nuova finestra...")
        hwnd_left = wait_for_new_chrome_window(hwnds_before_left)
        if hwnd_left:
            position_window(hwnd_left, 0, 0, half_left, screen_h)
            print("  Finestra SINISTRA posizionata correttamente.")
        else:
            print("  Impossibile trovare la finestra SINISTRA.")

        hwnds_before_right = get_all_chrome_hwnds()
        print(f"\n[DESTRA]   Avvio Chrome -> {url_right}")
        launch_chrome_window(chrome, url_right, x_right, 0, half_right, screen_h)
        print("[DESTRA]   Attendo la nuova finestra...")
        hwnd_right = wait_for_new_chrome_window(hwnds_before_right)
        if hwnd_right:
            position_window(hwnd_right, x_right, 0, half_right, screen_h)
            print("  Finestra DESTRA posizionata correttamente.")
        else:
            print("  Impossibile trovare la finestra DESTRA.")

    elif os_name == "Linux":
        print(f"[SINISTRA] Avvio Chrome -> {url_left}")
        proc_left = launch_chrome_window(chrome, url_left, 0, 0, half_left, screen_h)
        time.sleep(2.5)
        force_move_linux(proc_left.pid, 0, 0, half_left, screen_h)
        print(f"\n[DESTRA]   Avvio Chrome -> {url_right}")
        proc_right = launch_chrome_window(chrome, url_right, x_right, 0, half_right, screen_h)
        time.sleep(2.5)
        force_move_linux(proc_right.pid, x_right, 0, half_right, screen_h)
    else:
        print(f"[SINISTRA] Avvio Chrome -> {url_left}")
        launch_chrome_window(chrome, url_left, 0, 0, half_left, screen_h)
        time.sleep(2.5)
        print(f"[DESTRA]   Avvio Chrome -> {url_right}")
        launch_chrome_window(chrome, url_right, x_right, 0, half_right, screen_h)
        print("\nMac: posiziona manualmente le finestre se necessario.")

    print(f"\n⚡ {APP_NAME} v{APP_VERSION} — {APP_AUTHOR}")
    print("\nFatto! Usa i pulsanti in basso a destra:")
    print("  ◻ Nascondi barra   → mostra/nasconde la barra verticale")
    print("  ➕ Dividi ×4       → apre 2 finestre in basso e aggiunge barra H")
    print("  ◻ Nascondi H-barra → mostra/nasconde la barra orizzontale")
    print("  ✕                  → chiude tutto\n")

    show_divider_and_toggle(
        screen_w, screen_h,
        thickness=divider_thickness,
        offset=extra,
        chrome_hwnds=[hwnd_left, hwnd_right],
        chrome_exe=chrome,
        url_bottom_left=url_bottom_left,
        url_bottom_right=url_bottom_right,
        x_left=0,          w_left=half_left,
        x_right=x_right,   w_right=half_right,
        h_divider_v=divider_thickness,
    )


if __name__ == "__main__":
    main()