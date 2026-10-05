# glowing-broccoli · Maschine MK1 + rekordbox

Dos cosas en un repo:

1. **`rekordbox-mapping/`**: mapeo MIDI del MASCHINE MK1 para rekordbox 7 (CSV, documentación y plantilla de Controller Editor).
2. **`driver/`**: primeros pasos de un driver en espacio de usuario para el MK1 en macOS Sequoia (Intel y Apple Silicon), sin kext.

## Estado

| Parte | Estado |
|---|---|
| Mapeo rekordbox (CSV + plantilla) | Generado y verificado internamente. Falta probarlo con el hardware. |
| `probe` (lista descriptores USB) | Funciona. Compila universal. |
| `mk1read` (lee eventos del MK1) | Compila. Falta ejecutarlo con el kext de NI descargado. |
| Traducción a MIDI (CoreMIDI) | **Pendiente (fase 2).** |
| LEDs y pantallas | **Pendiente.** Protocolo no documentado. |
| Instalador `.pkg` | **Pendiente.** Se hará cuando funcione la fase 2. |

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

### Qué falta
1. **Fase 2:** traducir pads, botones y knobs a MIDI con CoreMIDI. Los knobs son potenciómetros sin fin de dos fases, así que el driver puede emitir Relative real.
2. **LEDs:** capturar el tráfico del driver de NI para conocer el formato.
3. **Pantallas:** protocolo no documentado (ingeniería inversa).
4. **Instalador `.pkg`:** programa universal, LaunchAgent, puerto MIDI virtual y archivo de mapeo editable, con `pkgbuild` y `productbuild`. Sin cuenta de Apple Developer el paquete no está firmado ni notarizado: Gatekeeper pedirá abrirlo con clic derecho → Abrir.

## Licencia
MIT. El código del driver sigue el formato del protocolo documentado en el driver de Linux (GPL); `probe.c` y `mk1read.c` están escritos desde cero.
