import tkinter as tk
from tkinter import ttk
import win32clipboard
import win32con
import pyautogui
import threading
import time
from collections import deque
from pynput import keyboard

class ClipboardHistoryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor del Historial del Portapapeles")
        self.clipboard_history = deque(maxlen=20)
        self.font_size = 10
        self.hover_item = None
        self.hover_time = 0
        self.last_copied_content = None
        self.clipboard_lock = threading.Lock()
        self.setup_ui()
        self.start_monitoring()
        self.start_keyboard_listener()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.frame, columns=("Indicador", "Contenido"), show="headings")
        self.tree.heading("Indicador", text="")
        self.tree.heading("Contenido", text="Contenido del Portapapeles")
        self.tree.column("Indicador", width=30, stretch=tk.NO)
        self.tree.column("Contenido", width=400, stretch=tk.YES)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind("<Motion>", self.on_mouse_over)
        self.tree.bind("<Leave>", self.on_mouse_leave)
        
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        font_button = ttk.Button(button_frame, text="Aumentar tamaño de fuente", command=self.increase_font_size)
        font_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Borrar historial", command=self.clear_history)
        clear_button.grid(row=0, column=1, padx=5)

        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, pady=5)

        self.update_font()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        style.map("Treeview", background=[('selected', '#a6a6a6')])

        self.tree.tag_configure('odd', background='#F0F0F0')
        self.tree.tag_configure('even', background='#FFFFFF')
        self.tree.tag_configure('gray_circle', foreground='gray')
        self.tree.tag_configure('green_circle', foreground='lime')

    def start_monitoring(self):
        self.monitoring_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitoring_thread.start()

    def monitor_clipboard(self):
        last_content = ""
        while True:
            try:
                with self.clipboard_lock:
                    content = self.get_clipboard_content()
                if content != last_content:
                    self.root.after(0, self.add_to_history, content)
                    last_content = content
            except Exception as e:
                print(f"Error al monitorear el portapapeles: {e}")
            time.sleep(0.5)

    def get_clipboard_content(self):
        formats = [
            (win32con.CF_UNICODETEXT, self.get_unicode_text),
            (win32con.CF_TEXT, self.get_text),
            (win32con.CF_BITMAP, self.get_image_text),
            (win32con.CF_HDROP, self.get_file_text)
        ]
        
        try:
            win32clipboard.OpenClipboard()
            for format, getter in formats:
                if win32clipboard.IsClipboardFormatAvailable(format):
                    content = getter()
                    if content:
                        return content
            return "Contenido no soportado"
        except Exception as e:
            print(f"Error al obtener contenido del portapapeles: {e}")
            return "Error al leer el portapapeles"
        finally:
            win32clipboard.CloseClipboard()

    def get_unicode_text(self):
        return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)

    def get_text(self):
        return win32clipboard.GetClipboardData(win32con.CF_TEXT).decode('utf-8')

    def get_image_text(self):
        return "[Imagen en el portapapeles]"

    def get_file_text(self):
        files = win32clipboard.GetClipboardData(win32con.CF_HDROP)
        return "[Archivos en el portapapeles]: " + ", ".join(files)

    def set_clipboard_content(self, content):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(content, win32con.CF_UNICODETEXT)
        except Exception as e:
            print(f"Error al establecer contenido en el portapapeles: {e}")
        finally:
            win32clipboard.CloseClipboard()

    def start_keyboard_listener(self):
        def on_press(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = True
            elif hasattr(key, 'char') and key.char == 'c' and self.ctrl_pressed:
                self.root.after(100, self.update_on_ctrl_c)

        def on_release(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.ctrl_pressed = False

        self.ctrl_pressed = False
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

    def update_on_ctrl_c(self):
        with self.clipboard_lock:
            content = self.get_clipboard_content()
            self.add_to_history(content)

    def add_to_history(self, content):
        if content and content not in self.clipboard_history:
            self.clipboard_history.appendleft(content)
            self.update_treeview()

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for i, content in enumerate(self.clipboard_history):
            item = self.tree.insert("", "end", values=("●", content[:50] + "..." if len(content) > 50 else content), 
                                    tags=('odd' if i % 2 else 'even', 'gray_circle'))

    def on_mouse_over(self, event):
        item = self.tree.identify_row(event.y)
        if item != self.hover_item:
            self.hover_item = item
            self.hover_time = time.time()
        elif item and time.time() - self.hover_time >= 1:
            content = self.tree.item(item, "values")[1]
            if content.endswith("..."):
                content = list(self.clipboard_history)[self.tree.index(item)]
            
            if content != self.last_copied_content:
                with self.clipboard_lock:
                    self.set_clipboard_content(content)
                self.root.update()
                pyautogui.hotkey('ctrl', 'v')
                self.last_copied_content = content
                self.status_var.set(f"Copiado: {content[:30]}...")
                self.tree.item(item, tags=self.tree.item(item, "tags")[:-1] + ('green_circle',))
                self.root.after(2000, lambda: self.reset_status_and_color(item))
            else:
                self.status_var.set("Contenido ya copiado.")
                self.tree.item(item, tags=self.tree.item(item, "tags")[:-1] + ('green_circle',))
                self.root.after(2000, lambda: self.reset_status_and_color(item))

    def on_mouse_leave(self, event):
        self.hover_item = None
        self.hover_time = 0
        self.status_var.set("")

    def reset_status_and_color(self, item):
        self.status_var.set("")
        self.tree.item(item, tags=self.tree.item(item, "tags")[:-1] + ('gray_circle',))

    def increase_font_size(self):
        self.font_size += 2
        self.update_font()

    def update_font(self):
        style = ttk.Style()
        style.configure("Treeview", font=("TkDefaultFont", self.font_size))
        style.configure("Treeview.Heading", font=("TkDefaultFont", self.font_size, "bold"))

    def clear_history(self):
        self.clipboard_history.clear()
        self.update_treeview()
        self.status_var.set("Historial borrado")
        self.root.after(100, self.clear_clipboard)

    def clear_clipboard(self):
        with self.clipboard_lock:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
            except Exception as e:
                print(f"Error al limpiar el portapapeles: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardHistoryViewer(root)
    root.mainloop()
