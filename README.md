# Capybara Launcher Latam - Séquito del Terror Edition

Este repositorio contiene el código fuente oficial del **Launcher Personalizado** y el **Asistente de Instalación Gráfica** diseñados a medida para la comunidad y clan **El Séquito del Terror** (https://sequitodelterror.netlify.app/) que juega en el servidor **Capycraft.io** (https://capycraft.io/).

---

## 📥 DESCARGA DIRECTA DEL INSTALADOR (1-CLIC)

Para jugar de inmediato, haz clic en el siguiente enlace para descargar el instalador oficial autocontenido:

👉 **[DESCARGAR INSTALADOR OFICIAL (71.2 MB)](https://github.com/DarckRovert/Capybara_launcher_latam/raw/main/Instalador_Sequito_WoW.exe)**

*(Una vez descargado, ejecútalo, selecciona la carpeta y comenzará a preparar todo de forma 100% automatizada).*

---

## 🎨 Identidad Visual y Experiencia Premium

El launcher y el instalador han sido diseñados bajo una estética **Gótica y Classic+**, incorporando:
*   **Splash Art Oficial:** Un fondo personalizado de alta calidad en 16:9 que evoca el misterio y el terror.
*   **Emblema del Clan:** Logotipo representativo (calavera dorada con filigranas) embebido y utilizado como el icono del sistema operativo (`logo.ico`) en los accesos directos generados de Windows.
*   **Tema Oscuro Premium:** Integración fluida con CustomTkinter para ofrecer barras de título nativas del sistema operativo en gris carbón/carbono en Windows.

---

## 🚀 Características Principales

### 📦 1. Asistente de Instalación Gráfica (`installer.py`)
*   **Fácil Despliegue:** Asistente dinámico que copia los archivos del launcher portátil, los recursos góticos y la configuración inicial de realmlist.
*   **Accesos Directos Automáticos:** Utiliza la API nativa de Windows (`win32com.client`) para generar accesos directos de inmediato en el **Escritorio** y en el **Menú Inicio**, enlazándolos con el icono de la calavera oficial (`logo.ico`).
*   **Detección de Juego:** Al finalizar, identifica de forma inteligente si la carpeta ya cuenta con los archivos del juego (como `WoW.exe`) o si requiere descargar el cliente completo, mostrando un mensaje informativo personalizado.

### ⚡ 2. Motor de Descarga en 1-Clic del Juego Completo (`launcher.py`)
*   **Detección de Archivos:** Si el launcher se ejecuta y no detecta el archivo `WoW.exe`, el botón principal cambia dinámicamente a **"DESCARGAR JUEGO"** (en color naranja medieval) e informa al usuario sobre el estado.
*   **Descargador Multihilo Asíncrono:** Utiliza la librería `requests` para descargar de forma fluida el cliente completo de WoW Classic 1.12.1 en segundo plano desde un mirror optimizado y permanente de **Internet Archive (Archive.org)**.
*   **Telemetría de Descarga:** Reporta en tiempo real el porcentaje completado en la barra de progreso, la velocidad en **MB/s** y el tiempo estimado restante (**ETA**).
*   **Descompresión y Despliegue Inteligente:** Al descargar el archivo `.zip`, el motor lo extrae y detecta automáticamente si los archivos de juego están aninados dentro de una subcarpeta. De ser así, mueve los archivos core a la raíz y limpia las subcarpetas vacías.
*   **Activación Inmediata:** Al completarse la instalación, auto-escribe el realmlist y el botón cambia de forma fluida al color carmesí de **"JUGAR"**.

### 🔌 3. Selector de Idiomas Nativo (Locale Switcher)
*   **Lectura / Escritura en WTF:** Lee de forma nativa la configuración de tu cliente en `WTF/Config.wtf` y te permite cambiar de inmediato entre **Español (esES)**, **Inglés (enUS)** o **Chino (zhCN)** sin tocar los archivos de texto.
*   **Asistente pfUI:** Si seleccionas Español, el launcher te recordará activar los addons de traducción.

### 🔌 4. Gestor de Addons Oficiales del Clan
*   ** pfUI Integrado:** Descarga e instala en un solo clic el reemplazo completo de interfaz pfUI desde repositorios oficiales de GitHub, configurando las rutas y descompresión de forma automática en la carpeta `Interface/AddOns/`.
*   **ShaguTweaks:** Gestor ligero de calidad de vida Classic+ para mantener la estética clásica.

### 🛠️ 5. Mantenimiento del Juego
*   **Limpiar Caché (WDB):** Elimina con un solo clic la carpeta de base de datos local para corregir bugs visuales y problemas de carga de items en el juego.
*   **Reparación de Realmlist:** Escribe y bloquea el realmlist apuntando a `SET realmList "apac.capycraft.io"` en caso de que otros servidores lo corrompan.
*   **Verificación de Integridad:** Compara y comprueba de forma rápida la existencia de los archivos DLL y de datos (`Data/common.MPQ`) necesarios para arrancar el cliente de WoW.

### 📶 6. Latencia de Servidor (Ping en Vivo)
*   **TCP Ping:** Hilo asíncrono que mide la latencia de red al puerto web/de juego del host `apac.capycraft.io` cada 15 segundos, reportando si está `● ONLINE` o `● OFFLINE` directamente en la UI.

---

## 🛠️ Requisitos de Desarrollo

Para ejecutar y modificar este proyecto localmente, necesitas tener instalado Python 3.10+ en Windows y las siguientes librerías:

```bash
pip install customtkinter Pillow requests pypresence pywin32 pyinstaller
```

---

## 🏗️ Instrucciones de Compilación y Distribución

Tanto el launcher como el instalador son empaquetados como ejecutables portátiles independientes (`.exe`) sin dependencias externas usando **PyInstaller**:

### 🛡️ Compilar el Launcher Oficial:
Ejecuta el siguiente comando en PowerShell desde la carpeta raíz del código fuente para compilar el Launcher (`SequitoLauncher.exe`):

```powershell
pyinstaller --noconsole --onefile --icon=assets/logo.ico --add-data 'assets;assets' --add-data 'config.json;.' --name 'SequitoLauncher' launcher.py
```
*Nota: Copia el ejecutable generado en `dist/` y colócalo en la carpeta `launcher-src/` para que el instalador pueda embeberlo.*

### 📦 Compilar el Instalador de Escritorio:
Ejecuta el siguiente comando para generar el instalador autocontenido (`Instalador_Sequito_WoW.exe`) que incluye el launcher y los recursos:

```powershell
pyinstaller --noconsole --onefile --icon=assets/logo.ico --add-data 'assets;assets' --add-data 'config.json;.' --add-data 'SequitoLauncher.exe;.' --name 'Instalador_Sequito_WoW' installer.py
```
*Nota: El archivo Instalador_Sequito_WoW.exe resultante en dist/ es el único archivo que necesitas compartir con tus usuarios. Mide ~74.9MB y maneja todo de forma completamente autónoma.*

---

## 👥 Créditos e Integración

*   **Página Oficial de Capycraft:** https://capycraft.io/
*   **Sitio del Clan El Séquito del Terror:** https://sequitodelterror.netlify.app/
*   **Desarrollo Técnico y Estabilidad:** Google DeepMind Advanced Agentic Coding Team.
