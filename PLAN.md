# Plan para continuar · Maschine MK1 en macOS Sequoia

Documento para retomar el proyecto más adelante, sin depender de la conversación donde se empezó. Todo lo que aquí figura como "verificado" se comprobó en la sesión de trabajo; lo demás está marcado como **sin verificar**.

## 1. Objetivo

Usar el **MASCHINE MK1** como controlador MIDI en **macOS Sequoia (15)**, en Mac **Intel y Apple Silicon**, con **cualquier software** (Ableton Live, rekordbox, etc.), **sin el driver de NI**, que es un kext de 2014 y no funciona en Sequoia.

Dos líneas de trabajo:

1. **Mapeo para rekordbox** con el driver de NI (Controller Editor): hecho, falta probarlo con el hardware.
2. **Driver propio** en espacio de usuario que publique un puerto MIDI virtual: escrito, **falta probarlo con el hardware**.

## 2. Estado actual

| Pieza | Dónde | Estado |
|---|---|---|
| Generador del CSV, MAPA y plantilla | `rekordbox-mapping/` | Hecho. Verificado internamente (códigos sin colisiones, plantilla coherente con el CSV). Sin probar en rekordbox ni en Controller Editor con el hardware. |
| Sonda USB | `driver/probe.c` | Funciona. |
| Lector de eventos | `driver/mk1read.c` | Compila. Probado: llega a abrir el dispositivo y falla con `0xE00002C5` porque el kext de NI lo reclama. |
| MK1 → MIDI | `driver/mk1midi.c` | Compila universal. `--selftest` OK (CoreMIDI). **Lectura del hardware sin probar.** |
| Instalador | `packaging/` | Se construye; contenido inspeccionado. **No instalado ni probado.** Sin firmar. |
| LEDs | — | No hecho. Protocolo desconocido. |
| Pantallas | — | No hecho. Protocolo desconocido. |

## 3. Datos técnicos de referencia

### Dispositivo
- USB `17CC:0808`, "Maschine Controller", versión de dispositivo USB `0.11`.
- Clase de dispositivo `255` (vendor). **No es HID.** Una sola configuración y una sola interfaz (interfaz 0).
- Alt 0: endpoints bulk `0x01` (OUT) y `0x81` (IN), 512 bytes.
- **Alt 1** (necesaria): además `0x84` (IN, bulk, 512) y `0x08` (OUT, bulk, 512). Verificado con `probe`.
- Driver de NI: `/Library/Extensions/NIUSBMaschineController.kext`, bundle id `com.caiaq.driver.NIUSBMaschineControllerDriver`, versión 2.8.0. Instalador original en `Descargas/Maschine_Controller_280_Mac_p.dmg`.
- El mapeo de las plantillas lo aplica el software de NI en el Mac (`NIHardwareAgent`), no el dispositivo.

### Protocolo "caiaq" (de `sound/usb/caiaq` del kernel de Linux; **sin verificar con este hardware**)
Archivos fuente: `https://raw.githubusercontent.com/torvalds/linux/master/sound/usb/caiaq/{input.c,device.c,device.h,midi.c}`. Licencia GPL: se usó solo como documentación del formato.

- Comandos por EP1 (primer byte = comando): `0x01` GET_DEVICE_INFO, `0x02` READ_ERP, `0x03` READ_ANALOG, `0x04` READ_IO, `0x05` WRITE_IO, `0x06` MIDI_READ, `0x07` MIDI_WRITE, `0x09` AUDIO_PARAMS, `0x0B` AUTO_MSG (args: digital, analog, erp), `0x0C` DIMM_LEDS.
- Tras `SetAlternateInterface(1)` se envía `GET_DEVICE_INFO`; Linux usa `AUTO_MSG`. Para el MK1 Linux **no** muestra un `AUTO_MSG` explícito: puede que el MK1 emita eventos sin él. `mk1midi` manda `{1, 10, 10}`; si molesta o no hace falta, quitarlo.
- **Botones:** `READ_IO`, bitmap, 42 bits. Orden en `mk1midi.c` (`BTN_NAME`), copiado de `keycode_maschine`.
- **Knobs:** `READ_ERP`, 22 bytes; 11 knobs sin fin de dos fases `(a, b)` → posición 0–999 con `decode_erp`. Pares en `ERP_AB`.
- **Pads:** EP4 (`0x84`), 16 valores `u16` LE: bits 15–12 id del pad, 11–0 presión.
- LEDs y pantallas: **no documentados en Linux**.

### Mapeo MIDI por defecto de `mk1midi` (genérico)
Pads canal 1 notas 36–51 · botones canal 2 nota = nº de bit · knobs K1–K8 canal 1 CC 20–27 y VOLUME/TEMPO/SWING CC 28–30, todos **Relative** (1 = +, 127 = −).

### rekordbox
- Formato del CSV: 15 columnas, ASCII, CRLF (igual que los oficiales). Los mapeos oficiales están en `/Applications/rekordbox 7/rekordbox.app/Contents/Resources/MidiMappings/`.
- Funciones oficiales útiles encontradas ahí: `BrowseUp`, `BrowseDown`, `Forward`, `ForwardAndLoad`, `Back`, `LoopHalf`, `LoopDouble`, `LoopIn`, `LoopOut`, `ReloopExit`, `AutoLoop`, `Slicer`, `SlicerLoop`, `PADn_Slicer`, `PADn_SlicerLoop`, `TrackPrev`, `TrackNext`, `JogSearch`, `NeedleSearch`.
- rekordbox guarda sus mapeos en `~/Library/Application Support/Pioneer/rekordbox6/MidiMappings/`.

### Controller Editor
- Las plantillas del MK1 son XML (`.ncm`). Los knobs del MK1 **no tienen modo Relative** en el Inspector (por eso Browse, Zoom y loops no van en knobs en ese mapeo).
- Plantillas de ejemplo de NI: `/Library/Application Support/Native Instruments/Controller Editor/Templates/`.
- Manual (PDF) en `/Applications/Native Instruments/Controller Editor/Documentation/`.

## 4. Pasos, en orden

### Fase A · Validar `mk1midi` con el hardware  ← **siguiente paso**
Hay que hacerlo en un Mac con el driver de NI instalado (como este), o en uno sin él.

1. Compilar:
   ```bash
   cd driver
   clang -arch x86_64 -arch arm64 -Wno-deprecated-declarations -o mk1midi mk1midi.c \
         -framework IOKit -framework CoreFoundation -framework CoreMIDI
   ```
2. Si el kext de NI está cargado, descargarlo (necesita `sudo`; cierra antes MASCHINE, Controller Editor y rekordbox):
   ```bash
   sudo kextunload -b com.caiaq.driver.NIUSBMaschineControllerDriver
   killall NIHardwareAgent        # puede relanzarse solo; repetir si hace falta
   ```
3. Ejecutar `./mk1midi --debug` y tocar **cada control**, uno por uno.
4. Rellenar la tabla de comprobación (abajo) y corregir en `mk1midi.c`:
   - `BTN_NAME` / orden de bits de los botones.
   - `ERP_AB` / orden de los knobs.
   - Número de cada pad (el id que llega puede no coincidir con la posición física).
   - `PAD_ON`, `PAD_OFF` y el cálculo de velocity.
   - `TICK` (sensibilidad de los knobs relativos).
5. Comprobar el MIDI con un monitor (por ejemplo la app *MIDI Monitor*, o Ableton con el puerto **Maschine MK1** activado en Preferencias → Link, Tempo & MIDI).

Posibles resultados y qué hacer:
- `USBInterfaceOpen fallo 0xE00002C5`: algo sigue reclamando el dispositivo (kext o agente).
- No llega ningún evento: probar sin el `AUTO_MSG`, o con otros valores `{digital, analog, erp}`; revisar si hace falta enviar algo más tras `GET_DEVICE_INFO`.
- Llegan botones pero no pads (o al revés): revisar que `SetAlternateInterface(1)` devuelva `0` y que existan las pipes de `0x84`.

**Tabla de comprobación** (anotar lo que imprime `--debug`):

| Control | Evento esperado | Resultado |
|---|---|---|
| 16 pads (uno por uno) | pad 0–15 en orden físico | |
| 42 botones | nombre correcto de `BTN_NAME` | |
| K1–K8 | `knob 0`–`7` de izquierda a derecha | |
| VOLUME / TEMPO / SWING | `knob 8` / `9` / `10` | |
| Sentido de giro | `+` a la derecha | |
| Pad con poca/mucha presión | velocity coherente | |

**Criterio de éxito:** cada control produce el mensaje MIDI correcto y el puerto aparece en Ableton y en rekordbox.

### Fase B · Capa de mapeo configurable
Hoy el mapeo está fijo en el código.

1. Definir un archivo de configuración (propuesta: JSON en `~/Library/Application Support/MaschineMK1/mapping.json`).
2. Permitir por control: tipo (nota/CC), canal, número, modo (absoluto/relativo), modo del botón (gate/toggle).
3. Implementar **páginas** en el driver (hoy las aplica Controller Editor): 8 páginas de pads (GROUP A–H) y páginas de knobs, con los botones GROUP y PAGE consumidos por el driver. Tomar las tablas de `rekordbox-mapping/generador.py` (`PAD_PAGES`, `KNOB_PAGES`, `GLOBAL_BUTTONS`) y exportarlas a JSON desde ahí, para tener una sola fuente de verdad.
4. Recarga en caliente del archivo de configuración.
5. Perfiles: uno genérico (el actual) y uno "rekordbox" generado desde `generador.py`.

**Criterio de éxito:** con el perfil rekordbox, el Maschine hace lo mismo que con la plantilla de Controller Editor, sin NI instalado.

### Fase C · LEDs
Los LEDs de pads y botones son necesarios para el feedback de rekordbox.

1. Capturar el tráfico USB del driver de NI mientras se encienden y apagan LEDs. Opciones: Wireshark o `tcpdump` sobre la interfaz USB de macOS (`XHC20`; el método exacto en Monterey **está sin verificar**), o desensamblar `NIUSBMaschineController.kext/Contents/MacOS/NIUSBMaschineController`.
2. Identificar qué comando y qué endpoint (EP1 con `WRITE_IO` / `DIMM_LEDS`, o EP8) controla cada LED y el brillo.
3. Implementar un destino MIDI virtual ("Maschine MK1 LEDs") para que rekordbox/Ableton envíen notas/CC y se enciendan los LEDs.

### Fase D · Pantallas (opcional)
1. Capturar el tráfico hacia el endpoint `0x08`.
2. Identificar el formato de imagen (tamaño, profundidad, orden de píxeles) de las dos pantallas.
3. Implementar texto y barras de valor (por ejemplo el valor del knob y el nombre de la función).

Nota: rekordbox **no envía** datos de pistas por MIDI, así que las pantallas solo mostrarían lo que genere el driver (nombres de función y valores), no títulos ni BPM.

### Fase E · Robustez del driver
- **Hot-plug:** hoy `mk1midi` sale si no encuentra el MK1 y el LaunchAgent lo reintenta cada 10 s. Sustituir por `IOServiceAddMatchingNotification` para detectar conexión y desconexión.
- Cierre limpio al recibir SIGTERM (soltar la interfaz).
- Recuperación tras suspensión del Mac y tras reconectar.
- Registro de eventos con niveles, en lugar de `/tmp/maschine-mk1.log`.
- Comprobar permisos/privacidad de USB en Sequoia con el programa instalado como LaunchAgent (**sin verificar**).

### Fase F · Instalador y distribución
1. Probar `packaging/build-pkg.sh` e instalar el `.pkg` en el Mac con **Sequoia Intel** y en uno con **Apple Silicon** (**no probado en ninguno**).
2. Comprobar que el LaunchAgent arranca, que el puerto aparece y que el desinstalador limpia todo.
3. Para distribuir a otras personas, firmar y notarizar (requiere cuenta de Apple Developer):
   - Firmar el binario: `codesign --options runtime --timestamp --sign "Developer ID Application: …" mk1midi`.
   - Firmar el paquete: `SIGN_ID="Developer ID Installer: …" ./build-pkg.sh`.
   - Notarizar: `xcrun notarytool submit MaschineMK1-x.y.z.pkg --wait …` y luego `xcrun stapler staple`.
4. Publicar una release en GitHub con el `.pkg`.
5. Revisar la licencia (ver riesgos).

## 5. Mapeo de rekordbox: pendientes

- **Probar el mapeo con el hardware** (Controller Editor + import del CSV): Play/Cue, pads, FX, browse con ◄ ► y LOOP.
- **Knobs de loop:** quedaron sin función. Con el driver propio se pueden recuperar como Relative; con Controller Editor hay que usar botones (`LoopHalf`, `LoopDouble`).
- **Slicer:** pendiente de decidir si usar los grupos E y F para `PADn_Slicer` en lugar de Pad FX 2 (que es una función deducida). Falta aclarar si "slice para sampleo" significa Slicer en los decks o cortar pistas para meterlas en el sampler (rekordbox no exporta trozos al sampler por MIDI).
- **Búsqueda rápida / `TrackPrev` / `TrackNext`:** no incluidas.
- **Filas ⚠️ del MAPA:** deducidas por patrón, no verificadas con archivos oficiales: `FX2-*`, `PADn_PadFx2`, sampler 9–16. Si rekordbox las rechaza, borrarlas del CSV.
- Los códigos MIDI de `BrowseUp`, `BrowseDown` y `Forward` los eligió el generador; los **nombres** de función sí son oficiales.

## 6. Riesgos y limitaciones conocidas

- **Pantallas y LEDs:** dependen de ingeniería inversa; pueden no ser viables o llevar tiempo.
- **Órdenes de bits, knobs y pads:** vienen del driver de Linux; pueden no coincidir con tu unidad.
- **Licencia:** el repo es MIT. `probe.c`, `mk1read.c` y `mk1midi.c` están escritos desde cero y solo siguen el formato del protocolo documentado en el driver de Linux (GPL), pero conviene revisarlo antes de distribuir. No copiar código de ese driver sin cambiar la licencia.
- **Firma y notarización:** sin ellas, Gatekeeper bloquea el `.pkg` en otros Macs.
- **Conflicto con NI:** no pueden convivir el driver de NI y `mk1midi` sobre el mismo dispositivo.
- **Comparar con el driver original:** el kext de NI es de 2014 y, según lo investigado, no funciona en Sequoia; este Mac (macOS 12) es donde se puede capturar el tráfico del driver de NI para LEDs y pantallas. Conviene conservarlo tal cual hasta terminar esas fases.

## 7. Cómo retomar

Archivos:
```
README.md                 cómo se usa cada pieza
PLAN.md                   este documento
rekordbox-mapping/        generador.py (fuente única), CSV, MAPA, plantilla .ncm
driver/                   probe.c, mk1read.c, mk1midi.c
packaging/                build-pkg.sh, LaunchAgent, postinstall, uninstall.sh
```

Para continuar con Claude Code desde una carpeta nueva:
```bash
gh repo clone carlos-ssh/glowing-broccoli
cd glowing-broccoli
claude
```
y pedir, por ejemplo: *"Lee README.md y PLAN.md y continúa con la Fase A. El kext de NI ya está descargado."*

Comandos útiles:
```bash
kextstat | grep -i caiaq                                 # ¿está cargado el kext de NI?
system_profiler SPUSBDataType | grep -A8 "Maschine"      # ¿ve macOS el MK1?
./probe                                                   # descriptores USB
./mk1midi --selftest                                      # prueba de CoreMIDI sin hardware
./mk1midi --debug                                         # eventos del MK1
sudo kextload /Library/Extensions/NIUSBMaschineController.kext   # restaurar el driver de NI
```

## 8. Decisiones ya tomadas

- Controlador objetivo: **MASCHINE MK1**.
- Destino: macOS **Sequoia**, **Intel y Apple Silicon** (binario universal).
- Alcance: **reemplazar el driver de NI**, con el MK1 usable como MIDI en cualquier software.
- Tecnología: **C**, IOKit (USB en espacio de usuario) y CoreMIDI. Sin kext ni dependencias externas (no se usa libusb).
- Instalador: **`.pkg`** con `pkgbuild` y `productbuild`.
