import os
import sys
import shutil
import threading
import subprocess
from tkinter import filedialog
from PIL import Image
import customtkinter as ctk

# Redirigir errores de forma segura a un archivo de log local para diagnóstico
log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "installer_debug.log")
try:
    sys.stdout = open(log_path, "w", encoding="utf-8")
    sys.stderr = sys.stdout
    print("--- INICIANDO DEPURACIÓN DEL INSTALADOR ---")
except Exception:
    pass

# Importación segura de win32com para crear accesos directos
try:
    import win32com.client
    SHORTCUTS_AVAILABLE = True
except ImportError:
    SHORTCUTS_AVAILABLE = False

# Configuración básica de CustomTkinter
ctk.deactivate_automatic_dpi_awareness()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """Obtiene la ruta absoluta a los recursos, compatible con PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class WoWInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de Ventana (Utiliza el borde del sistema operativo)
        self.title("Instalador Oficial - Séquito del Terror WoW")
        self.geometry("750x450")
        self.resizable(False, False)

        # Tipografía
        self.title_font = ctk.CTkFont(family="Cinzel", size=20, weight="bold")
        self.desc_font = ctk.CTkFont(family="Inter", size=13, weight="normal")
        self.btn_font = ctk.CTkFont(family="Inter", size=13, weight="bold")

        # Cargar recursos
        self.load_assets()

        # Interfaz de usuario
        self.create_widgets()

    def load_assets(self):
        bg_path = resource_path("assets/bg.png")
        if os.path.exists(bg_path):
            self.bg_image = ctk.CTkImage(Image.open(bg_path), size=(750, 450))
        else:
            self.bg_image = None

        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(100, 100))
        else:
            self.logo_image = None

    def create_widgets(self):
        # 1. Fondo de pantalla principal
        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.bg_label = ctk.CTkLabel(self, fg_color="#101010", text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 2. Panel de Contenido Glassmorphic Central
        self.main_card = ctk.CTkFrame(self, width=690, height=380, fg_color="#0F0F0F", corner_radius=15,
                                      border_color="#A83232", border_width=1)
        self.main_card.place(x=30, y=35)
        self.main_card.lift()

        # Logotipo gótico
        if self.logo_image:
            self.logo_lbl = ctk.CTkLabel(self.main_card, image=self.logo_image, text="")
            self.logo_lbl.place(x=30, y=30)
        else:
            self.logo_lbl = ctk.CTkLabel(self.main_card, text="[SÉQUITO]", font=self.title_font, text_color="#A83232")
            self.logo_lbl.place(x=30, y=30)

        # Titulo y descripción de instalación
        self.welcome_lbl = ctk.CTkLabel(self.main_card, text="INSTALACIÓN DEL LAUNCHER OFICIAL", 
                                        font=self.title_font, text_color="#A83232", anchor="w")
        self.welcome_lbl.place(x=150, y=35)

        self.welcome_desc = ctk.CTkLabel(self.main_card, text="Este asistente desplegará el launcher portátil y configurará los accesos\ndirectos del clan con el emblema gótico para jugar en Capycraft.io.", 
                                         font=self.desc_font, text_color="#D4AF37", justify="left")
        self.welcome_desc.place(x=150, y=70)

        # Pantalla de Paso 1: Selección de Carpeta
        self.render_step_select_path()

    def render_step_select_path(self):
        # Etiqueta
        self.path_lbl = ctk.CTkLabel(self.main_card, text="Selecciona la carpeta donde deseas instalar (o tu carpeta de WoW existente):", 
                                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
                                     text_color="#FFFFFF")
        self.path_lbl.place(x=30, y=175)

        # Campo de entrada para la ruta
        self.path_var = ctk.StringVar(value="C:\\Games\\WoW Capycraft Sequito")
        self.path_entry = ctk.CTkEntry(self.main_card, textvariable=self.path_var, width=470, height=35,
                                       font=ctk.CTkFont(family="Inter", size=12), border_color="#A83232", fg_color="#1A1A1A")
        self.path_entry.place(x=30, y=210)

        # Botón Examinar
        self.browse_btn = ctk.CTkButton(self.main_card, text="EXAMINAR...", font=self.btn_font,
                                        fg_color="#1E1E1E", hover_color="#2D2D2D", border_color="#D4AF37", border_width=1,
                                        width=140, height=35, text_color="#E0E0E0", corner_radius=6,
                                        command=self.browse_folder)
        self.browse_btn.place(x=515, y=210)

        # Botón Instalar
        self.install_btn = ctk.CTkButton(self.main_card, text="INSTALAR CLIENTE SÉQUITO", font=self.btn_font,
                                         fg_color="#A83232", hover_color="#801D1D", text_color="#FFFFFF",
                                         width=625, height=45, corner_radius=8, border_color="#D4AF37", border_width=1,
                                         command=self.start_installation_thread)
        self.install_btn.place(x=30, y=300)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir="C:\\Games", title="Selecciona la Carpeta de Destino")
        if selected:
            # Normalizar barra inclinada en Windows
            self.path_var.set(os.path.normpath(selected))

    def start_installation_thread(self):
        # 1. Obtener la ruta antes de destruir cualquier widget para evitar fallos de StringVar en Tkinter
        target_dir = self.path_var.get()

        # Deshabilitar botones
        self.install_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.path_entry.configure(state="disabled")
        
        # Eliminar controles y cambiar a vista de progreso
        self.path_lbl.destroy()
        self.path_entry.destroy()
        self.browse_btn.destroy()
        
        # Crear barra de progreso e indicador de estado
        self.status_lbl = ctk.CTkLabel(self.main_card, text="Iniciando instalación...", 
                                       font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
                                       text_color="#E0E0E0", anchor="w", width=625)
        self.status_lbl.place(x=30, y=190)

        self.progress_bar = ctk.CTkProgressBar(self.main_card, width=625, height=10, progress_color="#A83232", fg_color="#222222")
        self.progress_bar.place(x=30, y=225)
        self.progress_bar.set(0)

        # Lanzar hilo de instalación pasando la ruta de forma segura
        threading.Thread(target=self.run_installation, args=(target_dir,), daemon=True).start()

    def run_installation(self, target_dir):
        try:
            # 1. Crear directorios
            self.update_status("Creando estructura de directorios...", 0.15)
            os.makedirs(target_dir, exist_ok=True)
            os.makedirs(os.path.join(target_dir, "assets"), exist_ok=True)
            
            # 2. Desplegar realmlist preconfigurado
            self.update_status("Escribiendo realmlist.wtf oficial de Capycraft...", 0.35)
            realmlist_content = 'SET realmList "apac.capycraft.io"\nSET patchList "apac.capycraft.io"\n'
            with open(os.path.join(target_dir, "realmlist.wtf"), "w", encoding="utf-8") as f:
                f.write(realmlist_content)

            # 3. Copiar recursos embebidos a destino
            self.update_status("Copiando recursos visuales góticos del clan...", 0.60)
            assets_to_copy = ["bg.png", "logo.png", "logo.ico"]
            for asset in assets_to_copy:
                src_asset = resource_path(f"assets/{asset}")
                if os.path.exists(src_asset):
                    shutil.copy2(src_asset, os.path.join(target_dir, "assets", asset))

            # 4. Copiar configuración local
            self.update_status("Copiando archivo de configuración config.json...", 0.75)
            src_config = resource_path("config.json")
            if os.path.exists(src_config):
                shutil.copy2(src_config, os.path.join(target_dir, "config.json"))

            # 5. Copiar el ejecutable del launcher portátil (ASCII Seguro)
            self.update_status("Copiando SequitoLauncher.exe...", 0.85)
            src_launcher = resource_path("SequitoLauncher.exe")
            if not os.path.exists(src_launcher):
                src_launcher = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "SequitoLauncher.exe")

            if os.path.exists(src_launcher):
                shutil.copy2(src_launcher, os.path.join(target_dir, "SequitoLauncher.exe"))
            else:
                raise FileNotFoundError("No se encontró el ejecutable SequitoLauncher.exe para copiar.")

            # 6. Crear accesos directos
            self.update_status("Creando acceso directo oficial en tu Escritorio...", 0.95)
            self.create_windows_shortcuts(target_dir)

            self.progress_bar.set(1.0)
            # Detección inteligente para guiar al usuario
            if os.path.exists(os.path.join(target_dir, "WoW.exe")):
                self.update_status("✓ ¡Instalación Completada con Éxito! Tu cliente de juego ya está listo.", 1.0)
            else:
                self.update_status("✓ ¡Instalado! Abre el Launcher para descargar el juego completo en 1-Clic.", 1.0)
            
            # Cambiar botón Instalar por Finalizar de forma segura
            self.after(0, lambda: self.install_btn.configure(text="FINALIZAR Y ABRIR LAUNCHER", state="normal", command=lambda: self.finalize_installation(target_dir)))

        except Exception as e:
            self.update_status(f"Error durante la instalación: {e}", 0.0)
            self.after(0, lambda: self.install_btn.configure(text="REINTENTAR", state="normal", command=self.destroy))

    def update_status(self, text, progress):
        self.after(0, lambda: self.status_lbl.configure(text=text))
        self.after(0, lambda: self.progress_bar.set(progress))

    def create_windows_shortcuts(self, install_dir):
        if not SHORTCUTS_AVAILABLE:
            return
        
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # 1. Escritorio
            desktop_path = shell.SpecialFolders("Desktop")
            shortcut_desktop = shell.CreateShortCut(os.path.join(desktop_path, "Séquito del Terror WoW.lnk"))
            shortcut_desktop.TargetPath = os.path.join(install_dir, "SequitoLauncher.exe")
            shortcut_desktop.WorkingDirectory = install_dir
            shortcut_desktop.IconLocation = os.path.join(install_dir, "assets", "logo.ico")
            shortcut_desktop.Description = "Launcher Oficial del Clan Séquito del Terror para Capycraft.io"
            shortcut_desktop.Save()

            # 2. Menú Inicio
            programs_path = shell.SpecialFolders("Programs")
            shortcut_menu = shell.CreateShortCut(os.path.join(programs_path, "Séquito del Terror WoW.lnk"))
            shortcut_menu.TargetPath = os.path.join(install_dir, "SequitoLauncher.exe")
            shortcut_menu.WorkingDirectory = install_dir
            shortcut_menu.IconLocation = os.path.join(install_dir, "assets", "logo.ico")
            shortcut_menu.Description = "Launcher Oficial del Clan Séquito del Terror para Capycraft.io"
            shortcut_menu.Save()
        except Exception as e:
            print(f"Error creando accesos directos: {e}")

    def finalize_installation(self, install_dir):
        # Lanzar el launcher recién instalado
        launcher_path = os.path.join(install_dir, "SequitoLauncher.exe")
        if os.path.exists(launcher_path):
            try:
                subprocess.Popen([launcher_path], cwd=install_dir, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    app = WoWInstaller()
    app.mainloop()
