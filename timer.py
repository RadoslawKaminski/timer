import tkinter as tk
import time
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import threading
import winsound
import pygame

# Initialize pygame mixer
pygame.mixer.init()


def play_loud_sound():
    pygame.mixer.music.load("alarm.wav")  # Replace with the path to your sound file
    pygame.mixer.music.set_volume(1.0)  # Volume ranges from 0.0 to 1.0 (1.0 is max volume)
    pygame.mixer.music.play()


def create_tray_icon(root, osd_window, toggle_osd):
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill='white')

    def show_window(item):
        print("Otwieram okno...")
        root.deiconify()

    def quit_app(item):
        print("Zamykam aplikację...")
        item.stop()
        root.quit()
        quit()

    menu = Menu(MenuItem('Pokaż', show_window), MenuItem('Zamknij', quit_app), MenuItem('Włącz/Odłącz OSD', toggle_osd))
    icon = Icon("Minutnik", image, menu=menu)

    threading.Thread(target=icon.run, daemon=True).start()


def create_floating_clock(toggle_osd_state):
    osd_window = tk.Toplevel()
    osd_window.overrideredirect(True)  # Usuwamy górny pasek
    osd_window.wm_attributes("-topmost", True)  # Zawsze na wierzchu
    osd_window.wm_attributes("-transparentcolor", "black")  # Ustawiamy czarne tło jako przezroczyste
    osd_window.geometry("300x200")  # Ustawiamy rozmiar i pozycję okna
    osd_window.minsize(50, 50)
    osd_window.withdraw()  # OSD jest domyślnie ukryte

    osd_time_label = tk.Label(osd_window, font=("Arial", 100), bg="black", fg="white", text="00:00")
    osd_time_label.pack(fill=tk.BOTH, expand=True)

    def update_font_size_osd(event):
        new_font_size = min(event.width // 4, int(event.height // (5 / 3)))
        osd_time_label.config(font=("Arial", new_font_size))

    osd_window.bind("<Configure>", update_font_size_osd)

    # Zmienne do przechowywania pozycji
    offset_x = 0
    offset_y = 0

    def drag_window(event):
        new_x = event.x_root - offset_x
        new_y = event.y_root - offset_y
        osd_window.geometry(f'+{new_x}+{new_y}')

    def on_button_press(event):
        nonlocal offset_x, offset_y
        offset_x = event.x_root - osd_window.winfo_x()
        offset_y = event.y_root - osd_window.winfo_y()

    def resize_window(event):
        new_width = event.x + 10
        new_height = event.y + 10
        if new_width > 0 and new_height > 0:
            osd_window.geometry(f"{new_width}x{new_height}")

    osd_window.bind("<Button-1>", on_button_press)
    osd_time_label.bind("<B1-Motion>", drag_window)
    osd_time_label.bind("<B3-Motion>", resize_window)
    osd_window.bind("<Double-Button-1>", lambda e: toggle_osd_state())

    return osd_window, osd_time_label


def start_timer():
    root = tk.Tk()
    root.title("Minutnik")
    root.geometry("300x300")
    root.minsize(300, 300)
    root.configure(bg="black")
    root.attributes('-topmost', True)

    osd_enabled = False

    time_label = tk.Label(root, font=("Arial", 48), bg="black", fg="white", text="00:00")
    time_label.pack(pady=10, fill=tk.BOTH, expand=True)

    input_frame = tk.Frame(root, bg="black")
    input_frame.pack(pady=5)

    minute_label = tk.Label(input_frame, text="Min:", bg="black", fg="white", font=("Arial", 20))
    minute_label.grid(row=0, column=0, padx=(5, 5))

    minute_entry = tk.Entry(input_frame, width=2, bg="black", fg="white", borderwidth=2, relief="flat", font=("Arial", 20),
                            highlightbackground="white", highlightcolor="white", highlightthickness=1)
    minute_entry.grid(row=0, column=1, padx=(0, 5))

    second_label = tk.Label(input_frame, text="Sec:", bg="black", fg="white", font=("Arial", 20))
    second_label.grid(row=0, column=2, padx=(5, 5))

    second_entry = tk.Entry(input_frame, width=2, bg="black", fg="white", borderwidth=2, relief="flat", font=("Arial", 20),
                            highlightbackground="white", highlightcolor="white", highlightthickness=1)
    second_entry.grid(row=0, column=3, padx=(0, 5))

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack(pady=5)

    start_button = tk.Button(button_frame, text="▶", command=lambda: toggle_timer(), bg="black", fg="white",
                             relief="flat", highlightbackground="white", borderwidth=1, font=("Arial", 20))
    start_button.grid(row=0, column=1, padx=5)

    reset_button = tk.Button(button_frame, text="🔄", command=lambda: reset_timer(), bg="black", fg="white",
                             relief="flat", highlightbackground="white", borderwidth=1, font=("Arial", 20))
    reset_button.grid(row=0, column=2, padx=5)

    original_minutes = 0
    original_seconds = 0
    total_seconds = 0
    elapsed_time = 0
    is_finished = False
    is_running = False
    clean = True
    last_time_called = 0

    def toggle_osd_state():
        nonlocal osd_enabled
        if osd_enabled:
            osd_window.withdraw()
            root.geometry(f"{osd_window.winfo_width()}x{osd_window.winfo_height()}+{osd_window.winfo_x()}+{osd_window.winfo_y()}")
            root.deiconify()
        else:
            root.withdraw()
            osd_window.geometry(f"{root.winfo_width()}x{root.winfo_height()}+{root.winfo_x()}+{root.winfo_y()}")
            osd_window.deiconify()
        osd_enabled = not osd_enabled

    time_label.bind("<Double-Button-1>", lambda e: toggle_osd_state())
    osd_window, osd_time_label = create_floating_clock(toggle_osd_state)

    def update_font_size_root(event):
        if event.widget == root:
            new_font_size = min(event.width // 4, int((event.height - 100) // (5 / 3)))
            time_label.config(font=("Arial", new_font_size))

    root.bind("<Configure>", update_font_size_root)

    create_tray_icon(root, osd_window, toggle_osd_state)

    def minimize_to_tray():
        print("Minimalizuję do zasobnika...")
        root.withdraw()

    root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

    def update_timer():
        nonlocal total_seconds, elapsed_time, is_finished, is_running, last_time_called, osd_enabled
        delta = time.time() - last_time_called
        if delta < 0.9:
            return
        last_time_called = time.time()
        if total_seconds > 1 and is_running:
            total_seconds -= 1
            mins, secs = divmod(total_seconds, 60)
            time_label.config(text=f"{mins:02}:{secs:02}")
            osd_time_label.config(text=f"{mins:02}:{secs:02}")
            if total_seconds <= 25:
                time_label.config(fg="red")
                osd_time_label.config(fg="red")
            root.after(1000, update_timer)
        elif is_running:
            if not is_finished and (original_minutes != 0 or original_seconds != 0):
                total_seconds -= 1
                if osd_enabled:
                    toggle_osd_state()
                elif not root.winfo_viewable():
                    root.geometry("400x200")
                    root.deiconify()
                root.attributes("-topmost", True)
                time_label.config(text="END")
                osd_time_label.config(text="END")
                is_finished = True
                hide_inputs()
                play_loud_sound()
                root.after(1000, update_timer)
            else:
                elapsed_time += 1
                mins, secs = divmod(elapsed_time, 60)
                time_label.config(text=f"+{mins:02}:{secs:02}")
                osd_time_label.config(text=f"+{mins:02}:{secs:02}")
                root.after(1000, update_timer)

    def toggle_timer():
        nonlocal original_minutes, original_seconds, total_seconds, elapsed_time, is_finished, is_running, clean

        if is_running:
            is_running = False
            start_button.config(text="▶")
        else:
            try:
                if clean:
                    minutes_input = minute_entry.get().strip()
                    seconds_input = second_entry.get().strip()

                    original_minutes = int(minutes_input) if minutes_input else 0
                    original_seconds = int(seconds_input) if seconds_input else 0

                    total_seconds = original_minutes * 60 + original_seconds
                    mins, secs = divmod(total_seconds, 60)
                    time_label.config(text=f"{mins:02}:{secs:02}")
                    osd_time_label.config(text=f"{mins:02}:{secs:02}")
                    elapsed_time = 0
                    clean = False
                    is_finished = False
                is_running = True
                root.after(1000, update_timer)
                start_button.config(text="⏸")
                hide_inputs()
            except ValueError:
                time_label.config(text="Wprowadź poprawne liczby!")

    def hide_inputs():
        minute_label.grid_forget()
        minute_entry.grid_forget()
        second_label.grid_forget()
        second_entry.grid_forget()

    def show_inputs():
        minute_label.grid(row=0, column=0, padx=(5, 5))
        minute_entry.grid(row=0, column=1, padx=(0, 5))
        second_label.grid(row=0, column=2, padx=(5, 5))
        second_entry.grid(row=0, column=3, padx=(0, 5))

    def reset_timer():
        nonlocal is_finished, is_running, clean
        is_finished = False
        is_running = False
        clean = True
        time_label.config(text="00:00", fg="white")
        osd_time_label.config(text="00:00", fg="white")
        start_button.config(text="▶")
        show_inputs()
        pygame.mixer.music.stop()

    root.mainloop()


start_timer()