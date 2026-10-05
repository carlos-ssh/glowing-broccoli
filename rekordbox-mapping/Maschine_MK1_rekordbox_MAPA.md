# MASCHINE MK1 → rekordbox · Mapa MIDI profesional (sampler · FX · performance)

Archivo de mapeo: `Maschine_MK1_rekordbox.midi.csv` (formato oficial de rekordbox, 15 columnas, importable desde el panel MIDI).  
Este documento explica **qué manda cada control del Maschine** (para configurarlo en Controller Editor) y **qué hace en rekordbox**.

> Leyenda de confianza por función: ✅ = nombre tomado tal cual de los mapeos oficiales de Pioneer (DDJ-FLX10 / DDJ-GRV6) · ⚠️ = deducido por patrón (funciona con alta probabilidad; si rekordbox no lo reconoce, borra esa fila del CSV).

## 1. Concepto

El MK1 en **modo MIDI** no tiene lógica condicional, así que cada *capa* se construye con lo que el hardware sí ofrece nativamente:

| Recurso del MK1 | Cómo se usa | Capas |
|---|---|---|
| **Pad Pages** (botones GROUP A–H) | 8 capas de 16 pads, cada una manda notas en un canal/rango distinto | A–H |
| **Knob Pages** (botones PAGE ◄ ►) | 4 páginas de 8 knobs + 8 botones de display | 1–4 |
| Botones globales (22) | Siempre activos, independientes de la página | — |
| Knob master SWING | Siempre activo (VOLUME y TEMPO sin asignar) | — |

Cada función de rekordbox recibe **un código MIDI único** (regla de rekordbox: un código = una función), por eso no dependemos del botón SHIFT de rekordbox: la capa la decide el Maschine.

Decks: la plantilla cubre **Deck 1 y Deck 2**; el CSV ya trae los códigos de Deck 3/4 (offsets 2,3 y canales de pads 12–15) por si un día haces una segunda plantilla a 4 decks.

### Chuleta del panel

```
MASCHINE MK1 · plantilla REKORDBOX

CONTROL = Back (biblioteca)     STEP = Browse View       B1..B8 (sobre displays) = botones de la PÁGINA DE KNOBS
BROWSE  = Load Deck 1           SAMPLING = Load Deck 2   K1..K8 (bajo displays)  = knobs de la PÁGINA DE KNOBS
◄ ►     = cambiar página de knobs (SHIFT+◄► = plantilla)
F1      = Preview track         F2 = Tag track

SWING = Sampler Volume      NOTE REPEAT = RELEASE FX (mantener)      VOLUME / TEMPO = sin asignar

GROUP A..H = CAPA DE PADS:
  A D1 HotCue+PadFX1   B D2 HotCue+PadFX1   C D1 Jump+Loop   D D2 Jump+Loop
  E D1 PadFX2+Borrar   F D2 PadFX2+Borrar   G Sampler PLAY   H Sampler STOP

SCENE = Play D1    PATTERN = Play D2    KEYBOARD = Cue D1     NAVIGATE = Cue D2
DUPLICATE = Sync D1  SELECT = Sync D2   SOLO = 4Beat Loop D1  MUTE = 4Beat Loop D2

LOOP = Forward (abrir carpeta)   ◄ = Browse Up   ► = Browse Down   GRID = FX1 -> Sampler (latch)
PLAY = FX1 ON/OFF      REC = FX2 ON/OFF      ERASE = Sampler Cue     SHIFT = reservado

PÁGINAS DE KNOBS: 1 FX1 + Color FX depth | 2 FX2 | 3 FX1 selección directa + Gain/EQ | 4 Color FX type + Quantize
```

## 2. Plan de canales MIDI

| Uso | Canal (Controller Editor, 1–16) | Status hex | Tipo |
|---|---|---|---|
| Deck 1 (botones / knobs de deck) | 1 | `90` / `B0` | Note / CC |
| Deck 2 | 2 | `91` / `B1` | Note / CC |
| Deck 3 / Deck 4 (reservado) | 3 / 4 | `92` `93` / `B2` `B3` | Note / CC |
| Beat FX 1 | 5 | `94` / `B4` | Note / CC |
| Beat FX 2 | 6 | `95` / `B5` | Note / CC |
| Global: browser, sampler, mixer, Color FX | 7 | `96` / `B6` | Note / CC |
| Pads Deck 1 · capa normal / capa "shift" (borrar, stop) | 8 / 9 | `97` / `98` | Note |
| Pads Deck 2 · normal / shift | 10 / 11 | `99` / `9A` | Note |
| Pads Deck 3 y 4 (reservado) | 12–15 | `9B`–`9E` | Note |

Rango de notas de los pads (igual que Pioneer): HOT CUE `00–0F` · PAD FX1 `10–1F` · BEAT JUMP `20–2F` · SAMPLER `30–3F` · KEYBOARD `40–4F` · PAD FX2 `50–5F` · BEAT LOOP `60–6F` · KEY SHIFT `70–7F`.

## 3. Capas de pads (GROUP A–H)

Numeración física del MK1: el pad **1 está abajo a la izquierda** y el **16 arriba a la derecha** (fila inferior 1-4, luego 5-8, 9-12 y arriba 13-16).

| GROUP | Capa | Pads 1–8 (dos filas inferiores) | Pads 9–16 (dos filas superiores) |
|---|---|---|---|
| **A** | Deck 1 | Hot Cue 1–8 | Pad FX 1 · slots 1–8 (momentáneo) |
| **B** | Deck 2 | Hot Cue 1–8 | Pad FX 1 · slots 1–8 |
| **C** | Deck 1 | Beat Jump ◄1 ►1 ◄2 ►2 ◄4 ►4 ◄8 ►8 | Beat Loop slots 1–8 |
| **D** | Deck 2 | Beat Jump | Beat Loop |
| **E** | Deck 1 | Pad FX 2 · slots 1–8 | **Borrar** Hot Cue 1–8 |
| **F** | Deck 2 | Pad FX 2 · slots 1–8 | Borrar Hot Cue 1–8 |
| **G** | Sampler | Slots 1–8 ▶ | Slots 9–16 ▶ (banco activo) |
| **H** | Sampler | Slots 1–8 ■ stop | Slots 9–16 ■ stop |

Los tamaños de Beat Jump / Beat Loop siguen el **rango activo** en el panel PAD de rekordbox (por defecto Beat Jump 1-2-4-8 beats y Beat Loop ¼ … 32 beats).

Los botones GROUP y PAGE no mandan MIDI (los consume Controller Editor), así que el modo de pad que muestra la pantalla de rekordbox no cambia solo: no importa, cada función es explícita (`PAD1_HotCue`, `PAD1_Sampler`…) y se ejecuta sin importar el modo visible.

### GROUP A — DECK 1 · HOT CUE + PAD FX 1

```
+-----------------------+-----------------------+-----------------------+-----------------------+
| 13: Pad FX 1 · slot 5 | 14: Pad FX 1 · slot 6 | 15: Pad FX 1 · slot 7 | 16: Pad FX 1 · slot 8 |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 9: Pad FX 1 · slot 1  | 10: Pad FX 1 · slot 2 | 11: Pad FX 1 · slot 3 | 12: Pad FX 1 · slot 4 |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 5: Hot Cue 5          | 6: Hot Cue 6          | 7: Hot Cue 7          | 8: Hot Cue 8          |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 1: Hot Cue 1          | 2: Hot Cue 2          | 3: Hot Cue 3          | 4: Hot Cue 4          |
+-----------------------+-----------------------+-----------------------+-----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **8** · nota **0** (0x00) | `9700` | `PAD1_HotCue` ✅ | Hot Cue 1 |
| 2 | Note · ch **8** · nota **1** (0x01) | `9701` | `PAD2_HotCue` ✅ | Hot Cue 2 |
| 3 | Note · ch **8** · nota **2** (0x02) | `9702` | `PAD3_HotCue` ✅ | Hot Cue 3 |
| 4 | Note · ch **8** · nota **3** (0x03) | `9703` | `PAD4_HotCue` ✅ | Hot Cue 4 |
| 5 | Note · ch **8** · nota **4** (0x04) | `9704` | `PAD5_HotCue` ✅ | Hot Cue 5 |
| 6 | Note · ch **8** · nota **5** (0x05) | `9705` | `PAD6_HotCue` ✅ | Hot Cue 6 |
| 7 | Note · ch **8** · nota **6** (0x06) | `9706` | `PAD7_HotCue` ✅ | Hot Cue 7 |
| 8 | Note · ch **8** · nota **7** (0x07) | `9707` | `PAD8_HotCue` ✅ | Hot Cue 8 |
| 9 | Note · ch **8** · nota **16** (0x10) | `9710` | `PAD1_PadFx1` ✅ | Pad FX 1 · slot 1 |
| 10 | Note · ch **8** · nota **17** (0x11) | `9711` | `PAD2_PadFx1` ✅ | Pad FX 1 · slot 2 |
| 11 | Note · ch **8** · nota **18** (0x12) | `9712` | `PAD3_PadFx1` ✅ | Pad FX 1 · slot 3 |
| 12 | Note · ch **8** · nota **19** (0x13) | `9713` | `PAD4_PadFx1` ✅ | Pad FX 1 · slot 4 |
| 13 | Note · ch **8** · nota **20** (0x14) | `9714` | `PAD5_PadFx1` ✅ | Pad FX 1 · slot 5 |
| 14 | Note · ch **8** · nota **21** (0x15) | `9715` | `PAD6_PadFx1` ✅ | Pad FX 1 · slot 6 |
| 15 | Note · ch **8** · nota **22** (0x16) | `9716` | `PAD7_PadFx1` ✅ | Pad FX 1 · slot 7 |
| 16 | Note · ch **8** · nota **23** (0x17) | `9717` | `PAD8_PadFx1` ✅ | Pad FX 1 · slot 8 |

### GROUP B — DECK 2 · HOT CUE + PAD FX 1

```
+-----------------------+-----------------------+-----------------------+-----------------------+
| 13: Pad FX 1 · slot 5 | 14: Pad FX 1 · slot 6 | 15: Pad FX 1 · slot 7 | 16: Pad FX 1 · slot 8 |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 9: Pad FX 1 · slot 1  | 10: Pad FX 1 · slot 2 | 11: Pad FX 1 · slot 3 | 12: Pad FX 1 · slot 4 |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 5: Hot Cue 5          | 6: Hot Cue 6          | 7: Hot Cue 7          | 8: Hot Cue 8          |
+-----------------------+-----------------------+-----------------------+-----------------------+
| 1: Hot Cue 1          | 2: Hot Cue 2          | 3: Hot Cue 3          | 4: Hot Cue 4          |
+-----------------------+-----------------------+-----------------------+-----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **10** · nota **0** (0x00) | `9900` | `PAD1_HotCue` ✅ | Hot Cue 1 |
| 2 | Note · ch **10** · nota **1** (0x01) | `9901` | `PAD2_HotCue` ✅ | Hot Cue 2 |
| 3 | Note · ch **10** · nota **2** (0x02) | `9902` | `PAD3_HotCue` ✅ | Hot Cue 3 |
| 4 | Note · ch **10** · nota **3** (0x03) | `9903` | `PAD4_HotCue` ✅ | Hot Cue 4 |
| 5 | Note · ch **10** · nota **4** (0x04) | `9904` | `PAD5_HotCue` ✅ | Hot Cue 5 |
| 6 | Note · ch **10** · nota **5** (0x05) | `9905` | `PAD6_HotCue` ✅ | Hot Cue 6 |
| 7 | Note · ch **10** · nota **6** (0x06) | `9906` | `PAD7_HotCue` ✅ | Hot Cue 7 |
| 8 | Note · ch **10** · nota **7** (0x07) | `9907` | `PAD8_HotCue` ✅ | Hot Cue 8 |
| 9 | Note · ch **10** · nota **16** (0x10) | `9910` | `PAD1_PadFx1` ✅ | Pad FX 1 · slot 1 |
| 10 | Note · ch **10** · nota **17** (0x11) | `9911` | `PAD2_PadFx1` ✅ | Pad FX 1 · slot 2 |
| 11 | Note · ch **10** · nota **18** (0x12) | `9912` | `PAD3_PadFx1` ✅ | Pad FX 1 · slot 3 |
| 12 | Note · ch **10** · nota **19** (0x13) | `9913` | `PAD4_PadFx1` ✅ | Pad FX 1 · slot 4 |
| 13 | Note · ch **10** · nota **20** (0x14) | `9914` | `PAD5_PadFx1` ✅ | Pad FX 1 · slot 5 |
| 14 | Note · ch **10** · nota **21** (0x15) | `9915` | `PAD6_PadFx1` ✅ | Pad FX 1 · slot 6 |
| 15 | Note · ch **10** · nota **22** (0x16) | `9916` | `PAD7_PadFx1` ✅ | Pad FX 1 · slot 7 |
| 16 | Note · ch **10** · nota **23** (0x17) | `9917` | `PAD8_PadFx1` ✅ | Pad FX 1 · slot 8 |

### GROUP C — DECK 1 · BEAT JUMP + BEAT LOOP

```
+----------------------+----------------------+----------------------+----------------------+
| 13: Beat Loop slot 5 | 14: Beat Loop slot 6 | 15: Beat Loop slot 7 | 16: Beat Loop slot 8 |
+----------------------+----------------------+----------------------+----------------------+
| 9: Beat Loop slot 1  | 10: Beat Loop slot 2 | 11: Beat Loop slot 3 | 12: Beat Loop slot 4 |
+----------------------+----------------------+----------------------+----------------------+
| 5: Beat Jump <4      | 6: Beat Jump >4      | 7: Beat Jump <8      | 8: Beat Jump >8      |
+----------------------+----------------------+----------------------+----------------------+
| 1: Beat Jump <1      | 2: Beat Jump >1      | 3: Beat Jump <2      | 4: Beat Jump >2      |
+----------------------+----------------------+----------------------+----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **8** · nota **32** (0x20) | `9720` | `PAD1_BeatJump` ✅ | Beat Jump <1 |
| 2 | Note · ch **8** · nota **33** (0x21) | `9721` | `PAD2_BeatJump` ✅ | Beat Jump >1 |
| 3 | Note · ch **8** · nota **34** (0x22) | `9722` | `PAD3_BeatJump` ✅ | Beat Jump <2 |
| 4 | Note · ch **8** · nota **35** (0x23) | `9723` | `PAD4_BeatJump` ✅ | Beat Jump >2 |
| 5 | Note · ch **8** · nota **36** (0x24) | `9724` | `PAD5_BeatJump` ✅ | Beat Jump <4 |
| 6 | Note · ch **8** · nota **37** (0x25) | `9725` | `PAD6_BeatJump` ✅ | Beat Jump >4 |
| 7 | Note · ch **8** · nota **38** (0x26) | `9726` | `PAD7_BeatJump` ✅ | Beat Jump <8 |
| 8 | Note · ch **8** · nota **39** (0x27) | `9727` | `PAD8_BeatJump` ✅ | Beat Jump >8 |
| 9 | Note · ch **8** · nota **96** (0x60) | `9760` | `PAD1_BeatLoop` ✅ | Beat Loop slot 1 |
| 10 | Note · ch **8** · nota **97** (0x61) | `9761` | `PAD2_BeatLoop` ✅ | Beat Loop slot 2 |
| 11 | Note · ch **8** · nota **98** (0x62) | `9762` | `PAD3_BeatLoop` ✅ | Beat Loop slot 3 |
| 12 | Note · ch **8** · nota **99** (0x63) | `9763` | `PAD4_BeatLoop` ✅ | Beat Loop slot 4 |
| 13 | Note · ch **8** · nota **100** (0x64) | `9764` | `PAD5_BeatLoop` ✅ | Beat Loop slot 5 |
| 14 | Note · ch **8** · nota **101** (0x65) | `9765` | `PAD6_BeatLoop` ✅ | Beat Loop slot 6 |
| 15 | Note · ch **8** · nota **102** (0x66) | `9766` | `PAD7_BeatLoop` ✅ | Beat Loop slot 7 |
| 16 | Note · ch **8** · nota **103** (0x67) | `9767` | `PAD8_BeatLoop` ✅ | Beat Loop slot 8 |

### GROUP D — DECK 2 · BEAT JUMP + BEAT LOOP

```
+----------------------+----------------------+----------------------+----------------------+
| 13: Beat Loop slot 5 | 14: Beat Loop slot 6 | 15: Beat Loop slot 7 | 16: Beat Loop slot 8 |
+----------------------+----------------------+----------------------+----------------------+
| 9: Beat Loop slot 1  | 10: Beat Loop slot 2 | 11: Beat Loop slot 3 | 12: Beat Loop slot 4 |
+----------------------+----------------------+----------------------+----------------------+
| 5: Beat Jump <4      | 6: Beat Jump >4      | 7: Beat Jump <8      | 8: Beat Jump >8      |
+----------------------+----------------------+----------------------+----------------------+
| 1: Beat Jump <1      | 2: Beat Jump >1      | 3: Beat Jump <2      | 4: Beat Jump >2      |
+----------------------+----------------------+----------------------+----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **10** · nota **32** (0x20) | `9920` | `PAD1_BeatJump` ✅ | Beat Jump <1 |
| 2 | Note · ch **10** · nota **33** (0x21) | `9921` | `PAD2_BeatJump` ✅ | Beat Jump >1 |
| 3 | Note · ch **10** · nota **34** (0x22) | `9922` | `PAD3_BeatJump` ✅ | Beat Jump <2 |
| 4 | Note · ch **10** · nota **35** (0x23) | `9923` | `PAD4_BeatJump` ✅ | Beat Jump >2 |
| 5 | Note · ch **10** · nota **36** (0x24) | `9924` | `PAD5_BeatJump` ✅ | Beat Jump <4 |
| 6 | Note · ch **10** · nota **37** (0x25) | `9925` | `PAD6_BeatJump` ✅ | Beat Jump >4 |
| 7 | Note · ch **10** · nota **38** (0x26) | `9926` | `PAD7_BeatJump` ✅ | Beat Jump <8 |
| 8 | Note · ch **10** · nota **39** (0x27) | `9927` | `PAD8_BeatJump` ✅ | Beat Jump >8 |
| 9 | Note · ch **10** · nota **96** (0x60) | `9960` | `PAD1_BeatLoop` ✅ | Beat Loop slot 1 |
| 10 | Note · ch **10** · nota **97** (0x61) | `9961` | `PAD2_BeatLoop` ✅ | Beat Loop slot 2 |
| 11 | Note · ch **10** · nota **98** (0x62) | `9962` | `PAD3_BeatLoop` ✅ | Beat Loop slot 3 |
| 12 | Note · ch **10** · nota **99** (0x63) | `9963` | `PAD4_BeatLoop` ✅ | Beat Loop slot 4 |
| 13 | Note · ch **10** · nota **100** (0x64) | `9964` | `PAD5_BeatLoop` ✅ | Beat Loop slot 5 |
| 14 | Note · ch **10** · nota **101** (0x65) | `9965` | `PAD6_BeatLoop` ✅ | Beat Loop slot 6 |
| 15 | Note · ch **10** · nota **102** (0x66) | `9966` | `PAD7_BeatLoop` ✅ | Beat Loop slot 7 |
| 16 | Note · ch **10** · nota **103** (0x67) | `9967` | `PAD8_BeatLoop` ✅ | Beat Loop slot 8 |

### GROUP E — DECK 1 · PAD FX 2 + BORRAR HOT CUE

```
+----------------------+----------------------+----------------------+----------------------+
| 13: Borrar Hot Cue 5 | 14: Borrar Hot Cue 6 | 15: Borrar Hot Cue 7 | 16: Borrar Hot Cue 8 |
+----------------------+----------------------+----------------------+----------------------+
| 9: Borrar Hot Cue 1  | 10: Borrar Hot Cue 2 | 11: Borrar Hot Cue 3 | 12: Borrar Hot Cue 4 |
+----------------------+----------------------+----------------------+----------------------+
| 5: Pad FX 2 · slot 5 | 6: Pad FX 2 · slot 6 | 7: Pad FX 2 · slot 7 | 8: Pad FX 2 · slot 8 |
+----------------------+----------------------+----------------------+----------------------+
| 1: Pad FX 2 · slot 1 | 2: Pad FX 2 · slot 2 | 3: Pad FX 2 · slot 3 | 4: Pad FX 2 · slot 4 |
+----------------------+----------------------+----------------------+----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **8** · nota **80** (0x50) | `9750` | `PAD1_PadFx2` ⚠️ | Pad FX 2 · slot 1 |
| 2 | Note · ch **8** · nota **81** (0x51) | `9751` | `PAD2_PadFx2` ⚠️ | Pad FX 2 · slot 2 |
| 3 | Note · ch **8** · nota **82** (0x52) | `9752` | `PAD3_PadFx2` ⚠️ | Pad FX 2 · slot 3 |
| 4 | Note · ch **8** · nota **83** (0x53) | `9753` | `PAD4_PadFx2` ⚠️ | Pad FX 2 · slot 4 |
| 5 | Note · ch **8** · nota **84** (0x54) | `9754` | `PAD5_PadFx2` ⚠️ | Pad FX 2 · slot 5 |
| 6 | Note · ch **8** · nota **85** (0x55) | `9755` | `PAD6_PadFx2` ⚠️ | Pad FX 2 · slot 6 |
| 7 | Note · ch **8** · nota **86** (0x56) | `9756` | `PAD7_PadFx2` ⚠️ | Pad FX 2 · slot 7 |
| 8 | Note · ch **8** · nota **87** (0x57) | `9757` | `PAD8_PadFx2` ⚠️ | Pad FX 2 · slot 8 |
| 9 | Note · ch **9** · nota **0** (0x00) | `9800` | `PAD1_HotCue+Shift` ✅ | Borrar Hot Cue 1 |
| 10 | Note · ch **9** · nota **1** (0x01) | `9801` | `PAD2_HotCue+Shift` ✅ | Borrar Hot Cue 2 |
| 11 | Note · ch **9** · nota **2** (0x02) | `9802` | `PAD3_HotCue+Shift` ✅ | Borrar Hot Cue 3 |
| 12 | Note · ch **9** · nota **3** (0x03) | `9803` | `PAD4_HotCue+Shift` ✅ | Borrar Hot Cue 4 |
| 13 | Note · ch **9** · nota **4** (0x04) | `9804` | `PAD5_HotCue+Shift` ✅ | Borrar Hot Cue 5 |
| 14 | Note · ch **9** · nota **5** (0x05) | `9805` | `PAD6_HotCue+Shift` ✅ | Borrar Hot Cue 6 |
| 15 | Note · ch **9** · nota **6** (0x06) | `9806` | `PAD7_HotCue+Shift` ✅ | Borrar Hot Cue 7 |
| 16 | Note · ch **9** · nota **7** (0x07) | `9807` | `PAD8_HotCue+Shift` ✅ | Borrar Hot Cue 8 |

### GROUP F — DECK 2 · PAD FX 2 + BORRAR HOT CUE

```
+----------------------+----------------------+----------------------+----------------------+
| 13: Borrar Hot Cue 5 | 14: Borrar Hot Cue 6 | 15: Borrar Hot Cue 7 | 16: Borrar Hot Cue 8 |
+----------------------+----------------------+----------------------+----------------------+
| 9: Borrar Hot Cue 1  | 10: Borrar Hot Cue 2 | 11: Borrar Hot Cue 3 | 12: Borrar Hot Cue 4 |
+----------------------+----------------------+----------------------+----------------------+
| 5: Pad FX 2 · slot 5 | 6: Pad FX 2 · slot 6 | 7: Pad FX 2 · slot 7 | 8: Pad FX 2 · slot 8 |
+----------------------+----------------------+----------------------+----------------------+
| 1: Pad FX 2 · slot 1 | 2: Pad FX 2 · slot 2 | 3: Pad FX 2 · slot 3 | 4: Pad FX 2 · slot 4 |
+----------------------+----------------------+----------------------+----------------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **10** · nota **80** (0x50) | `9950` | `PAD1_PadFx2` ⚠️ | Pad FX 2 · slot 1 |
| 2 | Note · ch **10** · nota **81** (0x51) | `9951` | `PAD2_PadFx2` ⚠️ | Pad FX 2 · slot 2 |
| 3 | Note · ch **10** · nota **82** (0x52) | `9952` | `PAD3_PadFx2` ⚠️ | Pad FX 2 · slot 3 |
| 4 | Note · ch **10** · nota **83** (0x53) | `9953` | `PAD4_PadFx2` ⚠️ | Pad FX 2 · slot 4 |
| 5 | Note · ch **10** · nota **84** (0x54) | `9954` | `PAD5_PadFx2` ⚠️ | Pad FX 2 · slot 5 |
| 6 | Note · ch **10** · nota **85** (0x55) | `9955` | `PAD6_PadFx2` ⚠️ | Pad FX 2 · slot 6 |
| 7 | Note · ch **10** · nota **86** (0x56) | `9956` | `PAD7_PadFx2` ⚠️ | Pad FX 2 · slot 7 |
| 8 | Note · ch **10** · nota **87** (0x57) | `9957` | `PAD8_PadFx2` ⚠️ | Pad FX 2 · slot 8 |
| 9 | Note · ch **11** · nota **0** (0x00) | `9A00` | `PAD1_HotCue+Shift` ✅ | Borrar Hot Cue 1 |
| 10 | Note · ch **11** · nota **1** (0x01) | `9A01` | `PAD2_HotCue+Shift` ✅ | Borrar Hot Cue 2 |
| 11 | Note · ch **11** · nota **2** (0x02) | `9A02` | `PAD3_HotCue+Shift` ✅ | Borrar Hot Cue 3 |
| 12 | Note · ch **11** · nota **3** (0x03) | `9A03` | `PAD4_HotCue+Shift` ✅ | Borrar Hot Cue 4 |
| 13 | Note · ch **11** · nota **4** (0x04) | `9A04` | `PAD5_HotCue+Shift` ✅ | Borrar Hot Cue 5 |
| 14 | Note · ch **11** · nota **5** (0x05) | `9A05` | `PAD6_HotCue+Shift` ✅ | Borrar Hot Cue 6 |
| 15 | Note · ch **11** · nota **6** (0x06) | `9A06` | `PAD7_HotCue+Shift` ✅ | Borrar Hot Cue 7 |
| 16 | Note · ch **11** · nota **7** (0x07) | `9A07` | `PAD8_HotCue+Shift` ✅ | Borrar Hot Cue 8 |

### GROUP G — SAMPLER · PLAY (slots 1-16 del banco activo)

```
+-----------------+-----------------+-----------------+-----------------+
| 13: Sample 13 ▶ | 14: Sample 14 ▶ | 15: Sample 15 ▶ | 16: Sample 16 ▶ |
+-----------------+-----------------+-----------------+-----------------+
| 9: Sample 9 ▶   | 10: Sample 10 ▶ | 11: Sample 11 ▶ | 12: Sample 12 ▶ |
+-----------------+-----------------+-----------------+-----------------+
| 5: Sample 5 ▶   | 6: Sample 6 ▶   | 7: Sample 7 ▶   | 8: Sample 8 ▶   |
+-----------------+-----------------+-----------------+-----------------+
| 1: Sample 1 ▶   | 2: Sample 2 ▶   | 3: Sample 3 ▶   | 4: Sample 4 ▶   |
+-----------------+-----------------+-----------------+-----------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **8** · nota **48** (0x30) | `9730` | `PAD1_Sampler` ✅ | Sample 1 ▶ |
| 2 | Note · ch **8** · nota **49** (0x31) | `9731` | `PAD2_Sampler` ✅ | Sample 2 ▶ |
| 3 | Note · ch **8** · nota **50** (0x32) | `9732` | `PAD3_Sampler` ✅ | Sample 3 ▶ |
| 4 | Note · ch **8** · nota **51** (0x33) | `9733` | `PAD4_Sampler` ✅ | Sample 4 ▶ |
| 5 | Note · ch **8** · nota **52** (0x34) | `9734` | `PAD5_Sampler` ✅ | Sample 5 ▶ |
| 6 | Note · ch **8** · nota **53** (0x35) | `9735` | `PAD6_Sampler` ✅ | Sample 6 ▶ |
| 7 | Note · ch **8** · nota **54** (0x36) | `9736` | `PAD7_Sampler` ✅ | Sample 7 ▶ |
| 8 | Note · ch **8** · nota **55** (0x37) | `9737` | `PAD8_Sampler` ✅ | Sample 8 ▶ |
| 9 | Note · ch **8** · nota **56** (0x38) | `9738` | `PAD9_Sampler` ⚠️ | Sample 9 ▶ |
| 10 | Note · ch **8** · nota **57** (0x39) | `9739` | `PAD10_Sampler` ⚠️ | Sample 10 ▶ |
| 11 | Note · ch **8** · nota **58** (0x3A) | `973A` | `PAD11_Sampler` ⚠️ | Sample 11 ▶ |
| 12 | Note · ch **8** · nota **59** (0x3B) | `973B` | `PAD12_Sampler` ⚠️ | Sample 12 ▶ |
| 13 | Note · ch **8** · nota **60** (0x3C) | `973C` | `PAD13_Sampler` ⚠️ | Sample 13 ▶ |
| 14 | Note · ch **8** · nota **61** (0x3D) | `973D` | `PAD14_Sampler` ⚠️ | Sample 14 ▶ |
| 15 | Note · ch **8** · nota **62** (0x3E) | `973E` | `PAD15_Sampler` ⚠️ | Sample 15 ▶ |
| 16 | Note · ch **8** · nota **63** (0x3F) | `973F` | `PAD16_Sampler` ⚠️ | Sample 16 ▶ |

### GROUP H — SAMPLER · STOP (slots 1-16 del banco activo)

```
+-----------------+-----------------+-----------------+-----------------+
| 13: Sample 13 ■ | 14: Sample 14 ■ | 15: Sample 15 ■ | 16: Sample 16 ■ |
+-----------------+-----------------+-----------------+-----------------+
| 9: Sample 9 ■   | 10: Sample 10 ■ | 11: Sample 11 ■ | 12: Sample 12 ■ |
+-----------------+-----------------+-----------------+-----------------+
| 5: Sample 5 ■   | 6: Sample 6 ■   | 7: Sample 7 ■   | 8: Sample 8 ■   |
+-----------------+-----------------+-----------------+-----------------+
| 1: Sample 1 ■   | 2: Sample 2 ■   | 3: Sample 3 ■   | 4: Sample 4 ■   |
+-----------------+-----------------+-----------------+-----------------+
```

| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| 1 | Note · ch **9** · nota **48** (0x30) | `9830` | `PAD1_Sampler+Shift` ✅ | Sample 1 ■ |
| 2 | Note · ch **9** · nota **49** (0x31) | `9831` | `PAD2_Sampler+Shift` ✅ | Sample 2 ■ |
| 3 | Note · ch **9** · nota **50** (0x32) | `9832` | `PAD3_Sampler+Shift` ✅ | Sample 3 ■ |
| 4 | Note · ch **9** · nota **51** (0x33) | `9833` | `PAD4_Sampler+Shift` ✅ | Sample 4 ■ |
| 5 | Note · ch **9** · nota **52** (0x34) | `9834` | `PAD5_Sampler+Shift` ✅ | Sample 5 ■ |
| 6 | Note · ch **9** · nota **53** (0x35) | `9835` | `PAD6_Sampler+Shift` ✅ | Sample 6 ■ |
| 7 | Note · ch **9** · nota **54** (0x36) | `9836` | `PAD7_Sampler+Shift` ✅ | Sample 7 ■ |
| 8 | Note · ch **9** · nota **55** (0x37) | `9837` | `PAD8_Sampler+Shift` ✅ | Sample 8 ■ |
| 9 | Note · ch **9** · nota **56** (0x38) | `9838` | `PAD9_Sampler+Shift` ⚠️ | Sample 9 ■ |
| 10 | Note · ch **9** · nota **57** (0x39) | `9839` | `PAD10_Sampler+Shift` ⚠️ | Sample 10 ■ |
| 11 | Note · ch **9** · nota **58** (0x3A) | `983A` | `PAD11_Sampler+Shift` ⚠️ | Sample 11 ■ |
| 12 | Note · ch **9** · nota **59** (0x3B) | `983B` | `PAD12_Sampler+Shift` ⚠️ | Sample 12 ■ |
| 13 | Note · ch **9** · nota **60** (0x3C) | `983C` | `PAD13_Sampler+Shift` ⚠️ | Sample 13 ■ |
| 14 | Note · ch **9** · nota **61** (0x3D) | `983D` | `PAD14_Sampler+Shift` ⚠️ | Sample 14 ■ |
| 15 | Note · ch **9** · nota **62** (0x3E) | `983E` | `PAD15_Sampler+Shift` ⚠️ | Sample 15 ■ |
| 16 | Note · ch **9** · nota **63** (0x3F) | `983F` | `PAD16_Sampler+Shift` ⚠️ | Sample 16 ■ |

## 4. Páginas de knobs (PAGE ◄ ►)

Cada página tiene los **8 knobs** bajo los displays y los **8 botones** sobre los displays (Botón 1 = izquierda). Los knobs del MK1 solo mandan valores **Absolute** (0-127) en Controller Editor: no existe modo Relative. Por eso no hay funciones tipo *Rotary* (Browse, Zoom, Loop) y la navegación de la biblioteca va con botones.

### Página 1 — FX1 · BEAT FX 1 + COLOR FX

| Knob | Controller Editor (CC · canal · nº · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| K1 | CC · ch **5** · nº **2** (0x02) · **Absolute** | `B402` | `FX1-1` ✅ | FX1 slot 1 · level/depth |
| K2 | CC · ch **5** · nº **3** (0x03) · **Absolute** | `B403` | `FX1-2` ✅ | FX1 slot 2 (modo multi) |
| K3 | CC · ch **5** · nº **4** (0x04) · **Absolute** | `B404` | `FX1-3` ✅ | FX1 slot 3 (modo multi) |
| K4 | CC · ch **5** · nº **5** (0x05) · **Absolute** | `B405` | `FX1-1Select` ⚠️ | Selector de efecto FX1 (truco KnobSlider) |
| K5 | CC · ch **7** · nº **23** (0x17) · **Absolute** | `B617` | `CFXParameterCH1` ✅ | Color FX canal 1 |
| K6 | CC · ch **7** · nº **24** (0x18) · **Absolute** | `B618` | `CFXParameterCH2` ✅ | Color FX canal 2 |
| K7 | CC · ch **7** · nº **25** (0x19) · **Absolute** | `B619` | `CFXParameterCH3` ✅ | Color FX canal 3 |
| K8 | CC · ch **7** · nº **26** (0x1A) · **Absolute** | `B61A` | `CFXParameterCH4` ✅ | Color FX canal 4 |

| Botón | Controller Editor (Note · canal · nota · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| B1 | Note · ch **5** · nota **71** (0x47) · **Gate** | `9447` | `FX1-1On` ✅ | FX1 slot 1 ON/OFF |
| B2 | Note · ch **5** · nota **72** (0x48) · **Gate** | `9448` | `FX1-2On` ✅ | FX1 slot 2 ON/OFF |
| B3 | Note · ch **5** · nota **73** (0x49) · **Gate** | `9449` | `FX1-3On` ✅ | FX1 slot 3 ON/OFF |
| B4 | Note · ch **5** · nota **74** (0x4A) · **Gate** | `944A` | `FX1BeatDown` ✅ | FX1 beat ◄ |
| B5 | Note · ch **5** · nota **75** (0x4B) · **Gate** | `944B` | `FX1BeatUp` ✅ | FX1 beat ► |
| B6 | Note · ch **5** · nota **16** (0x10) · **Toggle** | `9410` | `FX1Assign.CH1` ✅ | FX1 → canal 1 |
| B7 | Note · ch **5** · nota **17** (0x11) · **Toggle** | `9411` | `FX1Assign.CH2` ✅ | FX1 → canal 2 |
| B8 | Note · ch **5** · nota **20** (0x14) · **Toggle** | `9414` | `FX1Assign.MASTER` ✅ | FX1 → master |

### Página 2 — FX2 · BEAT FX 2

| Knob | Controller Editor (CC · canal · nº · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| K1 | CC · ch **6** · nº **2** (0x02) · **Absolute** | `B502` | `FX2-1` ⚠️ | FX2 slot 1 · level/depth |
| K2 | CC · ch **6** · nº **3** (0x03) · **Absolute** | `B503` | `FX2-2` ⚠️ | FX2 slot 2 (modo multi) |
| K3 | CC · ch **6** · nº **4** (0x04) · **Absolute** | `B504` | `FX2-3` ⚠️ | FX2 slot 3 (modo multi) |
| K4 | CC · ch **6** · nº **5** (0x05) · **Absolute** | `B505` | `FX2-1Select` ⚠️ | Selector de efecto FX2 (truco KnobSlider) |
| K5 | — | — | *(libre)* | Sin asignar |
| K6 | — | — | *(libre)* | Sin asignar |
| K7 | — | — | *(libre)* | Sin asignar |
| K8 | — | — | *(libre)* | Sin asignar |

| Botón | Controller Editor (Note · canal · nota · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| B1 | Note · ch **6** · nota **71** (0x47) · **Gate** | `9547` | `FX2-1On` ⚠️ | FX2 slot 1 ON/OFF |
| B2 | Note · ch **6** · nota **72** (0x48) · **Gate** | `9548` | `FX2-2On` ⚠️ | FX2 slot 2 ON/OFF |
| B3 | Note · ch **6** · nota **73** (0x49) · **Gate** | `9549` | `FX2-3On` ⚠️ | FX2 slot 3 ON/OFF |
| B4 | Note · ch **6** · nota **74** (0x4A) · **Gate** | `954A` | `FX2BeatDown` ⚠️ | FX2 beat ◄ |
| B5 | Note · ch **6** · nota **75** (0x4B) · **Gate** | `954B` | `FX2BeatUp` ⚠️ | FX2 beat ► |
| B6 | Note · ch **6** · nota **16** (0x10) · **Toggle** | `9510` | `FX2Assign.CH1` ⚠️ | FX2 → canal 1 |
| B7 | Note · ch **6** · nota **17** (0x11) · **Toggle** | `9511` | `FX2Assign.CH2` ⚠️ | FX2 → canal 2 |
| B8 | Note · ch **6** · nota **20** (0x14) · **Toggle** | `9514` | `FX2Assign.MASTER` ⚠️ | FX2 → master |

### Página 3 — FX SELECT · + MIXER (gain/EQ)

| Knob | Controller Editor (CC · canal · nº · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| K1 | CC · ch **1** · nº **4** (0x04) · **Absolute** | `B004` | `Gain` ✅ | Deck 1 · Gain |
| K2 | CC · ch **1** · nº **7** (0x07) · **Absolute** | `B007` | `EQHigh` ✅ | Deck 1 · EQ High |
| K3 | CC · ch **1** · nº **11** (0x0B) · **Absolute** | `B00B` | `EQMid` ✅ | Deck 1 · EQ Mid |
| K4 | CC · ch **1** · nº **15** (0x0F) · **Absolute** | `B00F` | `EQLow` ✅ | Deck 1 · EQ Low |
| K5 | CC · ch **2** · nº **4** (0x04) · **Absolute** | `B104` | `Gain` ✅ | Deck 2 · Gain |
| K6 | CC · ch **2** · nº **7** (0x07) · **Absolute** | `B107` | `EQHigh` ✅ | Deck 2 · EQ High |
| K7 | CC · ch **2** · nº **11** (0x0B) · **Absolute** | `B10B` | `EQMid` ✅ | Deck 2 · EQ Mid |
| K8 | CC · ch **2** · nº **15** (0x0F) · **Absolute** | `B10F` | `EQLow` ✅ | Deck 2 · EQ Low |

| Botón | Controller Editor (Note · canal · nota · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| B1 | Note · ch **5** · nota **33** (0x21) · **Gate** | `9421` | `FX1-1Select.ECHO` ✅ | FX1 = ECHO |
| B2 | Note · ch **5** · nota **35** (0x23) · **Gate** | `9423` | `FX1-1Select.SPIRAL` ✅ | FX1 = SPIRAL |
| B3 | Note · ch **5** · nota **37** (0x25) · **Gate** | `9425` | `FX1-1Select.REVERB` ✅ | FX1 = REVERB |
| B4 | Note · ch **5** · nota **38** (0x26) · **Gate** | `9426` | `FX1-1Select.FLANGER` ✅ | FX1 = FLANGER |
| B5 | Note · ch **5** · nota **39** (0x27) · **Gate** | `9427` | `FX1-1Select.PHASER` ✅ | FX1 = PHASER |
| B6 | Note · ch **5** · nota **40** (0x28) · **Gate** | `9428` | `FX1-1Select.FILTER` ✅ | FX1 = FILTER |
| B7 | Note · ch **5** · nota **43** (0x2B) · **Gate** | `942B` | `FX1-1Select.ROLL` ✅ | FX1 = ROLL |
| B8 | Note · ch **5** · nota **41** (0x29) · **Gate** | `9429` | `FX1-1Select.TRANS` ✅ | FX1 = TRANS |

### Página 4 — COLOR FX type + QUANTIZE

| Knob | Controller Editor (CC · canal · nº · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| K1 | — | — | *(libre)* | Sin asignar |
| K2 | — | — | *(libre)* | Sin asignar |
| K3 | — | — | *(libre)* | Sin asignar |
| K4 | — | — | *(libre)* | Sin asignar |
| K5 | — | — | *(libre)* | Sin asignar |
| K6 | — | — | *(libre)* | Sin asignar |
| K7 | — | — | *(libre)* | Sin asignar |
| K8 | — | — | *(libre)* | Sin asignar |

| Botón | Controller Editor (Note · canal · nota · modo) | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| B1 | Note · ch **7** · nota **0** (0x00) · **Gate** | `9600` | `CFX1On` ✅ | Color FX = SPACE |
| B2 | Note · ch **7** · nota **1** (0x01) · **Gate** | `9601` | `CFX2On` ✅ | Color FX = D-ECHO |
| B3 | Note · ch **7** · nota **2** (0x02) · **Gate** | `9602` | `CFX3On` ✅ | Color FX = CRUSH |
| B4 | Note · ch **7** · nota **3** (0x03) · **Gate** | `9603` | `CFX4On` ✅ | Color FX = PITCH |
| B5 | Note · ch **7** · nota **4** (0x04) · **Gate** | `9604` | `CFX5On` ✅ | Color FX = NOISE |
| B6 | Note · ch **7** · nota **5** (0x05) · **Gate** | `9605` | `CFX6On` ✅ | Color FX = FILTER |
| B7 | Note · ch **1** · nota **53** (0x35) · **Gate** | `9035` | `Quantize` ✅ | Deck 1 · Quantize |
| B8 | Note · ch **2** · nota **53** (0x35) · **Gate** | `9135` | `Quantize` ✅ | Deck 2 · Quantize |

## 5. Botones globales (no dependen de página)

| Botón MK1 | Zona | Controller Editor | Código | Función rekordbox | Acción |
|---|---|---|---|---|---|
| **CONTROL** | Arriba-izq. | Note · ch 7 · nota 101 (0x65) · Gate | `9665` | `Back` ✅ | Biblioteca: atrás / cerrar carpeta |
| **STEP** | Arriba-izq. | Note · ch 7 · nota 122 (0x7A) · Gate | `967A` | `SwitchActiveWindow` ✅ | BROWSE VIEW (navegador grande on/off) |
| **BROWSE** | Arriba-izq. | Note · ch 7 · nota 70 (0x46) · Gate | `9646` | `Load` ✅ | Cargar track en **Deck 1** |
| **SAMPLING** | Arriba-izq. | Note · ch 7 · nota 71 (0x47) · Gate | `9647` | `Load` ✅ | Cargar track en **Deck 2** |
| **◄ ► (bajo BROWSE)** | Arriba-izq. | — | — | — | Reservados por Controller Editor: cambian la **página de knobs** (SHIFT+◄► = plantilla) |
| **F1** | Arriba-izq. | Note · ch 7 · nota 54 (0x36) · Gate | `9636` | `PlayPausePreview` ✅ | Preview del track seleccionado |
| **F2** | Arriba-izq. | Note · ch 7 · nota 103 (0x67) · Gate | `9667` | `AddToTagList` ✅ | Agregar track a la Tag List |
| **NOTE REPEAT** | Master | Note · ch 5 · nota 67 (0x43) · Gate | `9443` | `FX1ReleaseFXOn` ✅ | **RELEASE FX** (echo out / brake / backspin) mientras se mantiene |
| **SCENE** | Columna central | Note · ch 1 · nota 11 (0x0B) · Gate | `900B` | `PlayPause` ✅ | Deck 1 · Play/Pause |
| **PATTERN** | Columna central | Note · ch 2 · nota 11 (0x0B) · Gate | `910B` | `PlayPause` ✅ | Deck 2 · Play/Pause |
| **KEYBOARD (PAD MODE)** | Columna central | Note · ch 1 · nota 12 (0x0C) · Gate | `900C` | `Cue` ✅ | Deck 1 · Cue |
| **NAVIGATE** | Columna central | Note · ch 2 · nota 12 (0x0C) · Gate | `910C` | `Cue` ✅ | Deck 2 · Cue |
| **DUPLICATE** | Columna central | Note · ch 1 · nota 88 (0x58) · Gate | `9058` | `Sync` ✅ | Deck 1 · Beat Sync |
| **SELECT** | Columna central | Note · ch 2 · nota 88 (0x58) · Gate | `9158` | `Sync` ✅ | Deck 2 · Beat Sync |
| **SOLO** | Columna central | Note · ch 1 · nota 20 (0x14) · Gate | `9014` | `4BeatLoop` ✅ | Deck 1 · Auto loop 4 beats |
| **MUTE** | Columna central | Note · ch 2 · nota 20 (0x14) · Gate | `9114` | `4BeatLoop` ✅ | Deck 2 · Auto loop 4 beats |
| **A – H (GROUPS)** | Grupos | — | — | — | Reservados: seleccionan la **capa de pads** (Pad Page A–H) |
| **LOOP** | Transporte | Note · ch 7 · nota 121 (0x79) · Gate | `9679` | `Forward` ✅ | Biblioteca: abrir carpeta / entrar |
| **◄ (transporte)** | Transporte | Note · ch 7 · nota 56 (0x38) · Gate | `9638` | `BrowseUp` ✅ | Biblioteca: subir un track |
| **► (transporte)** | Transporte | Note · ch 7 · nota 58 (0x3A) · Gate | `963A` | `BrowseDown` ✅ | Biblioteca: bajar un track |
| **GRID** | Transporte | Note · ch 5 · nota 22 (0x16) · Toggle | `9416` | `FX1Assign.SAMPLER` ✅ | Mandar el Beat FX 1 al **sampler** (latch) |
| **PLAY** | Transporte | Note · ch 5 · nota 71 (0x47) · Gate | `9447` | `FX1-1On` ✅ | Beat FX 1 ON/OFF (mismo que botón 1 de la página FX1) |
| **REC** | Transporte | Note · ch 6 · nota 71 (0x47) · Gate | `9547` | `FX2-1On` ⚠️ | Beat FX 2 ON/OFF (mismo que botón 1 de la página FX2) |
| **ERASE** | Transporte | Note · ch 7 · nota 105 (0x69) · Gate | `9669` | `SamplerCue` ✅ | Sampler a los audífonos (CUE) |
| **SHIFT** | Transporte | — | — | — | Reservado por Controller Editor (SHIFT+CONTROL = modo MIDI, SHIFT+◄► = plantilla) |

## 6. Knobs master (VOLUME · TEMPO · SWING)

| Knob | Controller Editor | Código | Función rekordbox | Acción |
|---|---|---|---|---|
| **SWING** | CC · ch 7 · nº 3 (0x03) · Absolute | `B603` | `SamplerVolume` ✅ | Volumen general del sampler |

## 7. Configuración en Controller Editor (paso a paso)

1. Abre **Controller Editor**, selecciona el MASCHINE (MK1) y crea/renombra la plantilla **REKORDBOX** (ya la tienes como `01 - REKORDBOX`).
2. Inspector → pestaña **Pages**: activa **Enable Pad Pages** y crea las 8 Pad Pages con nombres `A D1 CUE+FX`, `B D2 CUE+FX`, `C D1 JUMP+LOOP`, `D D2 JUMP+LOOP`, `E D1 FX2+DEL`, `F D2 FX2+DEL`, `G SAMPLER PLAY`, `H SAMPLER STOP`. Crea 4 Knob Pages: `FX1`, `FX2`, `FXSEL+MIX`, `CFX TYPE`.
3. **Pads** (en cada Pad Page): Type **Note** · Channel y Note según las tablas de la sección 3 · Mode **Gate** (Note On al golpear, Note Off al soltar — imprescindible para Pad FX momentáneo) · acción **Press** (presión) en **Off**.
4. **Botones** (globales y los 8 de cada Knob Page): Type **Note** · Mode **Gate** · Value 127. Excepción: los botones `FXnAssign.*` (botones 6-8 de las páginas FX1/FX2 y GRID) en modo **Toggle** (rekordbox trata la asignación de FX como un interruptor).
5. **Knobs**: Type **Control Change** · Channel/Number según tablas · Mode **Absolute** (rango 0-127) en todos.
6. **LEDs** (opcional, recomendado): en cada pad/botón pon *LED On* = **Remote/MIDI** para que rekordbox encienda hot cues cargados, samples sonando y FX activos (el CSV ya manda el mismo código por MIDI OUT).
7. En el Maschine: **SHIFT + CONTROL** entra al modo MIDI · **SHIFT + PAGE ◄ ►** elige plantilla · **PAGE ◄ ►** cambia página de knobs · **GROUP A–H** cambia capa de pads. No hace falta tener Controller Editor abierto; el servicio NI Hardware Agent carga la plantilla.

## 8. Importar en rekordbox

1. rekordbox en modo **PERFORMANCE** → botón **MIDI** (arriba a la derecha).
2. Dispositivo: *Maschine Controller* (en macOS puede aparecer como *Maschine Controller Virtual Input*). Si no aparece, cierra el software MASCHINE: no puede estar usando el controlador a la vez.
3. **IMPORT** → `Maschine_MK1_rekordbox.midi.csv`. rekordbox sobreescribe el mapeo del dispositivo y lo guarda al cerrar la ventana.
4. Prueba cada sección con **LEARN apagado**; la columna MIDI IN de la lista debe coincidir con el código de las tablas de este documento.

## 9. Ajustes recomendados dentro de rekordbox

- **PAD FX**: configura los bancos PAD FX 1 (Group A/B, pads 9-16) y PAD FX 2 (Group E/F, pads 1-8) con tus combinaciones (p. ej. Echo ½, Roll ⅛, Spiral 1, Filter LPF, Trans ¼, Reverb, Pitch, Vinyl Brake).
- **RELEASE FX** (NOTE REPEAT): elige el tipo en el panel FX1 (Vinyl Brake / Echo / Back Spin).
- **SAMPLER**: abre el panel SAMPLER en rekordbox → 16 slots por banco, 4 bancos (cámbialos desde la pantalla del sampler en rekordbox). Define por slot *one-shot* o *loop*; para loops usa la capa **H** para detenerlos. Sube el volumen del sampler con **SWING** antes de disparar (el encoder arranca en 0 al cargar la plantilla).
- **Beat FX multi/single**: los knobs 2-3 y botones 2-3 de las páginas FX solo actúan en modo *multi* (3 slots). En modo *single* usa knob 1 + botón 1 + beat ◄ ►.
- **Color FX**: elige el tipo con los botones 1-6 de la página 4 y la profundidad con los knobs 5-8 de la página 1. Como son encoders absolutos, **céntralos (valor 64 en el display) antes de activar un Color FX** o arrancarán desde el extremo.
- **Gain/EQ (página 3)**: sólo tiene sentido si mezclas dentro de rekordbox. Mismo aviso: lleva cada encoder a 64 antes de usarlo.

## 10. Verificación y problemas típicos

| Síntoma | Causa / solución |
|---|---|
| Nada responde | rekordbox no está en PERFORMANCE, el dispositivo seleccionado no es el Maschine, o el Maschine no está en modo MIDI (SHIFT+CONTROL). |
| Un pad/botón hace otra cosa | El display derecho del MK1 muestra el último evento (`EVENT: CH.x – NOTE – nn`); compáralo con la columna *Código* de este documento. |
| Pad FX / Release FX se queda pegado | El control no manda Note Off: en Controller Editor confirma Mode **Gate** (no Trigger/Toggle). Si tu versión manda Note Off como `8n` y rekordbox lo ignora, cambia ese control a Type **Control Change** (Gate, 127/0) y en el CSV sustituye `9nxx` por `Bnxx` en esa fila. |
| Navego la biblioteca y no avanza | ◄ / ► del transporte = BrowseUp / BrowseDown, LOOP = Forward (abrir carpeta). Antes pulsa STEP para ver la Browse View. |
| El FX se asigna y se desasigna solo | Los botones `FXnAssign.*` deben estar en **Toggle**, no Gate. |
| rekordbox rechaza el import | Borra las filas ⚠️ (sección *Deducidas/Reservados* y los `FX2-*`) y vuelve a importar; el resto son nombres oficiales de Pioneer. |
| Quiero velocidad en el sampler | rekordbox sólo acepta *Velocity Sampler* con pads que manden Note + CC (tipo `Value`); no está incluido. Se puede añadir usando la acción *Press* del pad como CC. |

## 11. Resumen de códigos (todas las filas funcionales del CSV)

| Código(s) MIDI | Función | Tipo | Dónde |
|---|---|---|---|
| `9638` | `BrowseUp` ✅ | Button | TRANSPORTE < - subir en la biblioteca |
| `963A` | `BrowseDown` ✅ | Button | TRANSPORTE > - bajar en la biblioteca |
| `9679` | `Forward` ✅ | Button | LOOP - abrir carpeta / entrar |
| `9646` `9647` `9648` `9649` | `Load` ✅ | Button | BROWSE = cargar en Deck 1 / SAMPLING = cargar en Deck 2 (doble clic = instant doubles) |
| `9665` | `Back` ✅ | Button | CONTROL - atras / cerrar carpeta |
| `967A` | `SwitchActiveWindow` ✅ | Button | STEP - BROWSE VIEW (navegador a pantalla completa) |
| `9636` | `PlayPausePreview` ✅ | Button | F1 - preview del track seleccionado |
| `9667` | `AddToTagList` ✅ | Button | F2 - agregar track a la Tag List |
| `900B` `910B` `920B` `930B` | `PlayPause` ✅ | Button | SCENE = Deck 1 / PATTERN = Deck 2 - Play/Pause |
| `900C` `910C` `920C` `930C` | `Cue` ✅ | Button | KEYBOARD = Deck 1 / NAVIGATE = Deck 2 - Cue |
| `9058` `9158` `9258` `9358` | `Sync` ✅ | Button | DUPLICATE = Deck 1 / SELECT = Deck 2 - Beat Sync |
| `9014` `9114` `9214` `9314` | `4BeatLoop` ✅ | Button | SOLO = Deck 1 / MUTE = Deck 2 - Auto loop 4 beats on/off |
| `9035` `9135` `9235` `9335` | `Quantize` ✅ | Button | Pagina de knobs 4 - Boton 7 = Deck 1 / Boton 8 = Deck 2 - Quantize |
| `B004` `B104` `B204` `B304` | `Gain` ✅ | KnobSlider | Pagina de knobs 3 - Knob 1 = Deck 1 / Knob 5 = Deck 2 - Gain (trim) |
| `B007` `B107` `B207` `B307` | `EQHigh` ✅ | KnobSlider | Pagina de knobs 3 - Knob 2 = Deck 1 / Knob 6 = Deck 2 - EQ High |
| `B00B` `B10B` `B20B` `B30B` | `EQMid` ✅ | KnobSlider | Pagina de knobs 3 - Knob 3 = Deck 1 / Knob 7 = Deck 2 - EQ Mid |
| `B00F` `B10F` `B20F` `B30F` | `EQLow` ✅ | KnobSlider | Pagina de knobs 3 - Knob 4 = Deck 1 / Knob 8 = Deck 2 - EQ Low |
| `B603` | `SamplerVolume` ✅ | KnobSlider | Knob SWING (master) - volumen del sampler |
| `9669` | `SamplerCue` ✅ | Button | ERASE - sampler a los audifonos (cue) |
| `B617` | `CFXParameterCH1` ✅ | KnobSlider | Pagina de knobs 1 - Knob 5 - Color FX canal 1 (centro = 64) |
| `B618` | `CFXParameterCH2` ✅ | KnobSlider | Pagina de knobs 1 - Knob 6 - Color FX canal 2 (centro = 64) |
| `B619` | `CFXParameterCH3` ✅ | KnobSlider | Pagina de knobs 1 - Knob 7 - Color FX canal 3 (centro = 64) |
| `B61A` | `CFXParameterCH4` ✅ | KnobSlider | Pagina de knobs 1 - Knob 8 - Color FX canal 4 (centro = 64) |
| `9600` | `CFX1On` ✅ | Button | Pagina de knobs 4 - Boton 1 - Color FX SPACE on/off |
| `9601` | `CFX2On` ✅ | Button | Pagina de knobs 4 - Boton 2 - Color FX D-ECHO on/off |
| `9602` | `CFX3On` ✅ | Button | Pagina de knobs 4 - Boton 3 - Color FX CRUSH on/off |
| `9603` | `CFX4On` ✅ | Button | Pagina de knobs 4 - Boton 4 - Color FX PITCH on/off |
| `9604` | `CFX5On` ✅ | Button | Pagina de knobs 4 - Boton 5 - Color FX NOISE on/off |
| `9605` | `CFX6On` ✅ | Button | Pagina de knobs 4 - Boton 6 - Color FX FILTER on/off |
| `B402` | `FX1-1` ✅ | KnobSlider | Pagina de knobs 1 - Knob 1 - FX1 slot 1 level/depth |
| `B403` | `FX1-2` ✅ | KnobSlider | Pagina de knobs 1 - Knob 2 - FX1 slot 2 (modo multi) |
| `B404` | `FX1-3` ✅ | KnobSlider | Pagina de knobs 1 - Knob 3 - FX1 slot 3 (modo multi) |
| `B405` | `FX1-1Select` ⚠️ | KnobSlider | Pagina de knobs 1 - Knob 4 - selector de efecto por knob (truco: Button->KnobSlider) |
| `9447` | `FX1-1On` ✅ | Button | Pagina de knobs 1 - Boton 1 (y PLAY) - FX1 slot 1 on/off |
| `9448` | `FX1-2On` ✅ | Button | Pagina de knobs 1 - Boton 2 - FX1 slot 2 on/off |
| `9449` | `FX1-3On` ✅ | Button | Pagina de knobs 1 - Boton 3 - FX1 slot 3 on/off |
| `944A` | `FX1BeatDown` ✅ | Button | Pagina de knobs 1 - Boton 4 - FX1 beat < |
| `944B` | `FX1BeatUp` ✅ | Button | Pagina de knobs 1 - Boton 5 - FX1 beat > |
| `9443` | `FX1ReleaseFXOn` ✅ | Button | NOTE REPEAT - Release FX (momentaneo) |
| `9410` | `FX1Assign.CH1` ✅ | Button | Pagina de knobs 1 - Boton 6 - asignar FX1 a CH1 (boton en modo Toggle) |
| `9411` | `FX1Assign.CH2` ✅ | Button | Pagina de knobs 1 - Boton 7 - asignar FX1 a CH2 (boton en modo Toggle) |
| `9414` | `FX1Assign.MASTER` ✅ | Button | Pagina de knobs 1 - Boton 8 - asignar FX1 a MASTER (boton en modo Toggle) |
| `9416` | `FX1Assign.SAMPLER` ✅ | Button | GRID - asignar FX1 a SAMPLER (boton en modo Toggle) |
| `9420` | `FX1-1Select.DELAY` ✅ | Button | seleccion directa de FX1: DELAY |
| `9421` | `FX1-1Select.ECHO` ✅ | Button | Pagina de knobs 3 - Boton 1 - seleccion directa de FX1: ECHO |
| `9422` | `FX1-1Select.LOWCUTECHO` ✅ | Button | seleccion directa de FX1: LOWCUTECHO |
| `9423` | `FX1-1Select.SPIRAL` ✅ | Button | Pagina de knobs 3 - Boton 2 - seleccion directa de FX1: SPIRAL |
| `9424` | `FX1-1Select.HELIX` ✅ | Button | seleccion directa de FX1: HELIX |
| `9425` | `FX1-1Select.REVERB` ✅ | Button | Pagina de knobs 3 - Boton 3 - seleccion directa de FX1: REVERB |
| `9426` | `FX1-1Select.FLANGER` ✅ | Button | Pagina de knobs 3 - Boton 4 - seleccion directa de FX1: FLANGER |
| `9427` | `FX1-1Select.PHASER` ✅ | Button | Pagina de knobs 3 - Boton 5 - seleccion directa de FX1: PHASER |
| `9428` | `FX1-1Select.FILTER` ✅ | Button | Pagina de knobs 3 - Boton 6 - seleccion directa de FX1: FILTER |
| `9429` | `FX1-1Select.TRANS` ✅ | Button | Pagina de knobs 3 - Boton 8 - seleccion directa de FX1: TRANS |
| `942A` | `FX1-1Select.PITCH` ✅ | Button | seleccion directa de FX1: PITCH |
| `942B` | `FX1-1Select.ROLL` ✅ | Button | Pagina de knobs 3 - Boton 7 - seleccion directa de FX1: ROLL |
| `942C` | `FX1-1Select.MOBIUSSAW` ✅ | Button | seleccion directa de FX1: MOBIUSSAW |
| `942D` | `FX1-1Select.MOBIUSTRI` ✅ | Button | seleccion directa de FX1: MOBIUSTRI |
| `B502` | `FX2-1` ⚠️ | KnobSlider | Pagina de knobs 2 - Knob 1 - FX2 slot 1 level/depth |
| `B503` | `FX2-2` ⚠️ | KnobSlider | Pagina de knobs 2 - Knob 2 - FX2 slot 2 (modo multi) |
| `B504` | `FX2-3` ⚠️ | KnobSlider | Pagina de knobs 2 - Knob 3 - FX2 slot 3 (modo multi) |
| `B505` | `FX2-1Select` ⚠️ | KnobSlider | Pagina de knobs 2 - Knob 4 - selector de efecto por knob (truco: Button->KnobSlider) |
| `9547` | `FX2-1On` ⚠️ | Button | Pagina de knobs 2 - Boton 1 (y REC) - FX2 slot 1 on/off |
| `9548` | `FX2-2On` ⚠️ | Button | Pagina de knobs 2 - Boton 2 - FX2 slot 2 on/off |
| `9549` | `FX2-3On` ⚠️ | Button | Pagina de knobs 2 - Boton 3 - FX2 slot 3 on/off |
| `954A` | `FX2BeatDown` ⚠️ | Button | Pagina de knobs 2 - Boton 4 - FX2 beat < |
| `954B` | `FX2BeatUp` ⚠️ | Button | Pagina de knobs 2 - Boton 5 - FX2 beat > |
| `9543` | `FX2ReleaseFXOn` ⚠️ | Button | RESERVADO - Release FX del FX2 |
| `9510` | `FX2Assign.CH1` ⚠️ | Button | Pagina de knobs 2 - Boton 6 - asignar FX2 a CH1 (boton en modo Toggle) |
| `9511` | `FX2Assign.CH2` ⚠️ | Button | Pagina de knobs 2 - Boton 7 - asignar FX2 a CH2 (boton en modo Toggle) |
| `9514` | `FX2Assign.MASTER` ⚠️ | Button | Pagina de knobs 2 - Boton 8 - asignar FX2 a MASTER (boton en modo Toggle) |
| `9516` | `FX2Assign.SAMPLER` ⚠️ | Button | RESERVADO - asignar FX2 a SAMPLER (boton en modo Toggle) |
| `9520` | `FX2-1Select.DELAY` ⚠️ | Button | seleccion directa de FX2: DELAY |
| `9521` | `FX2-1Select.ECHO` ⚠️ | Button | seleccion directa de FX2: ECHO |
| `9522` | `FX2-1Select.LOWCUTECHO` ⚠️ | Button | seleccion directa de FX2: LOWCUTECHO |
| `9523` | `FX2-1Select.SPIRAL` ⚠️ | Button | seleccion directa de FX2: SPIRAL |
| `9524` | `FX2-1Select.HELIX` ⚠️ | Button | seleccion directa de FX2: HELIX |
| `9525` | `FX2-1Select.REVERB` ⚠️ | Button | seleccion directa de FX2: REVERB |
| `9526` | `FX2-1Select.FLANGER` ⚠️ | Button | seleccion directa de FX2: FLANGER |
| `9527` | `FX2-1Select.PHASER` ⚠️ | Button | seleccion directa de FX2: PHASER |
| `9528` | `FX2-1Select.FILTER` ⚠️ | Button | seleccion directa de FX2: FILTER |
| `9529` | `FX2-1Select.TRANS` ⚠️ | Button | seleccion directa de FX2: TRANS |
| `952A` | `FX2-1Select.PITCH` ⚠️ | Button | seleccion directa de FX2: PITCH |
| `952B` | `FX2-1Select.ROLL` ⚠️ | Button | seleccion directa de FX2: ROLL |
| `952C` | `FX2-1Select.MOBIUSSAW` ⚠️ | Button | seleccion directa de FX2: MOBIUSSAW |
| `952D` | `FX2-1Select.MOBIUSTRI` ⚠️ | Button | seleccion directa de FX2: MOBIUSTRI |
| `9700` `9900` `9B00` `9D00` | `PAD1_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 1 - HOT CUE 1 |
| `9800` `9A00` `9C00` `9E00` | `PAD1_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 9 - BORRAR HOT CUE 1 |
| `9701` `9901` `9B01` `9D01` | `PAD2_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 2 - HOT CUE 2 |
| `9801` `9A01` `9C01` `9E01` | `PAD2_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 10 - BORRAR HOT CUE 2 |
| `9702` `9902` `9B02` `9D02` | `PAD3_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 3 - HOT CUE 3 |
| `9802` `9A02` `9C02` `9E02` | `PAD3_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 11 - BORRAR HOT CUE 3 |
| `9703` `9903` `9B03` `9D03` | `PAD4_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 4 - HOT CUE 4 |
| `9803` `9A03` `9C03` `9E03` | `PAD4_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 12 - BORRAR HOT CUE 4 |
| `9704` `9904` `9B04` `9D04` | `PAD5_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 5 - HOT CUE 5 |
| `9804` `9A04` `9C04` `9E04` | `PAD5_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 13 - BORRAR HOT CUE 5 |
| `9705` `9905` `9B05` `9D05` | `PAD6_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 6 - HOT CUE 6 |
| `9805` `9A05` `9C05` `9E05` | `PAD6_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 14 - BORRAR HOT CUE 6 |
| `9706` `9906` `9B06` `9D06` | `PAD7_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 7 - HOT CUE 7 |
| `9806` `9A06` `9C06` `9E06` | `PAD7_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 15 - BORRAR HOT CUE 7 |
| `9707` `9907` `9B07` `9D07` | `PAD8_HotCue` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 8 - HOT CUE 8 |
| `9807` `9A07` `9C07` `9E07` | `PAD8_HotCue+Shift` ✅ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 16 - BORRAR HOT CUE 8 |
| `9710` `9910` `9B10` `9D10` | `PAD1_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 9 - PAD FX 1 slot 1 (momentaneo) |
| `9711` `9911` `9B11` `9D11` | `PAD2_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 10 - PAD FX 1 slot 2 (momentaneo) |
| `9712` `9912` `9B12` `9D12` | `PAD3_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 11 - PAD FX 1 slot 3 (momentaneo) |
| `9713` `9913` `9B13` `9D13` | `PAD4_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 12 - PAD FX 1 slot 4 (momentaneo) |
| `9714` `9914` `9B14` `9D14` | `PAD5_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 13 - PAD FX 1 slot 5 (momentaneo) |
| `9715` `9915` `9B15` `9D15` | `PAD6_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 14 - PAD FX 1 slot 6 (momentaneo) |
| `9716` `9916` `9B16` `9D16` | `PAD7_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 15 - PAD FX 1 slot 7 (momentaneo) |
| `9717` `9917` `9B17` `9D17` | `PAD8_PadFx1` ✅ | Pad | Grupo A (Deck 1) / B (Deck 2) - Pad 16 - PAD FX 1 slot 8 (momentaneo) |
| `9720` `9920` `9B20` `9D20` | `PAD1_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 1 - BEAT JUMP <1 (segun rango activo) |
| `9721` `9921` `9B21` `9D21` | `PAD2_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 2 - BEAT JUMP >1 (segun rango activo) |
| `9722` `9922` `9B22` `9D22` | `PAD3_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 3 - BEAT JUMP <2 (segun rango activo) |
| `9723` `9923` `9B23` `9D23` | `PAD4_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 4 - BEAT JUMP >2 (segun rango activo) |
| `9724` `9924` `9B24` `9D24` | `PAD5_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 5 - BEAT JUMP <4 (segun rango activo) |
| `9725` `9925` `9B25` `9D25` | `PAD6_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 6 - BEAT JUMP >4 (segun rango activo) |
| `9726` `9926` `9B26` `9D26` | `PAD7_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 7 - BEAT JUMP <8 (segun rango activo) |
| `9727` `9927` `9B27` `9D27` | `PAD8_BeatJump` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 8 - BEAT JUMP >8 (segun rango activo) |
| `9760` `9960` `9B60` `9D60` | `PAD1_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 9 - BEAT LOOP slot 1 (segun rango activo) |
| `9761` `9961` `9B61` `9D61` | `PAD2_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 10 - BEAT LOOP slot 2 (segun rango activo) |
| `9762` `9962` `9B62` `9D62` | `PAD3_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 11 - BEAT LOOP slot 3 (segun rango activo) |
| `9763` `9963` `9B63` `9D63` | `PAD4_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 12 - BEAT LOOP slot 4 (segun rango activo) |
| `9764` `9964` `9B64` `9D64` | `PAD5_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 13 - BEAT LOOP slot 5 (segun rango activo) |
| `9765` `9965` `9B65` `9D65` | `PAD6_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 14 - BEAT LOOP slot 6 (segun rango activo) |
| `9766` `9966` `9B66` `9D66` | `PAD7_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 15 - BEAT LOOP slot 7 (segun rango activo) |
| `9767` `9967` `9B67` `9D67` | `PAD8_BeatLoop` ✅ | Pad | Grupo C (Deck 1) / D (Deck 2) - Pad 16 - BEAT LOOP slot 8 (segun rango activo) |
| `9750` `9950` `9B50` `9D50` | `PAD1_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 1 - PAD FX 2 slot 1 (momentaneo) |
| `9751` `9951` `9B51` `9D51` | `PAD2_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 2 - PAD FX 2 slot 2 (momentaneo) |
| `9752` `9952` `9B52` `9D52` | `PAD3_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 3 - PAD FX 2 slot 3 (momentaneo) |
| `9753` `9953` `9B53` `9D53` | `PAD4_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 4 - PAD FX 2 slot 4 (momentaneo) |
| `9754` `9954` `9B54` `9D54` | `PAD5_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 5 - PAD FX 2 slot 5 (momentaneo) |
| `9755` `9955` `9B55` `9D55` | `PAD6_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 6 - PAD FX 2 slot 6 (momentaneo) |
| `9756` `9956` `9B56` `9D56` | `PAD7_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 7 - PAD FX 2 slot 7 (momentaneo) |
| `9757` `9957` `9B57` `9D57` | `PAD8_PadFx2` ⚠️ | Pad | Grupo E (Deck 1) / F (Deck 2) - Pad 8 - PAD FX 2 slot 8 (momentaneo) |
| `9730` `9930` `9B30` `9D30` | `PAD1_Sampler` ✅ | Pad | Grupo G - Pad 1 - SAMPLER slot 1 play (banco activo) |
| `9731` `9931` `9B31` `9D31` | `PAD2_Sampler` ✅ | Pad | Grupo G - Pad 2 - SAMPLER slot 2 play (banco activo) |
| `9732` `9932` `9B32` `9D32` | `PAD3_Sampler` ✅ | Pad | Grupo G - Pad 3 - SAMPLER slot 3 play (banco activo) |
| `9733` `9933` `9B33` `9D33` | `PAD4_Sampler` ✅ | Pad | Grupo G - Pad 4 - SAMPLER slot 4 play (banco activo) |
| `9734` `9934` `9B34` `9D34` | `PAD5_Sampler` ✅ | Pad | Grupo G - Pad 5 - SAMPLER slot 5 play (banco activo) |
| `9735` `9935` `9B35` `9D35` | `PAD6_Sampler` ✅ | Pad | Grupo G - Pad 6 - SAMPLER slot 6 play (banco activo) |
| `9736` `9936` `9B36` `9D36` | `PAD7_Sampler` ✅ | Pad | Grupo G - Pad 7 - SAMPLER slot 7 play (banco activo) |
| `9737` `9937` `9B37` `9D37` | `PAD8_Sampler` ✅ | Pad | Grupo G - Pad 8 - SAMPLER slot 8 play (banco activo) |
| `9738` `9938` `9B38` `9D38` | `PAD9_Sampler` ⚠️ | Pad | Grupo G - Pad 9 - SAMPLER slot 9 play (banco activo) |
| `9739` `9939` `9B39` `9D39` | `PAD10_Sampler` ⚠️ | Pad | Grupo G - Pad 10 - SAMPLER slot 10 play (banco activo) |
| `973A` `993A` `9B3A` `9D3A` | `PAD11_Sampler` ⚠️ | Pad | Grupo G - Pad 11 - SAMPLER slot 11 play (banco activo) |
| `973B` `993B` `9B3B` `9D3B` | `PAD12_Sampler` ⚠️ | Pad | Grupo G - Pad 12 - SAMPLER slot 12 play (banco activo) |
| `973C` `993C` `9B3C` `9D3C` | `PAD13_Sampler` ⚠️ | Pad | Grupo G - Pad 13 - SAMPLER slot 13 play (banco activo) |
| `973D` `993D` `9B3D` `9D3D` | `PAD14_Sampler` ⚠️ | Pad | Grupo G - Pad 14 - SAMPLER slot 14 play (banco activo) |
| `973E` `993E` `9B3E` `9D3E` | `PAD15_Sampler` ⚠️ | Pad | Grupo G - Pad 15 - SAMPLER slot 15 play (banco activo) |
| `973F` `993F` `9B3F` `9D3F` | `PAD16_Sampler` ⚠️ | Pad | Grupo G - Pad 16 - SAMPLER slot 16 play (banco activo) |
| `9830` `9A30` `9C30` `9E30` | `PAD1_Sampler+Shift` ✅ | Pad | Grupo H - Pad 1 - SAMPLER slot 1 stop |
| `9831` `9A31` `9C31` `9E31` | `PAD2_Sampler+Shift` ✅ | Pad | Grupo H - Pad 2 - SAMPLER slot 2 stop |
| `9832` `9A32` `9C32` `9E32` | `PAD3_Sampler+Shift` ✅ | Pad | Grupo H - Pad 3 - SAMPLER slot 3 stop |
| `9833` `9A33` `9C33` `9E33` | `PAD4_Sampler+Shift` ✅ | Pad | Grupo H - Pad 4 - SAMPLER slot 4 stop |
| `9834` `9A34` `9C34` `9E34` | `PAD5_Sampler+Shift` ✅ | Pad | Grupo H - Pad 5 - SAMPLER slot 5 stop |
| `9835` `9A35` `9C35` `9E35` | `PAD6_Sampler+Shift` ✅ | Pad | Grupo H - Pad 6 - SAMPLER slot 6 stop |
| `9836` `9A36` `9C36` `9E36` | `PAD7_Sampler+Shift` ✅ | Pad | Grupo H - Pad 7 - SAMPLER slot 7 stop |
| `9837` `9A37` `9C37` `9E37` | `PAD8_Sampler+Shift` ✅ | Pad | Grupo H - Pad 8 - SAMPLER slot 8 stop |
| `9838` `9A38` `9C38` `9E38` | `PAD9_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 9 - SAMPLER slot 9 stop |
| `9839` `9A39` `9C39` `9E39` | `PAD10_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 10 - SAMPLER slot 10 stop |
| `983A` `9A3A` `9C3A` `9E3A` | `PAD11_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 11 - SAMPLER slot 11 stop |
| `983B` `9A3B` `9C3B` `9E3B` | `PAD12_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 12 - SAMPLER slot 12 stop |
| `983C` `9A3C` `9C3C` `9E3C` | `PAD13_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 13 - SAMPLER slot 13 stop |
| `983D` `9A3D` `9C3D` `9E3D` | `PAD14_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 14 - SAMPLER slot 14 stop |
| `983E` `9A3E` `9C3E` `9E3E` | `PAD15_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 15 - SAMPLER slot 15 stop |
| `983F` `9A3F` `9C3F` `9E3F` | `PAD16_Sampler+Shift` ⚠️ | Pad | Grupo H - Pad 16 - SAMPLER slot 16 stop |
| `9708` `9908` `9B08` `9D08` | `PAD9_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 9 |
| `9709` `9909` `9B09` `9D09` | `PAD10_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 10 |
| `970A` `990A` `9B0A` `9D0A` | `PAD11_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 11 |
| `970B` `990B` `9B0B` `9D0B` | `PAD12_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 12 |
| `970C` `990C` `9B0C` `9D0C` | `PAD13_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 13 |
| `970D` `990D` `9B0D` `9D0D` | `PAD14_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 14 |
| `970E` `990E` `9B0E` `9D0E` | `PAD15_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 15 |
| `970F` `990F` `9B0F` `9D0F` | `PAD16_HotCue` ⚠️ | Pad | RESERVADO - HOT CUE 16 |
| `9718` `9918` `9B18` `9D18` | `PAD9_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 9 |
| `9719` `9919` `9B19` `9D19` | `PAD10_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 10 |
| `971A` `991A` `9B1A` `9D1A` | `PAD11_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 11 |
| `971B` `991B` `9B1B` `9D1B` | `PAD12_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 12 |
| `971C` `991C` `9B1C` `9D1C` | `PAD13_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 13 |
| `971D` `991D` `9B1D` `9D1D` | `PAD14_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 14 |
| `971E` `991E` `9B1E` `9D1E` | `PAD15_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 15 |
| `971F` `991F` `9B1F` `9D1F` | `PAD16_PadFx1` ⚠️ | Pad | RESERVADO - PAD FX 1 slot 16 |
| `9740` `9940` `9B40` `9D40` | `PAD1_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 1 |
| `9741` `9941` `9B41` `9D41` | `PAD2_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 2 |
| `9742` `9942` `9B42` `9D42` | `PAD3_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 3 |
| `9743` `9943` `9B43` `9D43` | `PAD4_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 4 |
| `9744` `9944` `9B44` `9D44` | `PAD5_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 5 |
| `9745` `9945` `9B45` `9D45` | `PAD6_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 6 |
| `9746` `9946` `9B46` `9D46` | `PAD7_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 7 |
| `9747` `9947` `9B47` `9D47` | `PAD8_Keyboard` ✅ | Pad | RESERVADO - KEYBOARD pad 8 |
| `9770` `9970` `9B70` `9D70` | `PAD1_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 1 |
| `9771` `9971` `9B71` `9D71` | `PAD2_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 2 |
| `9772` `9972` `9B72` `9D72` | `PAD3_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 3 |
| `9773` `9973` `9B73` `9D73` | `PAD4_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 4 |
| `9774` `9974` `9B74` `9D74` | `PAD5_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 5 |
| `9775` `9975` `9B75` `9D75` | `PAD6_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 6 |
| `9776` `9976` `9B76` `9D76` | `PAD7_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 7 |
| `9777` `9977` `9B77` `9D77` | `PAD8_KeyShift` ✅ | Pad | RESERVADO - KEY SHIFT pad 8 |

---
Fuentes del formato: mapeos oficiales `DDJ-FLX10.midi.csv` / `DDJ-GRV6.midi.csv` (rekordbox 7), *MIDI LEARN Operation Guide* (AlphaTheta), *Controller Editor Manual* (Native Instruments, cap. MASCHINE: Pad Pages via GROUP, Knob Pages via PAGE, SHIFT y PAGE no asignables), DJ TechTools *Hacking Rekordbox FX* (comandos `FX1-1Select.NAME`, `FX1Assign.*`, truco KnobSlider).
