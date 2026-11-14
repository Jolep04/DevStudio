# DevStudio

**DevStudio** es un gestor de entornos de desarrollo local moderno, ligero y portable para **Windows**, diseñado como una alternativa nativa y sin dependencias para reemplazar a **XAMPP**.

Construido con **Python** y **CustomTkinter**, permite administrar servidores PHP, bases de datos MySQL 8.0, proyectos de Laravel, Composer, Vite/NPM, Git y Docker desde una única interfaz gráfica oscura y limpia, sin necesidad de mantener múltiples ventanas de consola abiertas.

##  Características Principales

*  **Detección Inteligente de Entorno:** Identifica automáticamente si el proyecto seleccionado es **Laravel** o **PHP Nativo**, además de verificar la presencia de `composer.json`, el estado del repositorio **Git** (rama activa) y archivos de **Docker Compose**.

*  **Control de Servicios en Un Clic:**

  * **Servidor PHP:** Inicia o detiene el servidor integrado de PHP y abre el proyecto directamente en el navegador.

  * **MySQL 8.0:** Controla el servicio nativo de MySQL en Windows y monitorea su estado en tiempo real.

  * **Vite / NPM:** Ejecuta el servidor de desarrollo frontend (`npm run dev`) de forma integrada.

*  **Gestor de Base de Datos (SQL):** Soporte para múltiples perfiles de conexión MySQL (por ejemplo, `root` o usuarios dedicados para Laravel) configurables desde la interfaz.

*  **Asistente de Laravel y Composer:** Ejecuta comandos de `artisan`, migraciones, instalación de paquetes y gestión de dependencias sin tocar la terminal.

*  **Cliente Git Integrado:**

  * Inicialización de repositorios (`git init`), consulta de estado (`status`), historial de commits (`log`) y actualización (`pull`).

  * Flujo rápido de **Commit & Push** con un solo clic.

  * Consola integrada para ejecutar cualquier comando personalizado de Git.

*  **Soporte para Docker:** Administración rápida de contenedores y pilas definidas con Docker Compose.

*  **Asistente de Nuevos Proyectos y Configuración:** Crea proyectos desde cero, ábrelos directamente en **Visual Studio Code** y personaliza las rutas de tus binarios desde el modal de **Ajustes**.

##  Requisitos Previos

Para aprovechar todas las funcionalidades de **DevStudio**, asegúrate de contar en tu sistema Windows con las instalaciones nativas (añadidas al `PATH` del sistema o configuradas en **Ajustes**):

* **Sistema Operativo:** Windows 10 / 11

* **PHP:** Versión 8.1 o superior

* **MySQL:** Versión 8.0 (configurado como servicio de Windows)

* **Composer** y **Node.js / NPM** (opcional, para proyectos Laravel/Vite)

* **Git** (para control de versiones)

* **Docker Desktop** (opcional, para gestión de contenedores)

##  Instalación y Ejecución (Desde Código Fuente)

1. **Clona este repositorio:**

   ```
   git clone https://github.com/Jolep04/DevStudio.git
   cd DevStudio
   
   ```

2. **Instala la dependencia de interfaz gráfica:**

   ```
   pip install customtkinter
   
   ```

3. **Ejecuta la aplicación:**

   ```
   py DevStudio.py
   
   ```

##  Compilar Ejecutable Portable (`.exe`)

Si deseas generar el ejecutable independiente para abrirlo con doble clic o anclarlo a la barra de tareas sin mostrar consolas de fondo, instala **PyInstaller** y ejecuta:

```
pip install pyinstaller
py -m PyInstaller --noconsole --onefile --name "DevStudio" DevStudio.py

```

El archivo compilado se generará dentro de la carpeta `dist/DevStudio.exe`.

##  Configuración (`devstudio_config.json`)

Al iniciar por primera vez o guardar cambios en **Ajustes**, la aplicación genera un archivo local `devstudio_config.json` donde almacena tus rutas y perfiles de MySQL. Por seguridad, este archivo está excluido en `.gitignore` para evitar subir contraseñas locales al repositorio.

Ejemplo de estructura:

```
{
  "ruta_proyectos": "C:\\Users\\tu_usuario\\Documentos\\local",
  "perfiles_mysql": {
    "Local Root": {
      "host": "127.0.0.1",
      "port": 3306,
      "user": "root",
      "password": "tu_password_seguro"
    }
  }
}

```

##  Estructura del Proyecto

```
DevStudio/
├── DevStudio.py            # Código fuente principal e interfaz gráfica
├── .gitignore              # Exclusiones de compilación y credenciales locales
└── README.md               # Documentación del proyecto

```

##  Licencia

Este proyecto está bajo la Licencia **MIT**. Desarrollado por **Jolep04**.