import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import time
import json
import os
import shutil
import webbrowser

CONFIG_FILE = "devstudio_config.json"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

CONFIG_DEFAULT = {
    "php_exe": r"C:\php\php.exe",
    "mysqld_exe": r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe",
    "mysql_exe": r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
    "mysqladmin_exe": r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqladmin.exe",
    "composer_exe": "composer",
    "puerto_php": "8000",
    "ruta_actual": r"C:\Documentos\local",
    "proyectos_guardados": [r"C:\Documentos\local"],
    "perfiles_mysql": {
        "Root (Admin)": {"user": "root", "pass": "Likxusub.13"},
        "Laravel User": {"user": "laravelUser", "pass": "LarVel.@10"}
    }
}


# ==============================================================================
# MODAL 1: ASISTENTE DE NUEVO PROYECTO (PHP NATIVO O LARAVEL)
# ==============================================================================
class VentanaNuevoProyecto(ctk.CTkToplevel):
    def __init__(self, master, ruta_base_inicial, composer_bin, on_proyecto_creado):
        super().__init__(master)
        self.composer_bin = composer_bin
        self.on_proyecto_creado = on_proyecto_creado
        self.creando = False

        self.title("Nuevo Proyecto — DevStudio")
        self.geometry("580x440")
        self.resizable(False, False)
        self.transient(master)
        self.after(100, self.grab_set)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self, text="Crear Nuevo Proyecto", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(16, 10), sticky="w"
        )

        form = ctk.CTkFrame(self, corner_radius=10)
        form.grid(row=1, column=0, padx=20, pady=4, sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Ubicación:").grid(row=0, column=0, padx=(14, 8), pady=(14, 8), sticky="w")
        self.entry_ubicacion = ctk.CTkEntry(form)
        ruta_inicial = ruta_base_inicial if os.path.isdir(ruta_base_inicial) else r"C:\Documentos\local"
        self.entry_ubicacion.insert(0, ruta_inicial)
        self.entry_ubicacion.grid(row=0, column=1, padx=4, pady=(14, 8), sticky="ew")
        ctk.CTkButton(form, text="...", width=40, fg_color="#334155", command=self.elegir_ubicacion).grid(
            row=0, column=2, padx=(4, 14), pady=(14, 8)
        )

        ctk.CTkLabel(form, text="Nombre:").grid(row=1, column=0, padx=(14, 8), pady=8, sticky="w")
        self.entry_nombre = ctk.CTkEntry(form, placeholder_text="ej. sistema-ventas (sin espacios)")
        self.entry_nombre.grid(row=1, column=1, columnspan=2, padx=(4, 14), pady=8, sticky="ew")

        ctk.CTkLabel(form, text="Plantilla:").grid(row=2, column=0, padx=(14, 8), pady=(8, 14), sticky="w")
        self.combo_tipo = ctk.CTkOptionMenu(form, values=["Laravel (Composer)", "PHP Nativo (Limpio)"])
        self.combo_tipo.grid(row=2, column=1, padx=4, pady=(8, 14), sticky="w")

        self.chk_git = ctk.CTkCheckBox(form, text="Inicializar Git")
        self.chk_git.select()
        self.chk_git.grid(row=2, column=2, padx=(4, 14), pady=(8, 14), sticky="e")

        self.btn_crear = ctk.CTkButton(
            self, text="Crear Proyecto", height=36, fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"), command=self.iniciar_creacion
        )
        self.btn_crear.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.out_progreso = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#0F172A")
        self.out_progreso.insert("1.0", "Listo para crear tu proyecto...\n")
        self.out_progreso.grid(row=4, column=0, padx=20, pady=(0, 18), sticky="nsew")

    def elegir_ubicacion(self):
        carpeta = filedialog.askdirectory(initialdir=self.entry_ubicacion.get())
        if carpeta:
            self.entry_ubicacion.delete(0, "end")
            self.entry_ubicacion.insert(0, carpeta)

    def log(self, texto):
        self.out_progreso.insert("end", texto)
        self.out_progreso.see("end")

    def iniciar_creacion(self):
        if self.creando:
            return
        ubicacion = self.entry_ubicacion.get().strip()
        nombre = self.entry_nombre.get().strip().replace(" ", "-")
        if not ubicacion or not os.path.isdir(ubicacion):
            messagebox.showerror("Error", "Selecciona una carpeta de ubicación válida.", parent=self)
            return
        if not nombre:
            messagebox.showwarning("Falta nombre", "Escribe un nombre para la carpeta del proyecto.", parent=self)
            return

        ruta_final = os.path.join(ubicacion, nombre)
        if os.path.exists(ruta_final):
            messagebox.showerror("Ya existe", f"La carpeta '{nombre}' ya existe en esa ubicación.", parent=self)
            return

        self.creando = True
        self.btn_crear.configure(state="disabled", text="Creando proyecto...")
        self.out_progreso.delete("1.0", "end")

        tipo = self.combo_tipo.get()
        usar_git = self.chk_git.get() == 1

        def tarea():
            try:
                if "PHP Nativo" in tipo:
                    os.makedirs(ruta_final, exist_ok=True)
                    index_php = os.path.join(ruta_final, "index.php")
                    with open(index_php, "w", encoding="utf-8") as f:
                        f.write(
                            f"<?php\n// Proyecto: {nombre}\n"
                            f"echo '<h1>Proyecto {nombre} activo</h1>';\n"
                            f"echo '<p>PHP ' . phpversion() . '</p>';\n"
                        )
                    self.after(0, self.log, f"✔ Carpeta creada: {ruta_final}\n✔ Archivo index.php generado.\n")
                else:
                    self.after(0, self.log, f"$ composer create-project laravel/laravel {nombre}\nDescargando Laravel, esto puede tardar un momento...\n\n")
                    cmd = [self.composer_bin, "create-project", "laravel/laravel", nombre, "--no-interaction", "--no-ansi"]
                    proc = subprocess.Popen(
                        cmd, cwd=ubicacion, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, creationflags=NO_WINDOW
                    )
                    for linea in proc.stdout:
                        self.after(0, self.log, linea)
                    proc.wait()
                    if proc.returncode != 0:
                        self.after(0, self.log, "\n✖ Error al crear el proyecto Laravel.\n")
                        self.after(0, self._restaurar_boton)
                        return

                if usar_git:
                    subprocess.run(["git", "init"], cwd=ruta_final, capture_output=True, creationflags=NO_WINDOW)
                    self.after(0, self.log, "✔ Repositorio Git inicializado.\n")

                self.after(0, self.log, "\n✔ ¡Proyecto listo! Cargando entorno...\n")
                self.after(800, lambda: self._finalizar_exito(ruta_final))
            except FileNotFoundError:
                self.after(0, self.log, "✖ Error: No se encontró Composer en el sistema.\n")
                self.after(0, self._restaurar_boton)

        threading.Thread(target=tarea, daemon=True).start()

    def _restaurar_boton(self):
        self.creando = False
        self.btn_crear.configure(state="normal", text="Crear Proyecto")

    def _finalizar_exito(self, ruta_final):
        self.on_proyecto_creado(ruta_final)
        self.destroy()


# ==============================================================================
# MODAL 2: CONFIGURACIÓN DE PERFILES MYSQL Y RUTAS DEL SISTEMA
# ==============================================================================
class VentanaConfiguracion(ctk.CTkToplevel):
    def __init__(self, master, config_data, on_guardar_todo):
        super().__init__(master)
        self.config_data = config_data
        self.on_guardar_todo = on_guardar_todo

        self.title("Configuración — Perfiles MySQL y Entorno")
        self.geometry("620x490")
        self.resizable(False, False)
        self.transient(master)
        self.after(100, self.grab_set)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(self, corner_radius=10)
        self.tabs.grid(row=0, column=0, padx=18, pady=14, sticky="nsew")
        self.tabs.add("Perfiles de MySQL")
        self.tabs.add("Rutas y Puerto")

        self._construir_tab_perfiles()
        self._construir_tab_rutas()

    def _construir_tab_perfiles(self):
        tab = self.tabs.tab("Perfiles de MySQL")
        tab.grid_columnconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(tab, fg_color="transparent")
        top_bar.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 14), sticky="ew")
        top_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_bar, text="Editar existente:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(0, 8))
        nombres = list(self.config_data["perfiles_mysql"].keys())
        self.combo_editar_perfil = ctk.CTkOptionMenu(top_bar, values=nombres, command=self.cargar_datos_perfil)
        self.combo_editar_perfil.grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            top_bar, text="+ Nuevo Perfil", width=120, fg_color="#4F46E5", hover_color="#4338CA",
            command=self.preparar_nuevo_perfil
        ).grid(row=0, column=2, padx=(8, 0))

        card = ctk.CTkFrame(tab, corner_radius=10, fg_color="#1E293B")
        card.grid(row=1, column=0, columnspan=2, padx=10, pady=4, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="Nombre del Perfil:").grid(row=0, column=0, padx=(16, 10), pady=(16, 8), sticky="w")
        self.entry_perfil_nombre = ctk.CTkEntry(card, placeholder_text="ej. Perfil 3 (Cliente Web)")
        self.entry_perfil_nombre.grid(row=0, column=1, padx=(0, 16), pady=(16, 8), sticky="ew")

        ctk.CTkLabel(card, text="Usuario MySQL:").grid(row=1, column=0, padx=(16, 10), pady=8, sticky="w")
        self.entry_perfil_user = ctk.CTkEntry(card, placeholder_text="ej. root o laravelUser")
        self.entry_perfil_user.grid(row=1, column=1, padx=(0, 16), pady=8, sticky="ew")

        ctk.CTkLabel(card, text="Contraseña:").grid(row=2, column=0, padx=(16, 10), pady=(8, 16), sticky="w")
        pass_frame = ctk.CTkFrame(card, fg_color="transparent")
        pass_frame.grid(row=2, column=1, padx=(0, 16), pady=(8, 16), sticky="ew")
        pass_frame.grid_columnconfigure(0, weight=1)

        self.entry_perfil_pass = ctk.CTkEntry(pass_frame, show="*", placeholder_text="(Vacío si no tiene contraseña)")
        self.entry_perfil_pass.grid(row=0, column=0, sticky="ew")
        self.btn_ver_pass = ctk.CTkButton(pass_frame, text="Ver", width=50, fg_color="#334155", command=self.toggle_mostrar_pass)
        self.btn_ver_pass.grid(row=0, column=1, padx=(6, 0))

        btns = ctk.CTkFrame(tab, fg_color="transparent")
        btns.grid(row=2, column=0, columnspan=2, padx=10, pady=(16, 8), sticky="ew")

        ctk.CTkButton(
            btns, text="Guardar Perfil", width=150, height=36, fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"), command=self.guardar_perfil
        ).pack(side="left")

        ctk.CTkButton(
            btns, text="Eliminar Perfil", width=130, height=36, fg_color="#EF4444", hover_color="#DC2626",
            command=self.eliminar_perfil
        ).pack(side="right")

        self.lbl_feedback_perfil = ctk.CTkLabel(tab, text="", text_color="#34D399", font=ctk.CTkFont(size=12))
        self.lbl_feedback_perfil.grid(row=3, column=0, columnspan=2, padx=10, pady=6, sticky="w")

        if nombres:
            self.cargar_datos_perfil(nombres[0])

    def cargar_datos_perfil(self, nombre_perfil):
        datos = self.config_data["perfiles_mysql"].get(nombre_perfil, {"user": "", "pass": ""})
        self.entry_perfil_nombre.delete(0, "end")
        self.entry_perfil_nombre.insert(0, nombre_perfil)
        self.entry_perfil_user.delete(0, "end")
        self.entry_perfil_user.insert(0, datos.get("user", ""))
        self.entry_perfil_pass.delete(0, "end")
        self.entry_perfil_pass.insert(0, datos.get("pass", ""))
        self.lbl_feedback_perfil.configure(text="")

    def preparar_nuevo_perfil(self):
        self.entry_perfil_nombre.delete(0, "end")
        self.entry_perfil_user.delete(0, "end")
        self.entry_perfil_pass.delete(0, "end")
        self.entry_perfil_nombre.focus()
        self.lbl_feedback_perfil.configure(text="Escribe los datos del nuevo perfil y pulsa 'Guardar Perfil'.", text_color="#38BDF8")

    def toggle_mostrar_pass(self):
        actual = self.entry_perfil_pass.cget("show")
        self.entry_perfil_pass.configure(show="" if actual == "*" else "*")

    def guardar_perfil(self):
        nombre = self.entry_perfil_nombre.get().strip()
        usuario = self.entry_perfil_user.get().strip()
        password = self.entry_perfil_pass.get()

        if not nombre or not usuario:
            messagebox.showwarning("Datos incompletos", "El nombre del perfil y el usuario de MySQL son obligatorios.", parent=self)
            return

        self.config_data["perfiles_mysql"][nombre] = {"user": usuario, "pass": password}
        nombres = list(self.config_data["perfiles_mysql"].keys())
        self.combo_editar_perfil.configure(values=nombres)
        self.combo_editar_perfil.set(nombre)

        self.on_guardar_todo(perfil_seleccionado=nombre)
        self.lbl_feedback_perfil.configure(text=f"✔ Perfil '{nombre}' guardado y disponible en la lista.", text_color="#34D399")

    def eliminar_perfil(self):
        nombre = self.entry_perfil_nombre.get().strip()
        if nombre not in self.config_data["perfiles_mysql"]:
            return
        if len(self.config_data["perfiles_mysql"]) <= 1:
            messagebox.showwarning("Acción no permitida", "Debe existir al menos un perfil de MySQL configurado.", parent=self)
            return

        del self.config_data["perfiles_mysql"][nombre]
        nombres = list(self.config_data["perfiles_mysql"].keys())
        self.combo_editar_perfil.configure(values=nombres)
        self.combo_editar_perfil.set(nombres[0])
        self.cargar_datos_perfil(nombres[0])

        self.on_guardar_todo(perfil_seleccionado=nombres[0])
        self.lbl_feedback_perfil.configure(text=f"Perfil '{nombre}' eliminado.", text_color="#FBBF24")

    def _construir_tab_rutas(self):
        tab = self.tabs.tab("Rutas y Puerto")
        tab.grid_columnconfigure(1, weight=1)

        campos = [
            ("Puerto PHP:", "puerto_php"),
            ("PHP (php.exe):", "php_exe"),
            ("Motor MySQL (mysqld.exe):", "mysqld_exe"),
            ("Cliente MySQL (mysql.exe):", "mysql_exe"),
            ("Admin MySQL (mysqladmin.exe):", "mysqladmin_exe"),
            ("Composer:", "composer_exe"),
        ]
        self.entries_rutas = {}

        for idx, (etiqueta, clave) in enumerate(campos):
            ctk.CTkLabel(tab, text=etiqueta).grid(row=idx, column=0, padx=(12, 8), pady=6, sticky="w")
            entry = ctk.CTkEntry(tab)
            entry.insert(0, self.config_data.get(clave, ""))
            entry.grid(row=idx, column=1, padx=4, pady=6, sticky="ew")
            self.entries_rutas[clave] = entry

            if clave != "puerto_php":
                ctk.CTkButton(
                    tab, text="...", width=36, fg_color="#334155",
                    command=lambda e=entry: self._buscar_exe(e)
                ).grid(row=idx, column=2, padx=(4, 12), pady=6)

        ctk.CTkButton(
            tab, text="Guardar Rutas y Puerto", height=36, fg_color="#10B981", hover_color="#059669",
            font=ctk.CTkFont(weight="bold"), command=self.guardar_rutas
        ).grid(row=len(campos), column=0, columnspan=3, padx=12, pady=(16, 8), sticky="ew")

    def _buscar_exe(self, entry_widget):
        archivo = filedialog.askopenfilename(title="Seleccionar ejecutable")
        if archivo:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, archivo)

    def guardar_rutas(self):
        for clave, entry in self.entries_rutas.items():
            val = entry.get().strip()
            if val:
                self.config_data[clave] = val
        self.on_guardar_todo()
        messagebox.showinfo("Guardado", "Rutas y puerto actualizados correctamente.", parent=self)


# ==============================================================================
# APLICACIÓN PRINCIPAL: DEVSTUDIO
# ==============================================================================
class DevStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        os.makedirs(r"C:\Documentos\local", exist_ok=True)
        self.config_data = self.cargar_config()
        self.procesos = {"php": None, "mysql": None, "queue": None, "vite": None}

        self.title("DevStudio Control")
        self.geometry("1020x710")
        self.minsize(940, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.construir_ui()
        self.analizar_entorno_proyecto()
        self.sincronizar_estado_mysql()
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    def cargar_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**CONFIG_DEFAULT, **json.load(f)}
            except Exception:
                pass
        return CONFIG_DEFAULT.copy()

    def guardar_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4)

    def resolver_binario(self, nombre_o_ruta):
        if os.path.exists(nombre_o_ruta):
            return nombre_o_ruta
        return shutil.which(nombre_o_ruta) or nombre_o_ruta

    def construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- 1. BARRA SUPERIOR ---
        top_card = ctk.CTkFrame(self, corner_radius=12)
        top_card.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")
        top_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top_card, text="Proyecto:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(16, 8), pady=(14, 8), sticky="w"
        )

        self.combo_proyectos = ctk.CTkComboBox(
            top_card,
            values=self.config_data["proyectos_guardados"],
            command=self.cambiar_proyecto_guardado
        )
        self.combo_proyectos.set(self.config_data["ruta_actual"])
        self.combo_proyectos.grid(row=0, column=1, padx=4, pady=(14, 8), sticky="ew")

        ctk.CTkButton(top_card, text="Examinar", width=85, fg_color="#334155", command=self.seleccionar_ruta).grid(
            row=0, column=2, padx=3, pady=(14, 8)
        )
        ctk.CTkButton(top_card, text="+ Nuevo", width=82, fg_color="#10B981", hover_color="#059669", command=self.abrir_nuevo_proyecto).grid(
            row=0, column=3, padx=3, pady=(14, 8)
        )
        ctk.CTkButton(top_card, text="VS Code", width=78, fg_color="#0284C7", command=self.abrir_vscode).grid(
            row=0, column=4, padx=3, pady=(14, 8)
        )
        ctk.CTkButton(top_card, text="⚙ Ajustes", width=85, fg_color="#4F46E5", hover_color="#4338CA", command=self.abrir_configuracion).grid(
            row=0, column=5, padx=(3, 16), pady=(14, 8)
        )

        # Badges dinámicos
        badges_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        badges_frame.grid(row=1, column=0, columnspan=6, padx=16, pady=(0, 12), sticky="ew")

        self.lbl_badge_stack = ctk.CTkLabel(badges_frame, text="Stack: PHP Nativo", text_color="#38BDF8", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_badge_stack.pack(side="left", padx=(0, 16))

        self.lbl_badge_composer = ctk.CTkLabel(badges_frame, text="Composer: Sin composer.json", text_color="#94A3B8", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_badge_composer.pack(side="left", padx=(0, 16))

        self.lbl_badge_git = ctk.CTkLabel(badges_frame, text="Git: Sin repositorio", text_color="#94A3B8", font=ctk.CTkFont(size=12))
        self.lbl_badge_git.pack(side="left", padx=(0, 16))

        self.lbl_badge_docker = ctk.CTkLabel(badges_frame, text="Docker: Sin compose", text_color="#94A3B8", font=ctk.CTkFont(size=12))
        self.lbl_badge_docker.pack(side="left")

        # --- 2. TARJETAS DE SERVICIOS ---
        srv_grid = ctk.CTkFrame(self, fg_color="transparent")
        srv_grid.grid(row=1, column=0, padx=20, pady=4, sticky="ew")
        srv_grid.grid_columnconfigure((0, 1, 2), weight=1)

        c_php = ctk.CTkFrame(srv_grid, corner_radius=10, fg_color="#1E293B")
        c_php.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.lbl_php = ctk.CTkLabel(c_php, text="● PHP Detenido", text_color="#94A3B8", font=ctk.CTkFont(weight="bold"))
        self.lbl_php.pack(side="left", padx=12, pady=12)
        ctk.CTkButton(c_php, text="Web", width=48, fg_color="#0284C7", command=lambda: webbrowser.open(f"http://localhost:{self.config_data['puerto_php']}")).pack(side="right", padx=(2, 10))
        self.btn_php = ctk.CTkButton(c_php, text="Iniciar", width=72, fg_color="#10B981", command=self.toggle_php)
        self.btn_php.pack(side="right", padx=2)

        c_mysql = ctk.CTkFrame(srv_grid, corner_radius=10, fg_color="#1E293B")
        c_mysql.grid(row=0, column=1, padx=6, sticky="ew")
        self.lbl_mysql = ctk.CTkLabel(c_mysql, text="● MySQL Detenido", text_color="#94A3B8", font=ctk.CTkFont(weight="bold"))
        self.lbl_mysql.pack(side="left", padx=12, pady=12)
        self.btn_mysql = ctk.CTkButton(c_mysql, text="Iniciar", width=72, fg_color="#10B981", command=self.toggle_mysql)
        self.btn_mysql.pack(side="right", padx=10)

        c_vite = ctk.CTkFrame(srv_grid, corner_radius=10, fg_color="#1E293B")
        c_vite.grid(row=0, column=2, padx=(6, 0), sticky="ew")
        self.lbl_vite = ctk.CTkLabel(c_vite, text="● Vite / NPM Off", text_color="#94A3B8", font=ctk.CTkFont(weight="bold"))
        self.lbl_vite.pack(side="left", padx=12, pady=12)
        self.btn_vite = ctk.CTkButton(c_vite, text="Dev", width=72, fg_color="#6366F1", command=self.toggle_vite)
        self.btn_vite.pack(side="right", padx=10)

        # --- 3. PESTAÑAS MODULARES ---
        self.tabs = ctk.CTkTabview(self, corner_radius=12)
        self.tabs.grid(row=2, column=0, padx=20, pady=(6, 16), sticky="nsew")

        for nombre in ["Base de Datos (SQL)", "Laravel", "Composer", "Git", "Docker", "Logs Servidor"]:
            self.tabs.add(nombre)

        self._construir_tab_sql()
        self._construir_tab_laravel()
        self._construir_tab_composer()
        self._construir_tab_git()
        self._construir_tab_docker()
        self._construir_tab_logs()

    # --- SUB-VISTAS ---
    def _construir_tab_sql(self):
        tab = self.tabs.tab("Base de Datos (SQL)")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        ctk.CTkLabel(bar, text="Perfil activo:").pack(side="left", padx=(0, 8))

        self.combo_perfil = ctk.CTkOptionMenu(bar, values=list(self.config_data["perfiles_mysql"].keys()), width=200)
        self.combo_perfil.pack(side="left", padx=(0, 6))

        ctk.CTkButton(bar, text="+ Perfil", width=75, fg_color="#334155", command=self.abrir_configuracion).pack(side="left", padx=(0, 10))
        ctk.CTkButton(bar, text="Ver Bases de Datos", width=140, fg_color="#4F46E5", command=lambda: self.ejecutar_sql("SHOW DATABASES;")).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="▶ Ejecutar SQL", width=120, fg_color="#10B981", command=lambda: self.ejecutar_sql(self.txt_sql.get("1.0", "end").strip())).pack(side="right")

        self.txt_sql = ctk.CTkTextbox(tab, height=65, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_sql.insert("1.0", "SHOW DATABASES;")
        self.txt_sql.grid(row=1, column=0, padx=8, pady=4, sticky="ew")

        self.out_sql = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_sql.grid(row=2, column=0, padx=8, pady=(4, 8), sticky="nsew")

    def _construir_tab_laravel(self):
        tab = self.tabs.tab("Laravel")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")

        comandos = [
            ("Migrate", "migrate"),
            ("Fresh + Seed", "migrate:fresh --seed"),
            ("Optimize Clear", "optimize:clear"),
            ("Rutas", "route:list")
        ]
        for texto, arg in comandos:
            ctk.CTkButton(bar, text=texto, width=115, fg_color="#334155", command=lambda a=arg: self.ejecutar_artisan(a)).pack(side="left", padx=4)

        self.btn_queue = ctk.CTkButton(bar, text="▶ Queue Worker", width=130, fg_color="#D97706", command=self.toggle_queue)
        self.btn_queue.pack(side="right", padx=4)

        self.out_laravel = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_laravel.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="nsew")

    def _construir_tab_composer(self):
        tab = self.tabs.tab("Composer")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        bar_acciones = ctk.CTkFrame(tab, fg_color="transparent")
        bar_acciones.grid(row=0, column=0, padx=8, pady=(6, 4), sticky="ew")

        ctk.CTkButton(bar_acciones, text="Install", width=100, fg_color="#10B981", hover_color="#059669", command=lambda: self.ejecutar_composer(["install"])).pack(side="left", padx=4)
        ctk.CTkButton(bar_acciones, text="Update", width=100, fg_color="#0284C7", command=lambda: self.ejecutar_composer(["update"])).pack(side="left", padx=4)
        ctk.CTkButton(bar_acciones, text="Dump Autoload", width=125, fg_color="#334155", command=lambda: self.ejecutar_composer(["dump-autoload", "-o"])).pack(side="left", padx=4)
        ctk.CTkButton(bar_acciones, text="Ver Desactualizados", width=145, fg_color="#334155", command=lambda: self.ejecutar_composer(["outdated", "--direct"])).pack(side="left", padx=4)

        self.lbl_composer_estado = ctk.CTkLabel(bar_acciones, text="", text_color="#38BDF8", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_composer_estado.pack(side="right", padx=8)

        bar_pkg = ctk.CTkFrame(tab, fg_color="transparent")
        bar_pkg.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        bar_pkg.grid_columnconfigure(0, weight=1)

        self.entry_paquete = ctk.CTkEntry(bar_pkg, placeholder_text="Nombre del paquete (ej. laravel/sanctum, guzzlehttp/guzzle)...")
        self.entry_paquete.grid(row=0, column=0, padx=(4, 8), sticky="ew")

        self.chk_composer_dev = ctk.CTkCheckBox(bar_pkg, text="--dev", width=65)
        self.chk_composer_dev.grid(row=0, column=1, padx=4)

        ctk.CTkButton(bar_pkg, text="+ Require", width=100, fg_color="#4F46E5", command=lambda: self.gestionar_paquete_composer("require")).grid(row=0, column=2, padx=4)
        ctk.CTkButton(bar_pkg, text="- Remove", width=95, fg_color="#EF4444", command=lambda: self.gestionar_paquete_composer("remove")).grid(row=0, column=3, padx=(4, 4))

        self.out_composer = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_composer.grid(row=2, column=0, padx=8, pady=(4, 8), sticky="nsew")

    def _construir_tab_git(self):
        tab = self.tabs.tab("Git")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        ctk.CTkButton(top, text="Estado (Status)", width=120, fg_color="#334155", command=lambda: self.ejecutar_git(["status", "-s"])).pack(side="left", padx=4)
        ctk.CTkButton(top, text="↓ Git Pull", width=100, fg_color="#0284C7", command=lambda: self.ejecutar_git(["pull"])).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Historial", width=100, fg_color="#334155", command=lambda: self.ejecutar_git(["log", "--oneline", "-n", "12"])).pack(side="left", padx=4)

        commit_bar = ctk.CTkFrame(tab, fg_color="transparent")
        commit_bar.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        commit_bar.grid_columnconfigure(0, weight=1)
        self.entry_commit = ctk.CTkEntry(commit_bar, placeholder_text="Mensaje del commit...")
        self.entry_commit.grid(row=0, column=0, padx=(4, 8), sticky="ew")
        ctk.CTkButton(commit_bar, text="Commit & Push", width=130, fg_color="#10B981", command=self.git_commit_push).grid(row=0, column=1, padx=4)

        self.out_git = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_git.grid(row=2, column=0, padx=8, pady=(4, 8), sticky="nsew")

    def _construir_tab_docker(self):
        tab = self.tabs.tab("Docker")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        ctk.CTkButton(bar, text="▶ Compose Up -d", width=135, fg_color="#10B981", command=lambda: self.ejecutar_docker(["compose", "up", "-d"])).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="■ Compose Stop", width=130, fg_color="#EF4444", command=lambda: self.ejecutar_docker(["compose", "stop"])).pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Contenedores Activos", width=155, fg_color="#0284C7", command=lambda: self.ejecutar_docker(["ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])).pack(side="right", padx=4)

        self.out_docker = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_docker.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="nsew")

    def _construir_tab_logs(self):
        tab = self.tabs.tab("Logs Servidor")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(tab, fg_color="transparent")
        bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        ctk.CTkLabel(bar, text="Logs del servidor PHP en tiempo real", text_color="#94A3B8").pack(side="left", padx=4)
        ctk.CTkButton(bar, text="Limpiar Logs", width=100, fg_color="#334155", command=lambda: self.out_logs.delete("1.0", "end")).pack(side="right", padx=4)

        self.out_logs = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_logs.grid(row=1, column=0, padx=8, pady=(4, 8), sticky="nsew")

    # --- MODALES Y SINCRONIZACIÓN ---
    def abrir_nuevo_proyecto(self):
        composer_bin = self.resolver_binario(self.config_data["composer_exe"])
        VentanaNuevoProyecto(
            self,
            ruta_base_inicial=self.ruta_proyecto(),
            composer_bin=composer_bin,
            on_proyecto_creado=self.registrar_y_abrir_proyecto
        )

    def abrir_configuracion(self):
        VentanaConfiguracion(
            self,
            config_data=self.config_data,
            on_guardar_todo=self.al_actualizar_configuracion
        )

    def al_actualizar_configuracion(self, perfil_seleccionado=None):
        self.guardar_config()
        nombres = list(self.config_data["perfiles_mysql"].keys())
        self.combo_perfil.configure(values=nombres)
        if perfil_seleccionado and perfil_seleccionado in nombres:
            self.combo_perfil.set(perfil_seleccionado)
        elif self.combo_perfil.get() not in nombres and nombres:
            self.combo_perfil.set(nombres[0])

    def registrar_y_abrir_proyecto(self, ruta):
        if ruta not in self.config_data["proyectos_guardados"]:
            self.config_data["proyectos_guardados"].insert(0, ruta)
            self.combo_proyectos.configure(values=self.config_data["proyectos_guardados"])
        self.combo_proyectos.set(ruta)
        self.cambiar_proyecto_guardado(ruta)

    # --- DETECCIÓN DE ENTORNO ---
    def ruta_proyecto(self):
        return self.combo_proyectos.get().strip()

    def seleccionar_ruta(self):
        carpeta = filedialog.askdirectory(initialdir=self.ruta_proyecto())
        if carpeta:
            self.registrar_y_abrir_proyecto(carpeta)

    def cambiar_proyecto_guardado(self, ruta):
        self.config_data["ruta_actual"] = ruta
        self.guardar_config()
        self.analizar_entorno_proyecto()

    def analizar_entorno_proyecto(self):
        ruta = self.ruta_proyecto()
        if not os.path.isdir(ruta):
            return

        es_laravel = os.path.exists(os.path.join(ruta, "artisan"))
        self.lbl_badge_stack.configure(text="Stack: Laravel Framework" if es_laravel else "Stack: PHP Nativo")

        tiene_composer = os.path.exists(os.path.join(ruta, "composer.json"))
        tiene_vendor = os.path.isdir(os.path.join(ruta, "vendor"))
        if tiene_composer and tiene_vendor:
            self.lbl_badge_composer.configure(text="Composer: Listo", text_color="#34D399")
        elif tiene_composer:
            self.lbl_badge_composer.configure(text="Composer: Falta install", text_color="#FBBF24")
        else:
            self.lbl_badge_composer.configure(text="Composer: Sin composer.json", text_color="#94A3B8")

        if os.path.exists(os.path.join(ruta, ".git")):
            res = subprocess.run(["git", "-C", ruta, "branch", "--show-current"], capture_output=True, text=True, creationflags=NO_WINDOW)
            rama = res.stdout.strip() or "HEAD"
            self.lbl_badge_git.configure(text=f"Git: ⎇ {rama}", text_color="#34D399")
        else:
            self.lbl_badge_git.configure(text="Git: Sin repositorio", text_color="#94A3B8")

        tiene_docker = any(os.path.exists(os.path.join(ruta, f)) for f in ["docker-compose.yml", "docker-compose.yaml", "compose.yaml"])
        self.lbl_badge_docker.configure(
            text="Docker: Compose Listo" if tiene_docker else "Docker: Sin compose",
            text_color="#38BDF8" if tiene_docker else "#94A3B8"
        )

    def ejecutar_comando_async(self, cmd, widget_salida, cwd=None):
        def tarea():
            try:
                res = subprocess.run(cmd, cwd=cwd or self.ruta_proyecto(), capture_output=True, text=True, creationflags=NO_WINDOW)
                salida = res.stdout if res.returncode == 0 else f"{res.stdout}\n{res.stderr}"
                self.after(0, lambda: self._mostrar_en_caja(widget_salida, salida.strip() or "Comando completado sin salida."))
            except FileNotFoundError:
                self.after(0, lambda: self._mostrar_en_caja(widget_salida, f"Error: No se encontró '{cmd[0]}' en el sistema."))

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_en_caja(self, caja, texto):
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)

    def _anexar_en_caja(self, caja, linea):
        caja.insert("end", linea)
        caja.see("end")

    # --- COMPOSER ---
    def gestionar_paquete_composer(self, accion):
        paquete = self.entry_paquete.get().strip()
        if not paquete:
            messagebox.showwarning("Composer", "Escribe el nombre del paquete (ej. laravel/sanctum).")
            return
        args = [accion, paquete]
        if accion == "require" and self.chk_composer_dev.get() == 1:
            args.append("--dev")
        self.entry_paquete.delete(0, "end")
        self.ejecutar_composer(args)

    def ejecutar_composer(self, args):
        composer_bin = self.resolver_binario(self.config_data["composer_exe"])
        cmd = [composer_bin] + args + ["--no-interaction", "--no-ansi"]
        ruta = self.ruta_proyecto()

        self._mostrar_en_caja(self.out_composer, f"$ composer {' '.join(args)}\n" + "-" * 55 + "\n")
        self.lbl_composer_estado.configure(text="⏳ Ejecutando...")

        def tarea_stream():
            try:
                proc = subprocess.Popen(
                    cmd, cwd=ruta, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, creationflags=NO_WINDOW
                )
                for linea in proc.stdout:
                    self.after(0, self._anexar_en_caja, self.out_composer, linea)
                proc.wait()
                estado = "✔ Completado" if proc.returncode == 0 else f"✖ Error (código {proc.returncode})"
                self.after(0, lambda: self.lbl_composer_estado.configure(text=estado))
                self.after(0, self.analizar_entorno_proyecto)
            except FileNotFoundError:
                self.after(0, lambda: self._anexar_en_caja(self.out_composer, "Error: No se encontró Composer en el PATH del sistema."))
                self.after(0, lambda: self.lbl_composer_estado.configure(text="✖ No encontrado"))

        threading.Thread(target=tarea_stream, daemon=True).start()

    def _construir_tab_git(self):
        tab = self.tabs.tab("Git")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

        # Fila 0: Botones rápidos
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, padx=8, pady=(6, 4), sticky="ew")
        ctk.CTkButton(top, text="Inicializar Git", width=115, fg_color="#4F46E5", command=self.git_inicializar).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Estado (Status)", width=120, fg_color="#334155", command=lambda: self.ejecutar_git(["status", "-s"])).pack(side="left", padx=4)
        ctk.CTkButton(top, text="↓ Git Pull", width=95, fg_color="#0284C7", command=lambda: self.ejecutar_git(["pull"])).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Historial", width=95, fg_color="#334155", command=lambda: self.ejecutar_git(["log", "--oneline", "-n", "12"])).pack(side="left", padx=4)

        # Fila 1: Commit & Push
        commit_bar = ctk.CTkFrame(tab, fg_color="transparent")
        commit_bar.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        commit_bar.grid_columnconfigure(0, weight=1)
        self.entry_commit = ctk.CTkEntry(commit_bar, placeholder_text="Mensaje del commit...")
        self.entry_commit.grid(row=0, column=0, padx=(4, 8), sticky="ew")
        ctk.CTkButton(commit_bar, text="Commit & Push", width=130, fg_color="#10B981", command=self.git_commit_push).grid(row=0, column=1, padx=4)

        # Fila 2: Barra para ejecutar cualquier comando Git
        cmd_bar = ctk.CTkFrame(tab, fg_color="transparent")
        cmd_bar.grid(row=2, column=0, padx=8, pady=4, sticky="ew")
        cmd_bar.grid_columnconfigure(0, weight=1)
        self.entry_git_cmd = ctk.CTkEntry(cmd_bar, placeholder_text="Comando Git (ej. remote add origin https://... o branch -M main)")
        self.entry_git_cmd.grid(row=0, column=0, padx=(4, 8), sticky="ew")
        self.entry_git_cmd.bind("<Return>", lambda e: self.ejecutar_git_personalizado())
        ctk.CTkButton(cmd_bar, text="▶ Ejecutar", width=130, fg_color="#6366F1", command=self.ejecutar_git_personalizado).grid(row=0, column=1, padx=4)

        # Fila 3: Salida
        self.out_git = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#0F172A")
        self.out_git.grid(row=3, column=0, padx=8, pady=(4, 8), sticky="nsew")

    # --- SERVICIOS PHP, MYSQL 8.0 Y VITE ---
    def toggle_php(self):
        if self.procesos["php"] is None:
            ruta = self.ruta_proyecto()
            puerto = self.config_data["puerto_php"]
            artisan = os.path.join(ruta, "artisan")
            cmd = [self.config_data["php_exe"], artisan, "serve", f"--port={puerto}"] if os.path.exists(artisan) else [self.config_data["php_exe"], "-S", f"localhost:{puerto}", "-t", ruta]

            self.procesos["php"] = subprocess.Popen(cmd, cwd=ruta, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=NO_WINDOW)
            self.lbl_php.configure(text=f"● PHP :{puerto}", text_color="#34D399")
            self.btn_php.configure(text="Parar", fg_color="#EF4444")
            threading.Thread(target=self._leer_logs_php, daemon=True).start()
        else:
            self.procesos["php"].terminate()
            self.procesos["php"] = None
            self.lbl_php.configure(text="● PHP Detenido", text_color="#94A3B8")
            self.btn_php.configure(text="Iniciar", fg_color="#10B981")

    def _leer_logs_php(self):
        while self.procesos["php"] and self.procesos["php"].poll() is None:
            linea = self.procesos["php"].stdout.readline()
            if linea:
                self.after(0, self._anexar_en_caja, self.out_logs, linea)

    def mysql_esta_activo(self):
        res = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq mysqld.exe"],
            capture_output=True, text=True, creationflags=NO_WINDOW
        )
        return "mysqld.exe" in res.stdout.lower()

    def sincronizar_estado_mysql(self):
        if self.mysql_esta_activo():
            self.lbl_mysql.configure(text="● MySQL Activo", text_color="#34D399")
            self.btn_mysql.configure(text="Parar", fg_color="#EF4444")
        else:
            self.lbl_mysql.configure(text="● MySQL Detenido", text_color="#94A3B8")
            self.btn_mysql.configure(text="Iniciar", fg_color="#10B981")

    def toggle_mysql(self):
        if not self.mysql_esta_activo():
            mysqld = self.config_data["mysqld_exe"]
            my_ini = r"C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"
            cmd = [mysqld, f"--defaults-file={my_ini}"] if os.path.exists(my_ini) else [mysqld]

            self.procesos["mysql"] = subprocess.Popen(cmd, creationflags=NO_WINDOW)
            self.lbl_mysql.configure(text="● MySQL Activo", text_color="#34D399")
            self.btn_mysql.configure(text="Parar", fg_color="#EF4444")
        else:
            # Usa el perfil root (o el primer perfil) para apagar el motor de forma segura
            admin_perfil = next(
                (p for p in self.config_data["perfiles_mysql"].values() if p["user"].lower() == "root"),
                list(self.config_data["perfiles_mysql"].values())[0]
            )
            cmd = [self.config_data["mysqladmin_exe"], "-u", admin_perfil["user"]]
            if admin_perfil["pass"]:
                cmd.append(f"-p{admin_perfil['pass']}")
            cmd.append("shutdown")
            subprocess.run(cmd, creationflags=NO_WINDOW)
            self.procesos["mysql"] = None
            self.lbl_mysql.configure(text="● MySQL Detenido", text_color="#94A3B8")
            self.btn_mysql.configure(text="Iniciar", fg_color="#10B981")

    def toggle_vite(self):
        if self.procesos["vite"] is None:
            npm_bin = self.resolver_binario("npm")
            self.procesos["vite"] = subprocess.Popen([npm_bin, "run", "dev"], cwd=self.ruta_proyecto(), creationflags=NO_WINDOW)
            self.lbl_vite.configure(text="● Vite Activo", text_color="#34D399")
            self.btn_vite.configure(text="Parar", fg_color="#EF4444")
        else:
            self.procesos["vite"].terminate()
            self.procesos["vite"] = None
            self.lbl_vite.configure(text="● Vite / NPM Off", text_color="#94A3B8")
            self.btn_vite.configure(text="Dev", fg_color="#6366F1")

    def toggle_queue(self):
        if self.procesos["queue"] is None:
            self.procesos["queue"] = subprocess.Popen([self.config_data["php_exe"], "artisan", "queue:work"], cwd=self.ruta_proyecto(), creationflags=NO_WINDOW)
            self.btn_queue.configure(text="■ Parar Queue", fg_color="#EF4444")
        else:
            self.procesos["queue"].terminate()
            self.procesos["queue"] = None
            self.btn_queue.configure(text="▶ Queue Worker", fg_color="#D97706")

    def ejecutar_sql(self, query):
        arranco_ahora = False
        if not self.mysql_esta_activo():
            self.toggle_mysql()
            arranco_ahora = True

        perfil = self.config_data["perfiles_mysql"][self.combo_perfil.get()]
        cmd = [self.config_data["mysql_exe"], "-u", perfil["user"], "--table", "-e", query]
        if perfil["pass"]:
            cmd.insert(3, f"-p{perfil['pass']}")

        def tarea_sql():
            if arranco_ahora:
                time.sleep(2)
            res = subprocess.run(cmd, capture_output=True, text=True, creationflags=NO_WINDOW)
            salida = res.stdout if res.returncode == 0 else f"ERROR SQL:\n{res.stderr}"
            self.after(0, lambda: self._mostrar_en_caja(self.out_sql, salida.strip() or "Consulta ejecutada correctamente."))

        threading.Thread(target=tarea_sql, daemon=True).start()

    def ejecutar_artisan(self, subcomando):
        cmd = [self.config_data["php_exe"], "artisan"] + subcomando.split()
        self.ejecutar_comando_async(cmd, self.out_laravel)

    def ejecutar_git(self, args):
        self.ejecutar_comando_async(["git"] + args, self.out_git)

    def git_inicializar(self):
        self.ejecutar_git(["init"])
        self.after(600, self.analizar_entorno_proyecto)

    def ejecutar_git_personalizado(self):
        texto = self.entry_git_cmd.get().strip()
        if not texto:
            return
        if texto.lower().startswith("git "):
            texto = texto[4:].strip()
        self.entry_git_cmd.delete(0, "end")
        self.ejecutar_git(texto.split())
        self.after(800, self.analizar_entorno_proyecto)

    def git_commit_push(self):
        msg = self.entry_commit.get().strip()
        if not msg:
            messagebox.showwarning("Git", "Escribe un mensaje para el commit.")
            return
        self.entry_commit.delete(0, "end")
        self._mostrar_en_caja(self.out_git, "⏳ Guardando cambios y subiendo a GitHub...\n")

        def flujo():
            ruta = self.ruta_proyecto()
            subprocess.run(["git", "add", "."], cwd=ruta, stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)

            c = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=ruta, capture_output=True, text=True,
                stdin=subprocess.DEVNULL, creationflags=NO_WINDOW
            )
            if c.returncode != 0:
                error_commit = f"{c.stdout}\n{c.stderr}".strip()
                self.after(0, lambda: self._mostrar_en_caja(self.out_git, f"✖ Error en Commit:\n{error_commit}"))
                return

            rama_res = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=ruta, capture_output=True, text=True,
                stdin=subprocess.DEVNULL, creationflags=NO_WINDOW
            )
            rama = rama_res.stdout.strip() or "main"

            p = subprocess.run(
                ["git", "push", "-u", "origin", rama],
                cwd=ruta, capture_output=True, text=True,
                stdin=subprocess.DEVNULL, creationflags=NO_WINDOW
            )
            salida_total = f"✔ Commit realizado:\n{c.stdout}\n\n{p.stdout}\n{p.stderr}".strip()
            self.after(0, lambda: self._mostrar_en_caja(self.out_git, salida_total))
            self.after(0, self.analizar_entorno_proyecto)

        threading.Thread(target=flujo, daemon=True).start()

    def ejecutar_docker(self, args):
        self.ejecutar_comando_async(["docker"] + args, self.out_docker)

    def abrir_vscode(self):
        code_bin = self.resolver_binario("code")
        subprocess.Popen([code_bin, "."], cwd=self.ruta_proyecto(), creationflags=NO_WINDOW)

    def al_cerrar(self):
        for clave in ["php", "vite", "queue"]:
            if self.procesos[clave]:
                self.procesos[clave].terminate()
        # Solo apaga MySQL al cerrar si el propio programa lo encendió
        if self.procesos["mysql"] is not None:
            self.toggle_mysql()
        self.destroy()


if __name__ == "__main__":
    app = DevStudioApp()
    app.mainloop()