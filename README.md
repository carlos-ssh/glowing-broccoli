# glowing-broccoli · Maschine MK1 + rekordbox

Dos cosas en un repo:

1. **`rekordbox-mapping/`**: mapeo MIDI del MASCHINE MK1 para rekordbox 7 (CSV, documentación y plantilla de Controller Editor).
2. **`driver/`**: primeros pasos de un driver en espacio de usuario para el MK1 en macOS Sequoia (Intel y Apple Silicon), sin kext.

> **Para retomar el proyecto, lee [`PLAN.md`](PLAN.md)**: estado, datos técnicos, pasos en orden y cómo continuar.

## Estado

| Parte | Estado |
|---|---|
| Mapeo rekordbox (CSV + plantilla) | Generado y verificado internamente. Falta probarlo con el hardware. |
| `probe` (lista descriptores USB) | Funciona. Compila universal. |
| `mk1read` (lee eventos del MK1) | Compila. Falta ejecutarlo con el kext de NI descargado. |
| `mk1midi` (MK1 → puerto MIDI virtual) | Escrito y compilado. El puerto CoreMIDI está probado (`--selftest`). **La lectura del hardware no está probada**: falta ejecutarlo con el kext de NI descargado. |
| LEDs y pantallas | **Pendiente.** Protocolo no documentado. |
| Instalador `.pkg` | Se construye y su contenido está comprobado. **No se ha instalado ni probado en un Mac.** Sin firmar. |

## 1. Mapeo para rekordbox

Requisitos: Python 3, rekordbox 7, Controller Editor de NI.

### Regenerar los archivos
```bash
cd rekordbox-mapping
python3 generador.py          # escribe el CSV y el MAPA
python3 crear_plantilla.py    # escribe REKORDBOX.ncm
```
`generador.py` es la fuente única. Cambia ahí canales, notas o funciones y vuelve a ejecutar los dos scripts.

### Cargar la plantilla en Controller Editor
1. Cierra el software MASCHINE (no puede estar abierto a la vez).
2. Abre **Controller Editor** y elige tu MASCHINE (MK1).
3. En el panel Templates usa **Edit → Import** y elige `REKORDBOX.ncm`.
4. Comprueba que **Enable Pad Pages** esté activado.
5. Carga la plantilla en el Maschine y entra en modo MIDI con **SHIFT + CONTROL**.

### Importar el CSV en rekordbox
1. Abre rekordbox 7 en modo **PERFORMANCE**.
2. Pulsa el botón **MIDI** (arriba a la derecha).
3. Elige el dispositivo *Maschine Controller* (en macOS puede llamarse *Maschine Controller Virtual Input*).
4. Pulsa **IMPORT** y elige `Maschine_MK1_rekordbox.midi.csv`.
5. Cierra la ventana MIDI: rekordbox guarda el mapeo.

rekordbox guarda sus mapeos en `~/Library/Application Support/Pioneer/rekordbox6/MidiMappings/`. Importar sobrescribe el del Maschine, así que copia antes ese archivo si quieres conservarlo.

### Prueba rápida
Con LEARN apagado: **SCENE** = Play/Pause del Deck 1, **PATTERN** = Deck 2. **STEP** abre la Browse View. **◄ / ►** del transporte suben y bajan en la lista, **LOOP** entra en la carpeta, **BROWSE** / **SAMPLING** cargan en el Deck 1 / Deck 2.

### Limitaciones conocidas
- Controller Editor no tiene modo **Relative** para los knobs del MK1, así que Browse, Zoom y loops no usan knobs. La navegación va con botones.
- Las filas marcadas con ⚠️ en el MAPA están deducidas por patrón y no verificadas con los archivos oficiales de Pioneer. Si rekordbox rechaza el import, bórralas del CSV.
- Las pantallas del Maschine no pueden mostrar datos de rekordbox. Los LEDs sí reaccionan si activas *LED On = Remote/MIDI* en Controller Editor.

## 2. Driver para macOS Sequoia (en desarrollo)

El driver de NI para el MK1 es un kext de 2014 que no sirve en Sequoia. La idea es un programa en espacio de usuario que reclame el dispositivo por USB y lo publique como puerto MIDI virtual (CoreMIDI), utilizable desde Ableton, rekordbox y cualquier otro software.

Dispositivo: USB `17CC:0808`, interfaz de clase vendor con endpoints bulk `0x01`/`0x81` y, en la configuración alternativa 1, también `0x84` (pads) y `0x08`. El protocolo "caiaq" está documentado en el driver de Linux (`sound/usb/caiaq`).

Requisitos: macOS, herramientas de línea de comandos de Xcode (`xcode-select --install`).

### Compilar (binario universal Intel + Apple Silicon)
```bash
cd driver
clang -arch x86_64 -arch arm64 -o probe probe.c -framework IOKit -framework CoreFoundation
clang -arch x86_64 -arch arm64 -Wno-deprecated-declarations -o mk1read mk1read.c \
      -framework IOKit -framework CoreFoundation
clang -arch x86_64 -arch arm64 -Wno-deprecated-declarations -o mk1midi mk1midi.c \
      -framework IOKit -framework CoreFoundation -framework CoreMIDI
```

### `probe`: ver los descriptores USB
No abre el dispositivo y no necesita descargar nada.
```bash
./probe
```
Debe mostrar una interfaz con endpoints `0x01`, `0x81` y, en alt 1, `0x84` y `0x08`.

### `mk1read`: leer eventos del MK1
El kext de NI reclama el dispositivo, así que hay que descargarlo antes. Solo en un Mac donde esté instalado el driver de NI:
```bash
sudo kextunload -b com.caiaq.driver.NIUSBMaschineControllerDriver
killall NIHardwareAgent        # puede relanzarse solo; repite si hace falta
./mk1read                      # 30 s: toca pads, botones y knobs
```
Si `kextunload` falla, cierra MASCHINE, Controller Editor y rekordbox.

Si `mk1read` dice `USBInterfaceOpen fallo 0xE00002C5`, algo sigue reclamando el dispositivo.

Para recuperar el driver de NI: reinicia el Mac, o ejecuta
```bash
sudo kextload /Library/Extensions/NIUSBMaschineController.kext
```

### `mk1midi`: el MK1 como controlador MIDI (fase 2)
Publica un puerto MIDI virtual llamado **Maschine MK1** que aparece en Ableton, rekordbox y cualquier software MIDI.
```bash
./mk1midi --selftest   # no necesita hardware: comprueba que CoreMIDI funciona
./mk1midi --debug      # con el MK1 (kext de NI descargado): imprime cada evento
./mk1midi              # modo normal
```
Mapeo MIDI por defecto:

| Control | Mensaje |
|---|---|
| 16 pads | Canal 1, notas 36–51, velocity según la presión |
| Botones (42) | Canal 2, nota = número de bit (0–41) |
| Knobs K1–K8 | Canal 1, CC 20–27, **Relative** (1 = derecha, 127 = izquierda) |
| VOLUME, TEMPO, SWING | Canal 1, CC 28–30, Relative |

Los knobs del MK1 son potenciómetros sin fin de dos fases, por eso aquí sí se puede emitir Relative real. Las funciones de browse, zoom y loop que en Controller Editor no podían ir en knobs sí pueden usarlos con este driver.

**Sin verificar con hardware:** el orden de los bits de botones, el orden físico de los knobs (K1 a K8), el número de cada pad y los umbrales de presión están tomados del driver de Linux. Ejecuta `./mk1midi --debug` y comprueba que cada control produce el evento esperado. Los nombres de botón con `?` en el código son dudosos (por ejemplo F1/F2 y PAGE ◄ ►).

### Qué falta
1. **Validar `mk1midi` con el MK1 real** y corregir los órdenes que no coincidan.
2. **Mapeo de rekordbox en el driver:** páginas de pads y de knobs (hoy las aplica Controller Editor), usando las tablas de `generador.py`.
3. **LEDs:** capturar el tráfico del driver de NI para conocer el formato.
4. **Pantallas:** protocolo no documentado (ingeniería inversa).
5. **Probar el `.pkg`** en un Mac con Sequoia, y añadir un archivo de mapeo editable.

## 3. Instalador `.pkg`

```bash
cd packaging
./build-pkg.sh            # genera build/MaschineMK1-0.1.0.pkg
./build-pkg.sh 0.2.0      # otra versión
SIGN_ID="Developer ID Installer: Nombre (TEAMID)" ./build-pkg.sh   # firmado
```
Instala `mk1midi` (binario universal) en `/usr/local/libexec/maschine-mk1/` y un LaunchAgent en `/Library/LaunchAgents/` que lo arranca al iniciar sesión y lo reintenta cada 10 s hasta que el MK1 esté conectado.

- **Sin firmar:** el paquete no está firmado ni notarizado (hace falta una cuenta de Apple Developer). Gatekeeper pedirá abrirlo con clic derecho → Abrir, o desde Ajustes del Sistema → Privacidad y seguridad.
- **Conflicto con NI:** si el Mac tiene el driver de NI instalado, el kext reclama el dispositivo y `mk1midi` no podrá abrirlo. Hay que quitar ese driver.
- **Registro de errores:** `/tmp/maschine-mk1.log`.

Desinstalar:
```bash
sudo /usr/local/libexec/maschine-mk1/uninstall.sh
```

## Licencia
MIT. El código del driver sigue el formato del protocolo documentado en el driver de Linux (GPL); `probe.c` y `mk1read.c` están escritos desde cero.
