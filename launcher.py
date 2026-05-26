import os
import sys
import json
import time
import socket
import zipfile
import subprocess
import threading
import webbrowser
import shutil
import requests
from PIL import Image
import customtkinter as ctk

# Importación segura de pypresence
try:
    from pypresence import Presence
    PRESENCE_AVAILABLE = True
except ImportError:
    PRESENCE_AVAILABLE = False

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

class WoWLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cargar configuración
        self.load_config()

        # Configuración de Ventana Principal
        self.title("Séquito del Terror Launcher")
        self.geometry("920x570")
        self.resizable(False, False)
        
        # Tipografía y Estilos Premium
        self.title_font = ctk.CTkFont(family="Cinzel", size=24, weight="bold")
        self.tab_font = ctk.CTkFont(family="Inter", size=13, weight="bold")
        self.btn_font = ctk.CTkFont(family="Inter", size=13, weight="bold")
        self.play_font = ctk.CTkFont(family="Cinzel", size=24, weight="bold")

        # Hilo de Discord y estado
        self.discord_client = None
        self.game_running = False

        # Cargar recursos visuales
        self.load_assets()

        # Crear Interfaz de Usuario
        self.create_widgets()
        
        # Iniciar Tareas en Segundo Plano (Ping y Discord)
        self.start_background_services()

    def load_config(self):
        config_path = resource_path("config.json")
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "config.json")

        self.config = {
            "realmlist": "apac.capycraft.io",
            "patchlist": "apac.capycraft.io",
            "clan_url": "https://sequitodelterror.netlify.app/",
            "game_url": "https://capycraft.io/",
            "game_exe": "WoW.exe",
            "cache_dir": "WDB",
            "downloads": [],
            "addons": []
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except Exception as e:
                print(f"Error cargando config: {e}")

    def load_assets(self):
        # Imagen de fondo principal
        bg_path = resource_path("assets/bg.png")
        if os.path.exists(bg_path):
            self.bg_image = ctk.CTkImage(Image.open(bg_path), size=(920, 570))
        else:
            self.bg_image = None

        # Logotipo del Clan
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(85, 85))
        else:
            self.logo_image = None

    def start_background_services(self):
        # Autocorrección del realmlist
        self.auto_verify_realmlist()
        
        # Hilo continuo para medir el Ping al servidor
        threading.Thread(target=self.live_ping_worker, daemon=True).start()
        
        # Hilo de Discord Rich Presence
        if PRESENCE_AVAILABLE:
            threading.Thread(target=self.discord_presence_worker, daemon=True).start()

    def create_widgets(self):
        # 1. Capa de Fondo
        if self.bg_image:
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.bg_label = ctk.CTkLabel(self, fg_color="#101010", text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 3. Panel de Navegación por Pestañas (Centro Superior)
        self.nav_frame = ctk.CTkFrame(self, width=880, height=50, fg_color="#0F0F0F", corner_radius=10, 
                                      border_color="#A83232", border_width=1)
        self.nav_frame.place(x=20, y=20)
        self.nav_frame.lift()

        self.tab_noticias_btn = ctk.CTkButton(self.nav_frame, text="📰 NOTICIAS Y ESTADO", font=self.tab_font,
                                              fg_color="#A83232", hover_color="#801D1D", text_color="#FFFFFF",
                                              width=220, height=36, corner_radius=6, command=lambda: self.switch_tab("noticias"))
        self.tab_noticias_btn.pack(side="left", padx=10, pady=7)

        self.tab_addons_btn = ctk.CTkButton(self.nav_frame, text="🔌 GESTOR DE ADDONS", font=self.tab_font,
                                            fg_color="#1E1E1E", hover_color="#2D2D2D", text_color="#E0E0E0",
                                            width=220, height=36, corner_radius=6, command=lambda: self.switch_tab("addons"))
        self.tab_addons_btn.pack(side="left", padx=10, pady=7)

        self.tab_ajustes_btn = ctk.CTkButton(self.nav_frame, text="⚙️ AJUSTES DEL JUEGO", font=self.tab_font,
                                             fg_color="#1E1E1E", hover_color="#2D2D2D", text_color="#E0E0E0",
                                             width=220, height=36, corner_radius=6, command=lambda: self.switch_tab("ajustes"))
        self.tab_ajustes_btn.pack(side="left", padx=10, pady=7)

        # Widget de Latencia y Status en la barra de navegación
        self.ping_indicator = ctk.CTkLabel(self.nav_frame, text="● PINGING...", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
                                           text_color="#E0E0E0")
        self.ping_indicator.pack(side="right", padx=20)

        # 4. Contenedor de Contenido Principal Dinámico
        self.content_container = ctk.CTkFrame(self, width=880, height=340, fg_color="transparent")
        self.content_container.place(x=20, y=85)
        self.content_container.lift()

        # Inicializar Pestañas en Memoria
        self.switch_tab("noticias")

        # 5. Panel de Control Inferior (Jugar, Descargas, Estado)
        self.control_frame = ctk.CTkFrame(self, width=880, height=105, fg_color="#0A0A0A", corner_radius=12,
                                          border_color="#2D2D2D", border_width=1)
        self.control_frame.place(x=20, y=440)
        self.control_frame.lift()

        # Botón gigante JUGAR
        self.play_btn = ctk.CTkButton(self.control_frame, text="JUGAR", font=self.play_font,
                                      fg_color="#A83232", hover_color="#801D1D", text_color="#FFFFFF",
                                      width=240, height=75, corner_radius=10, border_color="#D4AF37", border_width=1,
                                      command=self.launch_game)
        self.play_btn.place(x=620, y=15)

        # Estado del cliente / descargas
        self.status_label = ctk.CTkLabel(self.control_frame, text="Listo para iniciar.", 
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
                                         text_color="#E0E0E0", anchor="w", width=580)
        self.status_label.place(x=20, y=15)

        # Detalles del motor de descarga (Velocidad, ETA, porcentaje)
        self.download_details_label = ctk.CTkLabel(self.control_frame, text="", 
                                                   font=ctk.CTkFont(family="Inter", size=12, weight="normal"), 
                                                   text_color="#888888", anchor="e", width=220)
        self.download_details_label.place(x=380, y=45)

        # Barra de progreso premium
        self.progress_bar = ctk.CTkProgressBar(self.control_frame, width=580, height=8, progress_color="#A83232", fg_color="#222222")
        self.progress_bar.place(x=20, y=70)
        self.progress_bar.set(0)

        # Verificar estado del juego e inicializar el botón JUGAR / DESCARGAR
        self.check_game_client_status()

    def switch_tab(self, tab_name):
        """Alterna el contenido del contenedor principal dinámicamente"""
        # Limpiar el contenedor
        for widget in self.content_container.winfo_children():
            widget.destroy()

        # Resetear estilos de botones de navegación
        self.tab_noticias_btn.configure(fg_color="#1E1E1E", text_color="#E0E0E0")
        self.tab_addons_btn.configure(fg_color="#1E1E1E", text_color="#E0E0E0")
        self.tab_ajustes_btn.configure(fg_color="#1E1E1E", text_color="#E0E0E0")

        if tab_name == "noticias":
            self.tab_noticias_btn.configure(fg_color="#A83232", text_color="#FFFFFF")
            self.render_noticias_tab()
        elif tab_name == "addons":
            self.tab_addons_btn.configure(fg_color="#A83232", text_color="#FFFFFF")
            self.render_addons_tab()
        elif tab_name == "ajustes":
            self.tab_ajustes_btn.configure(fg_color="#A83232", text_color="#FFFFFF")
            self.render_ajustes_tab()

    # RENDER DE PESTAÑAS
    def render_noticias_tab(self):
        # Diseño con panel de bienvenida y logo
        # Panel Izquierdo (Motto e Info del Clan)
        left_card = ctk.CTkFrame(self.content_container, width=520, height=340, fg_color="#0F0F0F", corner_radius=12,
                                 border_color="#A83232", border_width=1)
        left_card.place(x=0, y=0)

        welcome_title = ctk.CTkLabel(left_card, text="BIENVENIDO A LA SECTA DEL TERROR", 
                                     font=ctk.CTkFont(family="Cinzel", size=18, weight="bold"), 
                                     text_color="#A83232")
        welcome_title.place(x=20, y=20)

        welcome_desc = ctk.CTkLabel(left_card, text="\"La muerte es solo el comienzo. Caminamos entre las sombras para\nconquistar el mundo de Capycraft. Únete a nuestro séquito y reclama tu gloria.\"", 
                                    font=ctk.CTkFont(family="Cinzel", size=12, weight="normal"), 
                                    text_color="#D4AF37", justify="left")
        welcome_desc.place(x=20, y=55)

        # Tablón de anuncios estático de alta calidad
        news_frame = ctk.CTkFrame(left_card, width=480, height=190, fg_color="#1A1A1A", corner_radius=8)
        news_frame.place(x=20, y=120)

        news_label = ctk.CTkLabel(news_frame, text="📢 ANUNCIOS DEL CLAN Y CONSEJOS", 
                                  font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
                                  text_color="#FFFFFF")
        news_label.place(x=15, y=10)

        tips_text = (
            "• Servidor Oficial: Capycraft.io - Classic+ en versión 1.18.1.\n"
            "• ¡Verifica tu Addon de Traducción en la pestaña de Addons del Clan!\n"
            "• En caso de bugs visuales o de addons, usa el botón de Limpiar Caché.\n"
            "• Para jugar en ventana o ajustar FPS, ve a la pestaña de Ajustes.\n"
            "• Mantén activado el Discord Rich Presence para mostrar tu progreso."
        )
        tips_label = ctk.CTkLabel(news_frame, text=tips_text, 
                                  font=ctk.CTkFont(family="Inter", size=12, weight="normal"), 
                                  text_color="#CCCCCC", justify="left")
        tips_label.place(x=15, y=40)

        # Panel Derecho (Visual y Links Rápidos)
        right_card = ctk.CTkFrame(self.content_container, width=340, height=340, fg_color="#0F0F0F", corner_radius=12,
                                  border_color="#2D2D2D", border_width=1)
        right_card.place(x=540, y=0)

        if self.logo_image:
            logo_lbl = ctk.CTkLabel(right_card, image=self.logo_image, text="")
            logo_lbl.place(x=128, y=25)
        
        clan_motto = ctk.CTkLabel(right_card, text="EL SÉQUITO DEL TERROR", 
                                  font=ctk.CTkFont(family="Cinzel", size=14, weight="bold"), 
                                  text_color="#D4AF37")
        clan_motto.place(x=0, y=120, relwidth=1)

        # Botones de navegación externos
        btn_clan = ctk.CTkButton(right_card, text="PÁGINA WEB DEL CLAN", font=self.btn_font,
                                 fg_color="#1A1A1A", hover_color="#A83232", border_color="#A83232", border_width=1,
                                 width=280, height=38, text_color="#E0E0E0", corner_radius=8,
                                 command=lambda: webbrowser.open(self.config["clan_url"]))
        btn_clan.place(x=30, y=170)

        btn_game = ctk.CTkButton(right_card, text="WEB OFICIAL CAPYCRAFT", font=self.btn_font,
                                 fg_color="#1A1A1A", hover_color="#801D1D", border_color="#D4AF37", border_width=1,
                                 width=280, height=38, text_color="#E0E0E0", corner_radius=8,
                                 command=lambda: webbrowser.open(self.config["game_url"]))
        btn_game.place(x=30, y=225)

        btn_discord = ctk.CTkButton(right_card, text="ÚNETE A NUESTRO DISCORD", font=self.btn_font,
                                    fg_color="#1A1A1A", hover_color="#7289DA", border_color="#7289DA", border_width=1,
                                    width=280, height=38, text_color="#E0E0E0", corner_radius=8,
                                    command=lambda: webbrowser.open("https://discord.gg/capycraft"))
        btn_discord.place(x=30, y=280)

    def render_addons_tab(self):
        # Caja con scroll para los addons
        scroll_frame = ctk.CTkScrollableFrame(self.content_container, width=850, height=320, fg_color="#0F0F0F",
                                              border_color="#A83232", border_width=1, corner_radius=12)
        scroll_frame.place(x=0, y=0)

        title_lbl = ctk.CTkLabel(scroll_frame, text="🔌 GESTOR AUTOMÁTICO DE ADDONS DEL CLAN", 
                                 font=ctk.CTkFont(family="Cinzel", size=15, weight="bold"), 
                                 text_color="#D4AF37")
        title_lbl.pack(anchor="w", padx=15, pady=(10, 15))

        # Renderizar cada addon configurado
        for idx, addon in enumerate(self.config["addons"]):
            addon_id = addon["id"]
            name = addon["name"]
            desc = addon["desc"]
            folder = addon["folder_name"]
            url = addon.get("url", "")
            github_repo = addon.get("github_repo", "")
            if not url and github_repo:
                url = f"https://api.github.com/repos/{github_repo}/zipball"

            item_frame = ctk.CTkFrame(scroll_frame, height=80, fg_color="#1A1A1A", corner_radius=8)
            item_frame.pack(fill="x", padx=15, pady=8)

            # Texto informativo
            name_lbl = ctk.CTkLabel(item_frame, text=name, 
                                    font=ctk.CTkFont(family="Inter", size=13, weight="bold"), 
                                    text_color="#FFFFFF")
            name_lbl.place(x=15, y=10)

            desc_lbl = ctk.CTkLabel(item_frame, text=desc, 
                                    font=ctk.CTkFont(family="Inter", size=11, weight="normal"), 
                                    text_color="#AAAAAA", justify="left")
            desc_lbl.place(x=15, y=32)

            # Estado actual de instalación
            installed = self.check_addon_installed(folder)
            status_color = "#2ECC71" if installed else "#888888"
            status_text = "✓ Instalado" if installed else "No Instalado"

            status_lbl = ctk.CTkLabel(item_frame, text=status_text, 
                                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"), 
                                      text_color=status_color)
            status_lbl.place(x=520, y=25)

            # Botón de Descargar/Actualizar
            btn_text = "ACTUALIZAR" if installed else "INSTALAR"
            btn_dl = ctk.CTkButton(item_frame, text=btn_text, font=self.btn_font,
                                   fg_color="#A83232" if not installed else "#2A2A2A", 
                                   hover_color="#801D1D" if not installed else "#3D3D3D",
                                   width=130, height=32, corner_radius=6,
                                   command=lambda u=url, f=folder, i=item_frame: self.install_addon_async(u, f, i))
            if not url:
                btn_dl.configure(state="disabled", text="NO DISP.", fg_color="#333333")
            btn_dl.place(x=660, y=20)

    def render_ajustes_tab(self):
        left_card = ctk.CTkFrame(self.content_container, width=425, height=340, fg_color="#0F0F0F", corner_radius=12,
                                 border_color="#A83232", border_width=1)
        left_card.place(x=0, y=0)

        title_lbl1 = ctk.CTkLabel(left_card, text="⚙️ CONFIGURACIÓN DEL JUEGO", 
                                  font=ctk.CTkFont(family="Cinzel", size=14, weight="bold"), 
                                  text_color="#D4AF37")
        title_lbl1.place(x=20, y=20)

        # WTF Config Toggles
        self.windowed_var = ctk.BooleanVar(value=self.read_wtf_setting("windowedMode") == "1")
        toggle_win = ctk.CTkSwitch(left_card, text="Ejecutar en Modo Ventana", variable=self.windowed_var,
                                   font=ctk.CTkFont(family="Inter", size=12), progress_color="#A83232",
                                   command=lambda: self.write_wtf_setting("windowedMode", "1" if self.windowed_var.get() else "0"))
        toggle_win.place(x=30, y=65)

        self.fps_var = ctk.BooleanVar(value=self.read_wtf_setting("maxFPS") == "60")
        toggle_fps = ctk.CTkSwitch(left_card, text="Limitar FPS a 60 (Estabilidad)", variable=self.fps_var,
                                   font=ctk.CTkFont(family="Inter", size=12), progress_color="#A83232",
                                   command=lambda: self.write_wtf_setting("maxFPS", "60" if self.fps_var.get() else "0"))
        toggle_fps.place(x=30, y=105)

        self.drp_var = ctk.BooleanVar(value=True)
        toggle_drp = ctk.CTkSwitch(left_card, text="Activar Discord Rich Presence", variable=self.drp_var,
                                   font=ctk.CTkFont(family="Inter", size=12), progress_color="#A83232")
        toggle_drp.place(x=30, y=145)

        # Selector de Idioma (Locale)
        locale_lbl = ctk.CTkLabel(left_card, text="Idioma del Cliente (Locale):", 
                                  font=ctk.CTkFont(family="Inter", size=11, weight="bold"), 
                                  text_color="#E0E0E0")
        locale_lbl.place(x=30, y=185)

        self.locale_dropdown = ctk.CTkComboBox(left_card, values=["Español (esES)", "English (enUS)", "简体中文 (zhCN)"],
                                               font=ctk.CTkFont(family="Inter", size=12), width=220,
                                               command=self.change_locale_setting)
        self.locale_dropdown.place(x=30, y=210)

        # Leer idioma por defecto
        current_locale = self.read_wtf_setting("locale")
        if current_locale == "esES":
            default_val = "Español (esES)"
        elif current_locale == "zhCN":
            default_val = "简体中文 (zhCN)"
        else:
            default_val = "English (enUS)"
        self.locale_dropdown.set(default_val)

        lbl_desc = ctk.CTkLabel(left_card, text="Los ajustes anteriores modifican directamente tu archivo\nWTF/Config.wtf para optimizar el juego de manera segura.", 
                                font=ctk.CTkFont(family="Inter", size=11), text_color="#666666", justify="left")
        lbl_desc.place(x=30, y=275)

        # Panel de Mantenimiento Derecho
        right_card = ctk.CTkFrame(self.content_container, width=435, height=340, fg_color="#0F0F0F", corner_radius=12,
                                  border_color="#2D2D2D", border_width=1)
        right_card.place(x=445, y=0)

        title_lbl2 = ctk.CTkLabel(right_card, text="🛠️ MANTENIMIENTO DEL CLIENTE", 
                                  font=ctk.CTkFont(family="Cinzel", size=14, weight="bold"), 
                                  text_color="#A83232")
        title_lbl2.place(x=20, y=20)

        # Botones de Mantenimiento
        btn_cache = ctk.CTkButton(right_card, text="LIMPIAR CACHÉ (Carpeta WDB)", font=self.btn_font,
                                  fg_color="#1E1E1E", hover_color="#A83232", border_color="#A83232", border_width=1,
                                  width=375, height=45, text_color="#E0E0E0", corner_radius=8,
                                  command=self.clean_game_cache)
        btn_cache.place(x=30, y=70)

        btn_realm = ctk.CTkButton(right_card, text="FORZAR REPARACIÓN DE REALMLIST", font=self.btn_font,
                                  fg_color="#1E1E1E", hover_color="#801D1D", border_color="#D4AF37", border_width=1,
                                  width=375, height=45, text_color="#E0E0E0", corner_radius=8,
                                  command=self.manual_verify_realmlist)
        btn_realm.place(x=30, y=135)

        btn_repair = ctk.CTkButton(right_card, text="VERIFICAR INTEGRIDAD DE ARCHIVOS", font=self.btn_font,
                                   fg_color="#1E1E1E", hover_color="#2A2A2A",
                                   width=375, height=45, text_color="#888888", corner_radius=8,
                                   command=self.check_game_integrity)
        btn_repair.place(x=30, y=200)

    def change_locale_setting(self, selected_val):
        locale_map = {
            "Español (esES)": "esES",
            "English (enUS)": "enUS",
            "简体中文 (zhCN)": "zhCN"
        }
        selected_locale = locale_map.get(selected_val, "enUS")
        self.write_wtf_setting("locale", selected_locale)
        self.update_pfui_language(selected_locale)
        self.toggle_language_patch(selected_locale)
        
        if selected_locale == "esES":
            self.show_status("✓ Idioma Español configurado (Cliente y Addon).", "#D4AF37")
        else:
            self.show_status(f"✓ Idioma cambiado con éxito: {selected_locale}", "#2ECC71")

    def toggle_language_patch(self, locale):
        data_dir = "Data"
        if not os.path.exists(data_dir):
            return
            
        patch_es = os.path.join(data_dir, "patch-Z.mpq")
        patch_es_bak = os.path.join(data_dir, "patch-Z.mpq.bak")
        glue_strings = os.path.join(data_dir, "GlueStrings.lua")
        glue_strings_bak = os.path.join(data_dir, "GlueStrings.lua.bak")
        
        try:
            if locale == "esES":
                if os.path.exists(patch_es_bak):
                    os.rename(patch_es_bak, patch_es)
                if os.path.exists(glue_strings):
                    os.rename(glue_strings, glue_strings_bak)
            else:
                if os.path.exists(patch_es):
                    os.rename(patch_es, patch_es_bak)
                if os.path.exists(glue_strings_bak) and locale == "zhCN":
                    # Only restore Chinese loose files if locale is Chinese
                    os.rename(glue_strings_bak, glue_strings)
        except Exception as e:
            print(f"Error toggling language patch: {e}")

    def update_pfui_language(self, locale):
        account_dir = os.path.join("WTF", "Account")
        if not os.path.exists(account_dir):
            return
            
        force_region = "1" if locale in ["zhCN", "zhTW", "koKR"] else "0"
        
        for acc in os.listdir(account_dir):
            acc_path = os.path.join(account_dir, acc)
            if os.path.isdir(acc_path):
                sv_dir = os.path.join(acc_path, "SavedVariables")
                os.makedirs(sv_dir, exist_ok=True)
                pfui_lua = os.path.join(sv_dir, "pfUI.lua")
                
                try:
                    with open(pfui_lua, "a", encoding="utf-8") as f:
                        f.write(f'\nif not pfUI_config then pfUI_config = {{}} end\n')
                        f.write(f'if not pfUI_config["global"] then pfUI_config["global"] = {{}} end\n')
                        f.write(f'pfUI_config["global"]["language"] = "{locale}"\n')
                        f.write(f'pfUI_config["global"]["force_region"] = "{force_region}"\n')
                except Exception as e:
                    print(f"Error updating pfUI config for {acc}: {e}")

    # LÓGICA DE NEGOCIO Y OPERACIONES
    def check_addon_installed(self, folder_name):
        return os.path.exists(os.path.join("Interface", "AddOns", folder_name))

    def install_addon_async(self, url, folder_name, item_frame_widget):
        threading.Thread(target=self.download_and_extract_addon, args=(url, folder_name, item_frame_widget), daemon=True).start()

    def download_and_extract_addon(self, url, folder_name, item_frame):
        # Deshabilitar botones principales
        self.set_play_btn_state("disabled")
        
        # Encontrar los widgets del addon para actualizarlos visualmente
        status_label = None
        for widget in item_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") in ["✓ Instalado", "No Instalado"]:
                status_label = widget
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") in ["INSTALAR", "ACTUALIZAR"]:
                self.after(0, lambda w=widget: w.configure(state="disabled"))

        if status_label:
            self.after(0, lambda sl=status_label: sl.configure(text="Descargando...", text_color="#D4AF37"))

        temp_zip = os.path.join("Interface", "AddOns", "temp_addon.zip")
        os.makedirs(os.path.join("Interface", "AddOns"), exist_ok=True)

        try:
            self.show_status(f"Descargando Addon {folder_name}...", "#D4AF37")
            self.set_progress(0)

            # Descarga en segundo plano
            r = requests.get(url, stream=True)
            r.raise_for_status()
            total_size = r.headers.get('content-length')
            
            if total_size is None:
                with open(temp_zip, 'wb') as f:
                    f.write(r.content)
            else:
                dl = 0
                total_size = int(total_size)
                start_time = time.time()
                with open(temp_zip, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        dl += len(chunk)
                        f.write(chunk)
                        progress = dl / total_size
                        self.set_progress(progress)
                        
                        # Cálculos de Velocidad y ETA
                        elapsed = time.time() - start_time
                        speed = (dl / elapsed) if elapsed > 0 else 0
                        speed_mb = speed / (1024 * 1024)
                        eta = ((total_size - dl) / speed) if speed > 0 else 0
                        
                        self.show_download_details(speed_mb, eta, progress * 100)
            
            # Descompresión y renombrado inteligente
            self.show_status(f"Descomprimiendo Addon {folder_name}...", "#D4AF37")
            if status_label:
                self.after(0, lambda sl=status_label: sl.configure(text="Instalando..."))

            addons_root = os.path.join("Interface", "AddOns")
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                # Obtener la carpeta raíz del archivo ZIP (generalmente repositorio-master/)
                zip_contents = zip_ref.namelist()
                root_dir_in_zip = zip_contents[0].split('/')[0]
                
                # Extraer todo
                zip_ref.extractall(addons_root)

            # Si el directorio extraído no se llama igual que el destino, renombrar
            extracted_path = os.path.join(addons_root, root_dir_in_zip)
            target_path = os.path.join(addons_root, folder_name)

            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            os.rename(extracted_path, target_path)

            # Limpiar archivo temporal zip
            if os.path.exists(temp_zip):
                os.remove(temp_zip)

            self.show_status(f"✓ Addon {folder_name} instalado con éxito.", "#2ECC71")
            self.set_progress(1)
            self.clear_download_details()

            if status_label:
                self.after(0, lambda sl=status_label: sl.configure(text="✓ Instalado", text_color="#2ECC71"))

        except Exception as e:
            self.show_status(f"Error al instalar {folder_name}: {e}", "#A83232")
            if status_label:
                self.after(0, lambda sl=status_label: sl.configure(text="Error", text_color="#A83232"))
            if os.path.exists(temp_zip):
                os.remove(temp_zip)

        # Rehabilitar botones
        self.set_play_btn_state("normal")
        for widget in item_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") in ["INSTALAR", "ACTUALIZAR"]:
                self.after(0, lambda w=widget: w.configure(state="normal", text="ACTUALIZAR", fg_color="#2A2A2A", hover_color="#3D3D3D"))

    # OPERACIONES DEL WTF CONFIG
    def read_wtf_setting(self, setting_name):
        wtf_path = os.path.join("WTF", "Config.wtf")
        if not os.path.exists(wtf_path):
            return None
        try:
            with open(wtf_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f'SET {setting_name} '):
                        # Extrae el valor entre las comillas
                        parts = line.split('"')
                        if len(parts) >= 3:
                            return parts[1]
        except Exception:
            pass
        return None

    def write_wtf_setting(self, setting_name, value):
        wtf_dir = "WTF"
        os.makedirs(wtf_dir, exist_ok=True)
        wtf_path = os.path.join(wtf_dir, "Config.wtf")
        
        lines = []
        found = False
        setting_line = f'SET {setting_name} "{value}"\n'

        if os.path.exists(wtf_path):
            try:
                with open(wtf_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception:
                pass

        for idx, line in enumerate(lines):
            if line.strip().startswith(f'SET {setting_name} '):
                lines[idx] = setting_line
                found = True
                break

        if not found:
            lines.append(setting_line)

        try:
            with open(wtf_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            self.show_status(f"Configuración {setting_name} guardada correctamente.", "#D4AF37")
        except Exception as e:
            self.show_status(f"Error al escribir en Config.wtf: {e}", "#A83232")

    # MÓDULOS DE VERIFICACIÓN Y ASISTENCIA
    def auto_verify_realmlist(self):
        realmlist_path = "realmlist.wtf"
        correct_content = f'SET realmList "{self.config["realmlist"]}"\nSET patchList "{self.config["patchlist"]}"\n'
        
        # Eliminar atributo de solo lectura si existe
        if os.path.exists(realmlist_path):
            try:
                os.chmod(realmlist_path, 0o666)
            except Exception:
                pass

        needs_fix = True
        if os.path.exists(realmlist_path):
            try:
                with open(realmlist_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if self.config["realmlist"] in content:
                        needs_fix = False
            except Exception:
                pass

        if needs_fix:
            try:
                with open(realmlist_path, "w", encoding="utf-8") as f:
                    f.write(correct_content)
            except Exception:
                pass

    def manual_verify_realmlist(self):
        self.auto_verify_realmlist()
        self.show_status("✓ Realmlist reparado correctamente: apac.capycraft.io", "#2ECC71")

    def clean_game_cache(self):
        cache_dir = self.config["cache_dir"]
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                self.show_status("✓ Carpeta de caché (WDB) eliminada con éxito.", "#2ECC71")
            except Exception as e:
                self.show_status(f"Error al eliminar caché: {e}", "#A83232")
        else:
            self.show_status("La caché (WDB) ya está limpia.", "#D4AF37")

    def check_game_integrity(self):
        # Verifica la presencia de archivos core de WoW
        missing = []
        for file in [self.config["game_exe"], "realmlist.wtf", "SDL.dll", "Data/base.MPQ"]:
            if not os.path.exists(file):
                missing.append(file)
        
        if not missing:
            self.show_status("✓ Todos los archivos core del cliente están correctos.", "#2ECC71")
        else:
            self.show_status(f"Faltan archivos: {', '.join(missing)}", "#A83232")
    def show_status(self, text, color="#E0E0E0"):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def show_download_details(self, speed, eta, percentage):
        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta)) if eta < 86400 else "Lento"
        self.after(0, lambda: self.download_details_label.configure(
            text=f"{speed:.1f} MB/s | Restante: {eta_str} | {int(percentage)}%"
        ))

    def clear_download_details(self):
        self.after(0, lambda: self.download_details_label.configure(text=""))

    def set_progress(self, val):
        self.after(0, lambda: self.progress_bar.set(val))

    def set_play_btn_state(self, state):
        self.after(0, lambda: self.play_btn.configure(state=state))

    def safe_check_game_client_status(self):
        self.after(0, self.check_game_client_status)

    def launch_game(self):
        game_exe = self.config["game_exe"]
        if os.path.exists(game_exe):
            try:
                self.show_status("Iniciando WoW... ¡Que la sangre de tus enemigos riegue el camino!", "#2ECC71")
                subprocess.Popen([game_exe], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                self.game_running = True
                self.after(2000, self.iconify)
            except Exception as e:
                self.show_status(f"Error al ejecutar juego: {e}", "#A83232")
        else:
            self.show_status(f"No se encontró '{game_exe}'. Asegúrate de colocar el launcher en la carpeta raíz.", "#A83232")

    def check_game_client_status(self):
        game_exe = self.config["game_exe"]
        if os.path.exists(game_exe):
            self.play_btn.configure(text="JUGAR", fg_color="#A83232", hover_color="#801D1D", text_color="#FFFFFF", command=self.launch_game)
            self.show_status("Listo para iniciar.", "#E0E0E0")
        else:
            self.play_btn.configure(text="DESCARGAR JUEGO", fg_color="#D4AF37", hover_color="#B3922E", text_color="#000000", command=self.start_client_download)
            self.show_status("No se detectó WoW.exe. Haz clic en DESCARGAR JUEGO para preparar todo el cliente.", "#D4AF37")

    def start_client_download(self):
        self.play_btn.configure(state="disabled")
        threading.Thread(target=self.download_full_game_client, daemon=True).start()

    def download_full_game_client(self):
        url = self.config.get("client_zip_url", "")
        if not url:
            self.show_status("Por favor, descarga el juego desde el sitio web oficial de Capycraft.", "#A83232")
            webbrowser.open(self.config["game_url"])
            self.set_play_btn_state("normal")
            return
 
        temp_zip = "wow_client_temp.zip"
        try:
            self.show_status("Descargando juego completo base (3GB - 5GB)...", "#D4AF37")
            self.set_progress(0)
 
            # Descargar archivo ZIP con medición de velocidad y ETA
            r = requests.get(url, stream=True)
            r.raise_for_status()
            total_size = r.headers.get('content-length')
            
            if total_size is None:
                with open(temp_zip, 'wb') as f:
                    f.write(r.content)
            else:
                dl = 0
                total_size = int(total_size)
                start_time = time.time()
                with open(temp_zip, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):  # Tamaño de bloque más grande para velocidad
                        dl += len(chunk)
                        f.write(chunk)
                        progress = dl / total_size
                        self.set_progress(progress)
                        
                        # Cálculos de velocidad y tiempo estimado
                        elapsed = time.time() - start_time
                        speed = (dl / elapsed) if elapsed > 0 else 0
                        speed_mb = speed / (1024 * 1024)
                        eta = ((total_size - dl) / speed) if speed > 0 else 0
                        
                        self.show_download_details(speed_mb, eta, progress * 100)
 
            # Descompresión robusta del juego base
            self.show_status("Descomprimiendo archivos del juego... (Esto puede tomar unos minutos)", "#D4AF37")
            self.clear_download_details()
            
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                namelist = zip_ref.namelist()
                # Detectar si todo está dentro de un directorio de primer nivel
                first_item = namelist[0].split('/')[0] if '/' in namelist[0] else None
                is_single_dir = first_item and all(name.startswith(first_item + '/') or name == first_item for name in namelist)
 
                zip_ref.extractall(".")
 
                if is_single_dir:
                    # Mover los archivos de la subcarpeta extraída a la raíz
                    subfolder_path = os.path.abspath(first_item)
                    for item in os.listdir(subfolder_path):
                        shutil.move(os.path.join(subfolder_path, item), ".")
                    os.rmdir(subfolder_path)
 
            # Limpiar zip temporal
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
 
            # Forzar la escritura del realmlist.wtf por seguridad
            self.auto_verify_realmlist()
 
            self.show_status("✓ ¡Juego completo descargado e instalado con éxito!", "#2ECC71")
            self.set_progress(1.0)
            
        except Exception as e:
            self.show_status(f"Error al descargar juego: {e}", "#A83232")
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
 
        # Rehabilitar botón y verificar el nuevo estado (se configurará como JUGAR)
        self.set_play_btn_state("normal")
        self.safe_check_game_client_status()

    # SERVICIOS EN SEGUNDO PLANO (PING Y DISCORD RICH PRESENCE)
    def live_ping_worker(self):
        host = self.config["realmlist"]
        # El puerto oficial de WoW es 3724. Hacemos un ping de puerto TCP súper rápido
        port = 80  # Port 80 is safe for web connection check
        
        while True:
            try:
                start = time.time()
                # Crear socket TCP
                s = socket.create_connection((host, port), timeout=4)
                latency = int((time.time() - start) * 1000)
                s.close()
                self.ping_indicator.configure(text=f"● ONLINE | Latencia: {latency} ms", text_color="#2ECC71")
            except Exception:
                # Probar con puerto de juego alternativo 3724
                try:
                    start = time.time()
                    s = socket.create_connection((host, 3724), timeout=3)
                    latency = int((time.time() - start) * 1000)
                    s.close()
                    self.ping_indicator.configure(text=f"● ONLINE | Latencia: {latency} ms", text_color="#2ECC71")
                except Exception:
                    self.ping_indicator.configure(text="● OFFLINE", text_color="#A83232")
            
            time.sleep(15)

    def discord_presence_worker(self):
        if not PRESENCE_AVAILABLE:
            return
        
        client_id = "1243309033324646452"  # Client ID creado para WoW Capycraft Séquito
        try:
            self.discord_client = Presence(client_id)
            self.discord_client.connect()
        except Exception:
            # Discord no está abierto, reintentar cada 60s
            self.discord_client = None

        while True:
            if not self.drp_var.get():
                if self.discord_client:
                    try:
                        self.discord_client.clear()
                    except Exception:
                        pass
                time.sleep(10)
                continue

            # Verificar si Discord se abrió si antes estaba apagado
            if self.discord_client is None:
                try:
                    self.discord_client = Presence(client_id)
                    self.discord_client.connect()
                except Exception:
                    self.discord_client = None
                    time.sleep(60)
                    continue

            try:
                # Comprobar si el proceso WoW.exe está en ejecución
                wow_running = False
                if self.game_running:
                    # Método básico para verificar si WoW.exe sigue ejecutándose
                    # En Windows, podemos buscar en los procesos activos de manera silenciosa
                    output = subprocess.check_output('tasklist /FI "IMAGENAME eq WoW.exe"', shell=True).decode('utf-8', errors='ignore')
                    if "WoW.exe" in output:
                        wow_running = True
                    else:
                        self.game_running = False
                        self.show_status("Listo para iniciar.", "#E0E0E0")
                        self.deiconify()  # Volver a mostrar el launcher cuando se cierra WoW

                if wow_running:
                    self.discord_client.update(
                        state="En el clan: El Séquito del Terror",
                        details="Jugando en Capycraft.io (Classic+)",
                        large_image="logo",  # Nombre del asset cargado en el panel de desarrollador de Discord
                        large_text="Séquito del Terror",
                        small_image="wow",
                        small_text="World of Warcraft v1.18.1",
                        start=time.time()
                    )
                else:
                    self.discord_client.update(
                        state="Explorando el launcher",
                        details="Clan: El Séquito del Terror",
                        large_image="logo",
                        large_text="Entorno del Clan",
                        small_image="wow"
                    )
            except Exception:
                # Si se cae la conexión de Discord
                self.discord_client = None

            time.sleep(12)


if __name__ == "__main__":
    app = WoWLauncher()
    app.mainloop()
