import customtkinter as ctk
import subprocess
import os
import threading
from tkinter import Toplevel, Label, messagebox, filedialog
from PIL import Image
import json

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SteamCMDPathWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Укажите путь к SteamCMD")
        self.geometry("400x200")
        self.steamcmd_path = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self.main_frame, text="SteamCMD не найден. Пожалуйста, укажите путь:", wraplength=350)
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.path_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Путь к SteamCMD")
        self.path_entry.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.main_frame, text="Обзор", command=self.browse_path, width=70)
        self.browse_button.grid(row=1, column=1, padx=(5, 10), pady=10)

        self.confirm_button = ctk.CTkButton(self.main_frame, text="Подтвердить", command=self.confirm_path)
        self.confirm_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def browse_path(self):
        path = filedialog.askopenfilename(filetypes=[("SteamCMD", "steamcmd.exe")])
        if path:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, path)

    def confirm_path(self):
        self.steamcmd_path = self.path_entry.get()
        self.destroy()

class LogWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Журнал SteamCMD")
        self.geometry("600x400")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(self, height=350, width=550, state="disabled")
        self.log_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def update_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(ctk.END, message + "\n")
        self.log_text.see(ctk.END)
        self.log_text.configure(state="disabled")

class ListManagerWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Управление списками")
        self.geometry("400x300")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.list_name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Имя списка")
        self.list_name_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.id_entry = ctk.CTkTextbox(self.main_frame, height=100)
        self.id_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.id_entry.insert("1.0", "Введите ID в формате 'App ID:Workshop ID', по одному на строку")

        self.save_list_button = ctk.CTkButton(self.main_frame, text="Сохранить список", command=self.save_list)
        self.save_list_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.load_list_button = ctk.CTkButton(self.main_frame, text="Загрузить список", command=self.load_list)
        self.load_list_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def save_list(self):
        list_name = self.list_name_entry.get()
        id_text = self.id_entry.get("1.0", ctk.END).strip()
        if list_name and id_text:
            ids = [line.strip() for line in id_text.split('\n') if line.strip()]
            with open(f"{list_name}.json", 'w') as f:
                json.dump(ids, f)
            messagebox.showinfo("Успех", f"Список {list_name} сохранен")
        else:
            messagebox.showerror("Ошибка", "Введите имя списка и хотя бы один ID")

    def load_list(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                ids = json.load(f)
            self.id_entry.delete("1.0", ctk.END)
            self.id_entry.insert("1.0", '\n'.join(ids))
            self.list_name_entry.delete(0, ctk.END)
            self.list_name_entry.insert(0, os.path.splitext(os.path.basename(file_path))[0])

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip, text=self.text, background="#2b2b2b", relief="solid", borderwidth=0)
        label.pack()

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class InstallFromListWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Установка из списка")
        self.geometry("400x450")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Выбор списка
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        list_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(list_frame, text="Список:").grid(row=0, column=0, padx=(10, 5), pady=5)
        self.list_combobox = ctk.CTkComboBox(list_frame, values=self.get_list_files(), width=200)
        self.list_combobox.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Выбор пути сохранения
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(path_frame, text="Путь:").grid(row=0, column=0, padx=(10, 5), pady=5)
        self.path_entry = ctk.CTkEntry(path_frame)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(path_frame, text="...", command=self.browse_path, width=30).grid(row=0, column=2, padx=(5, 10), pady=5)

        # Кнопка установки
        self.install_button = ctk.CTkButton(main_frame, text="Установить", command=self.start_installation)
        self.install_button.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        # Информация об установке
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(info_frame, text="Информация об установке:").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.info_text = ctk.CTkTextbox(info_frame, height=200, wrap="word")
        self.info_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def get_list_files(self):
        return [f for f in os.listdir() if f.endswith('.json')]

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, path)

    def start_installation(self):
        selected_list = self.list_combobox.get()
        install_path = self.path_entry.get()

        if not selected_list or not install_path:
            messagebox.showerror("Ошибка", "Выберите список и укажите путь для установки")
            return

        with open(selected_list, 'r') as f:
            id_list = json.load(f)

        self.info_text.delete("1.0", ctk.END)
        self.info_text.insert(ctk.END, f"Начало установки из списка {selected_list}\n")
        
        threading.Thread(target=self.install_from_list, args=(id_list, install_path), daemon=True).start()

    def install_from_list(self, id_list, install_path):
        total_items = len(id_list)
        for index, id_pair in enumerate(id_list, 1):
            if ':' in id_pair:
                app_id, workshop_id = id_pair.split(':')
                self.update_info(f"Установка {index}/{total_items}: App ID {app_id}, Workshop ID {workshop_id}")
                self.master.download_workshop_item(app_id, workshop_id, install_path)
        self.update_info("Установка из списка завершена")

    def update_info(self, message):
        self.info_text.insert(ctk.END, message + "\n")
        self.info_text.see(ctk.END)

class SteamWorkshopDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Steam Workshop Downloader")
        self.geometry("460x330")  # Увеличили высоту для новой кнопки

        # Загрузка логотипа приложения
        logo_path = os.path.join(os.path.dirname(__file__), "gfx", "logo.ico")
        if os.path.exists(logo_path):
            self.iconbitmap(logo_path)

        self.steamcmd_path = self.find_steamcmd()
        if not self.steamcmd_path:
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.main_frame, text="Steam Workshop Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))

        self.app_id_entry = ctk.CTkEntry(self.main_frame, placeholder_text="App ID")
        self.app_id_entry.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        self.workshop_id_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Workshop ID")
        self.workshop_id_entry.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        self.path_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Путь для сохранения", width=350)
        self.path_entry.grid(row=3, column=0, columnspan=2, padx=(20, 5), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.main_frame, text="Обзор", command=self.browse_path, width=150)
        self.browse_button.grid(row=3, column=2, padx=(5, 20), pady=10)

        self.download_button = ctk.CTkButton(self.main_frame, text="Загрузить", command=self.start_download)
        self.download_button.grid(row=4, column=0, columnspan=2, padx=(20, 5), pady=10, sticky="ew")

        # Загрузка иконки Журнала
        log_path = os.path.join(os.path.dirname(__file__), "gfx", "log.png")
        if os.path.exists(log_path):
            log_icon = ctk.CTkImage(Image.open(log_path), size=(20, 20))
        else:
            log_icon = None

        # Кнопка Журнала  
        self.show_log_button = ctk.CTkButton(self.main_frame, text="", image=log_icon, width=30, height=30, command=self.show_log, fg_color="transparent")
        self.show_log_button.grid(row=4, column=2, padx=(5, 40), pady=10, sticky="e")
        ToolTip(self.show_log_button, "Показать журнал")

        # Загрузка иконки Редактора Списков
        list_icon_path = os.path.join(os.path.dirname(__file__), "gfx", "list.png")
        if os.path.exists(list_icon_path):
            list_icon = ctk.CTkImage(Image.open(list_icon_path), size=(20, 20))
        else:
            list_icon = None
        
        # Кнопка Редактора Списков
        self.manage_lists_button = ctk.CTkButton(self.main_frame, text="", image=list_icon, width=30, height=30, command=self.open_list_manager, fg_color="transparent")
        self.manage_lists_button.grid(row=4, column=2, padx=(0, 80), pady=10, sticky="e")
        ToolTip(self.manage_lists_button, "Управление списками")

        # Кнопка "Управление списками"
        # self.manage_lists_button = ctk.CTkButton(self.main_frame, text="Управление списками", command=self.open_list_manager, width=200)
        # self.manage_lists_button.grid(row=5, column=0, padx=(20, 5), pady=10, sticky="e")
        
        # Загрузка иконки установки из списка
        install_list_icon_path = os.path.join(os.path.dirname(__file__), "gfx", "list_download.png")
        if os.path.exists(install_list_icon_path):
            install_list_icon = ctk.CTkImage(Image.open(install_list_icon_path), size=(20, 20))
        else:
            install_list_icon = None

        self.install_from_list_button = ctk.CTkButton(self.main_frame, text="", image=install_list_icon, width=30, height=30, command=self.install_from_list, fg_color="transparent")
        self.install_from_list_button.grid(row=4, column=2, padx=(0, 120), pady=10, sticky="e")
        ToolTip(self.install_from_list_button, "Установить из списка")

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="w")

        self.log_window = None

    def find_steamcmd(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        steamcmd_name = "steamcmd.exe" if os.name == 'nt' else "steamcmd.sh"
        steamcmd_path = os.path.join(script_dir, steamcmd_name)
        
        if os.path.exists(steamcmd_path):
            return steamcmd_path
        else:
            steamcmd_window = SteamCMDPathWindow(self)
            self.wait_window(steamcmd_window)
            if steamcmd_window.steamcmd_path:
                return steamcmd_window.steamcmd_path
            else:
                messagebox.showerror("Ошибка", "Путь к SteamCMD не указан. Приложение будет закрыто.")
                self.quit()
                return None

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, path)

    def update_status(self, message):
        self.status_label.configure(text=message)

    def update_log(self, message):
        if self.log_window and not self.log_window.winfo_exists():
            self.log_window = None
        if self.log_window:
            self.log_window.update_log(message)

    def open_list_manager(self):
        ListManagerWindow(self)

    def install_from_list(self):
        InstallFromListWindow(self)

    def start_download(self):
        if not self.steamcmd_path:
            self.update_status("Ошибка: SteamCMD не найден")
            return
        
        app_id = self.app_id_entry.get()
        workshop_id = self.workshop_id_entry.get()
        install_path = self.path_entry.get()

        if not install_path:
            self.update_status("Ошибка: Укажите путь для сохранения")
            return

        if app_id and workshop_id:
            threading.Thread(target=self.download_workshop_item, args=(app_id, workshop_id, install_path), daemon=True).start()
        else:
            self.update_status("Ошибка: Введите App ID и Workshop ID")

    def download_multiple_items(self, id_list, install_path):
        total_items = len(id_list)
        for index, id_pair in enumerate(id_list, 1):
            if ':' in id_pair:
                app_id, workshop_id = id_pair.split(':')
                self.update_status(f"Загрузка {index}/{total_items}: App ID {app_id}, Workshop ID {workshop_id}")
                self.download_workshop_item(app_id, workshop_id, install_path)
        self.update_status("Все файлы из списка загружены")

    def download_workshop_item(self, app_id, workshop_id, install_path):
        try:
            command = [
                self.steamcmd_path,
                "+login tiralasg",
                f"+force_install_dir {install_path}",
                f"+workshop_download_item {app_id} {workshop_id}",
                "+quit"
            ]
    
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                   self.update_log(output.strip())

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise Exception(f"SteamCMD вернул код ошибки {process.returncode}\n{stderr}")

            self.update_status(f"Файл успешно загружен: App ID {app_id}, Workshop ID {workshop_id}")
        except Exception as e:
            self.update_status(f"Ошибка при загрузке {app_id}:{workshop_id}: {str(e)}")

    def show_log(self):
        if not self.log_window or not self.log_window.winfo_exists():
            self.log_window = LogWindow(self)
        else:
            self.log_window.focus()


if __name__ == "__main__":
    app = SteamWorkshopDownloader()
    if app.steamcmd_path:
        app.mainloop()