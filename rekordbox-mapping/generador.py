#!/usr/bin/env python3
"""Generates the rekordbox MIDI mapping CSV + Markdown docs for MASCHINE MK1.

Single source of truth: the HW list below describes what every physical control
of the Maschine MK1 sends (per Controller Editor page) and which rekordbox
function it triggers. The CSV rows are derived from the same constants.
"""
import csv, io, os, re

OUT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(OUT, "Maschine_MK1_rekordbox.midi.csv")
MD_PATH = os.path.join(OUT, "Maschine_MK1_rekordbox_MAPA.md")

# ---------------------------------------------------------------- channel plan
# 0-based MIDI channels (hex nibble)        1-based (Controller Editor)
CH_D1, CH_D2, CH_D3, CH_D4 = 0, 1, 2, 3  # deck buttons/knobs      ch 1-4
CH_FX1, CH_FX2 = 4, 5                    # Beat FX 1 / 2           ch 5-6
CH_GLB = 6                               # global / browser / mixer ch 7
CH_PAD = {1: 7, 2: 9, 3: 11, 4: 13}      # pads per deck (normal)   ch 8/10/12/14
CH_PADS = {1: 8, 2: 10, 3: 12, 4: 14}    # pads per deck ("shift")  ch 9/11/13/15

NOTE, CC = 0x90, 0xB0

def code(status, ch, data):
    return f"{status | ch:02X}{data:02X}"

def ch1(ch):  # 1-based channel for Controller Editor
    return ch + 1

# ------------------------------------------------------------ rekordbox rows
# Each row: 15 columns exactly like Pioneer's official files.
ROWS = []  # list of lists (15 cols) or None for empty separator
VERIFIED = {}  # function -> True (seen in official Pioneer CSV) / False (deduced)

def sep():
    ROWS.append([""] * 15)

def section(name):
    ROWS.append([f"# {name}"] + [""] * 14)

def row(fn, typ, inp="", decks=("", "", "", ""), out="", odecks=("", "", "", ""),
        opt="", cm="", label=None, verified=True):
    label = fn if label is None else label
    d = [str(x) for x in decks]
    o = [str(x) for x in odecks]
    assert "," not in cm and all(ord(c) < 128 for c in cm), cm
    ROWS.append([fn, label, typ, inp] + d + [out] + o + [opt, cm])
    VERIFIED[fn] = verified

DECKS = (CH_D1, CH_D2, CH_D3, CH_D4)
PADD = (CH_PAD[1], CH_PAD[2], CH_PAD[3], CH_PAD[4])
PADS = (CH_PADS[1], CH_PADS[2], CH_PADS[3], CH_PADS[4])

# -------- Browser (global, ch 7)
section("Browser")
row("BrowseUp", "Button", code(NOTE, CH_GLB, 0x38), cm="TRANSPORTE < - subir en la biblioteca")
row("BrowseDown", "Button", code(NOTE, CH_GLB, 0x3A), cm="TRANSPORTE > - bajar en la biblioteca")
row("Forward", "Button", code(NOTE, CH_GLB, 0x79), cm="LOOP - abrir carpeta / entrar")
row("Load", "Button", "", (code(NOTE, CH_GLB, 0x46), code(NOTE, CH_GLB, 0x47),
                           code(NOTE, CH_GLB, 0x48), code(NOTE, CH_GLB, 0x49)),
    cm="BROWSE = cargar en Deck 1 / SAMPLING = cargar en Deck 2 (doble clic = instant doubles)")
row("Back", "Button", code(NOTE, CH_GLB, 0x65), cm="CONTROL - atras / cerrar carpeta")
row("SwitchActiveWindow", "Button", code(NOTE, CH_GLB, 0x7A), cm="STEP - BROWSE VIEW (navegador a pantalla completa)")
row("PlayPausePreview", "Button", code(NOTE, CH_GLB, 0x36), cm="F1 - preview del track seleccionado")
row("AddToTagList", "Button", code(NOTE, CH_GLB, 0x67), cm="F2 - agregar track a la Tag List")
sep()

# -------- Deck (ch 1-4 with offsets 0..3)
section("Deck")
row("PlayPause", "Button", code(NOTE, 0, 0x0B), DECKS, code(NOTE, 0, 0x0B), DECKS,
    "Fast;Priority=50", "SCENE = Deck 1 / PATTERN = Deck 2 - Play/Pause")
row("Cue", "Button", code(NOTE, 0, 0x0C), DECKS, code(NOTE, 0, 0x0C), DECKS,
    "Fast;Priority=50", "KEYBOARD = Deck 1 / NAVIGATE = Deck 2 - Cue")
row("Sync", "Button", code(NOTE, 0, 0x58), DECKS, code(NOTE, 0, 0x58), DECKS,
    "Blink=600", "DUPLICATE = Deck 1 / SELECT = Deck 2 - Beat Sync")
row("4BeatLoop", "Button", code(NOTE, 0, 0x14), DECKS, code(NOTE, 0, 0x14), DECKS,
    "Fast", "SOLO = Deck 1 / MUTE = Deck 2 - Auto loop 4 beats on/off")
row("Quantize", "Button", code(NOTE, 0, 0x35), DECKS, code(NOTE, 0, 0x35), DECKS,
    "", "Pagina de knobs 4 - Boton 7 = Deck 1 / Boton 8 = Deck 2 - Quantize")
sep()

# -------- Mixer
section("Mixer")
row("Gain", "KnobSlider", code(CC, 0, 0x04), DECKS, opt="Fast",
    cm="Pagina de knobs 3 - Knob 1 = Deck 1 / Knob 5 = Deck 2 - Gain (trim)")
row("EQHigh", "KnobSlider", code(CC, 0, 0x07), DECKS, opt="Fast",
    cm="Pagina de knobs 3 - Knob 2 = Deck 1 / Knob 6 = Deck 2 - EQ High")
row("EQMid", "KnobSlider", code(CC, 0, 0x0B), DECKS, opt="Fast",
    cm="Pagina de knobs 3 - Knob 3 = Deck 1 / Knob 7 = Deck 2 - EQ Mid")
row("EQLow", "KnobSlider", code(CC, 0, 0x0F), DECKS, opt="Fast",
    cm="Pagina de knobs 3 - Knob 4 = Deck 1 / Knob 8 = Deck 2 - EQ Low")
row("SamplerVolume", "KnobSlider", code(CC, CH_GLB, 0x03),
    cm="Knob SWING (master) - volumen del sampler")
row("SamplerCue", "Button", code(NOTE, CH_GLB, 0x69), out=code(NOTE, CH_GLB, 0x69),
    cm="ERASE - sampler a los audifonos (cue)")
sep()

# -------- Sound Color FX
section("SoundColorFX")
CFX_KNOB = {}
for n, ccn in zip(range(1, 5), (0x17, 0x18, 0x19, 0x1A)):
    c = code(CC, CH_GLB, ccn)
    CFX_KNOB[n] = c
    row(f"CFXParameterCH{n}", "KnobSlider", c, opt="Fast",
        cm=f"Pagina de knobs 1 - Knob {4 + n} - Color FX canal {n} (centro = 64)")
CFX_NAMES = ["SPACE", "D-ECHO", "CRUSH", "PITCH", "NOISE", "FILTER"]
CFX_BTN = {}
for n, name in enumerate(CFX_NAMES, start=1):
    c = code(NOTE, CH_GLB, n - 1)
    CFX_BTN[n] = c
    row(f"CFX{n}On", "Button", c, out=c, opt="Fast",
        cm=f"Pagina de knobs 4 - Boton {n} - Color FX {name} on/off")
sep()

# -------- Beat FX 1 / 2
FX_SELECT = [  # (name, data byte) exactly as in DDJ-GRV6
    ("DELAY", 0x20), ("ECHO", 0x21), ("LOWCUTECHO", 0x22), ("SPIRAL", 0x23),
    ("HELIX", 0x24), ("REVERB", 0x25), ("FLANGER", 0x26), ("PHASER", 0x27),
    ("FILTER", 0x28), ("TRANS", 0x29), ("PITCH", 0x2A), ("ROLL", 0x2B),
    ("MOBIUSSAW", 0x2C), ("MOBIUSTRI", 0x2D),
]
FX_SEL_ON_BUTTONS = ["ECHO", "SPIRAL", "REVERB", "FLANGER", "PHASER", "FILTER", "ROLL", "TRANS"]

def fx_unit(u, ch, verified):
    section(f"Effect FX{u}")
    kp = u  # knob page number
    row(f"FX{u}-1", "KnobSlider", code(CC, ch, 0x02), cm=f"Pagina de knobs {kp} - Knob 1 - FX{u} slot 1 level/depth", verified=verified)
    row(f"FX{u}-2", "KnobSlider", code(CC, ch, 0x03), cm=f"Pagina de knobs {kp} - Knob 2 - FX{u} slot 2 (modo multi)", verified=verified)
    row(f"FX{u}-3", "KnobSlider", code(CC, ch, 0x04), cm=f"Pagina de knobs {kp} - Knob 3 - FX{u} slot 3 (modo multi)", verified=verified)
    row(f"FX{u}-1Select", "KnobSlider", code(CC, ch, 0x05),
        cm=f"Pagina de knobs {kp} - Knob 4 - selector de efecto por knob (truco: Button->KnobSlider)", verified=False)
    on1 = code(NOTE, ch, 0x47)
    row(f"FX{u}-1On", "Button", on1, out=on1,
        cm=f"Pagina de knobs {kp} - Boton 1 (y {'PLAY' if u == 1 else 'REC'}) - FX{u} slot 1 on/off", verified=verified)
    on2 = code(NOTE, ch, 0x48)
    row(f"FX{u}-2On", "Button", on2, out=on2, cm=f"Pagina de knobs {kp} - Boton 2 - FX{u} slot 2 on/off", verified=verified)
    on3 = code(NOTE, ch, 0x49)
    row(f"FX{u}-3On", "Button", on3, out=on3, cm=f"Pagina de knobs {kp} - Boton 3 - FX{u} slot 3 on/off", verified=verified)
    row(f"FX{u}BeatDown", "Button", code(NOTE, ch, 0x4A), out=code(NOTE, ch, 0x4A),
        cm=f"Pagina de knobs {kp} - Boton 4 - FX{u} beat <", verified=verified)
    row(f"FX{u}BeatUp", "Button", code(NOTE, ch, 0x4B), out=code(NOTE, ch, 0x4B),
        cm=f"Pagina de knobs {kp} - Boton 5 - FX{u} beat >", verified=verified)
    rel = code(NOTE, ch, 0x43)
    row(f"FX{u}ReleaseFXOn", "Button", rel, out=rel, opt="Fast",
        cm=("NOTE REPEAT - Release FX (momentaneo)" if u == 1 else "RESERVADO - Release FX del FX2"),
        verified=verified)
    for name, data, hw in (("CH1", 0x10, f"Pagina de knobs {kp} - Boton 6"),
                           ("CH2", 0x11, f"Pagina de knobs {kp} - Boton 7"),
                           ("MASTER", 0x14, f"Pagina de knobs {kp} - Boton 8"),
                           ("SAMPLER", 0x16, "GRID" if u == 1 else "RESERVADO")):
        row(f"FX{u}Assign.{name}", "Button", code(NOTE, ch, data), label="",
            cm=f"{hw} - asignar FX{u} a {name} (boton en modo Toggle)", verified=verified)
    for name, data in FX_SELECT:
        hw = ""
        if u == 1 and name in FX_SEL_ON_BUTTONS:
            hw = f"Pagina de knobs 3 - Boton {FX_SEL_ON_BUTTONS.index(name) + 1} - "
        row(f"FX{u}-1Select.{name}", "Button", code(NOTE, ch, data), label=name,
            cm=f"{hw}seleccion directa de FX{u}: {name}", verified=verified)
    sep()

fx_unit(1, CH_FX1, True)
fx_unit(2, CH_FX2, False)

# -------- Performance pads
# Pioneer note layout per pad mode (data byte = base + pad-1)
PAD_BASE = {"HotCue": 0x00, "PadFx1": 0x10, "BeatJump": 0x20, "Sampler": 0x30,
            "Keyboard": 0x40, "PadFx2": 0x50, "BeatLoop": 0x60, "KeyShift": 0x70}
BJ = ["<1", ">1", "<2", ">2", "<4", ">4", "<8", ">8"]

section("Performance Pads")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["HotCue"] + p - 1)
    row(f"PAD{p}_HotCue", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo A (Deck 1) / B (Deck 2) - Pad {p} - HOT CUE {p}")
    row(f"PAD{p}_HotCue+Shift", "Pad", c, PADS, c, PADS, "Fast",
        f"Grupo E (Deck 1) / F (Deck 2) - Pad {p + 8} - BORRAR HOT CUE {p}")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["PadFx1"] + p - 1)
    row(f"PAD{p}_PadFx1", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo A (Deck 1) / B (Deck 2) - Pad {p + 8} - PAD FX 1 slot {p} (momentaneo)")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["BeatJump"] + p - 1)
    row(f"PAD{p}_BeatJump", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo C (Deck 1) / D (Deck 2) - Pad {p} - BEAT JUMP {BJ[p - 1]} (segun rango activo)")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["BeatLoop"] + p - 1)
    row(f"PAD{p}_BeatLoop", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo C (Deck 1) / D (Deck 2) - Pad {p + 8} - BEAT LOOP slot {p} (segun rango activo)")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["PadFx2"] + p - 1)
    row(f"PAD{p}_PadFx2", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo E (Deck 1) / F (Deck 2) - Pad {p} - PAD FX 2 slot {p} (momentaneo)", verified=False)
sep()

section("Sampler Pads")
for p in range(1, 17):
    c = code(NOTE, 0, PAD_BASE["Sampler"] + p - 1)
    row(f"PAD{p}_Sampler", "Pad", c, PADD, c, PADD, "Fast",
        f"Grupo G - Pad {p} - SAMPLER slot {p} play (banco activo)", verified=(p <= 8))
for p in range(1, 17):
    c = code(NOTE, 0, PAD_BASE["Sampler"] + p - 1)
    row(f"PAD{p}_Sampler+Shift", "Pad", c, PADS, c, PADS, "Fast",
        f"Grupo H - Pad {p} - SAMPLER slot {p} stop", verified=(p <= 8))
sep()

section("Reservados - codigos listos pero sin asignar en la plantilla")
for p in range(9, 17):
    c = code(NOTE, 0, PAD_BASE["HotCue"] + p - 1)
    row(f"PAD{p}_HotCue", "Pad", c, PADD, c, PADD, "Fast", f"RESERVADO - HOT CUE {p}", verified=False)
for p in range(9, 17):
    c = code(NOTE, 0, PAD_BASE["PadFx1"] + p - 1)
    row(f"PAD{p}_PadFx1", "Pad", c, PADD, c, PADD, "Fast", f"RESERVADO - PAD FX 1 slot {p}", verified=False)
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["Keyboard"] + p - 1)
    row(f"PAD{p}_Keyboard", "Pad", c, PADD, c, PADD, "Fast", f"RESERVADO - KEYBOARD pad {p}")
for p in range(1, 9):
    c = code(NOTE, 0, PAD_BASE["KeyShift"] + p - 1)
    row(f"PAD{p}_KeyShift", "Pad", c, PADD, c, PADD, "Fast", f"RESERVADO - KEY SHIFT pad {p}")

# ---------------------------------------------------------------- CSV output
def write_csv():
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_NONE, escapechar="\\")
    w.writerow(["@file", "1", "Maschine Controller"])
    w.writerow("#name,function,type,input,deck1,deck2,deck3,deck4,output,deck1,deck2,deck3,deck4,option,comment".split(","))
    w.writerow([""] * 15)
    for r in ROWS:
        assert len(r) == 15, r
        w.writerow(r)
    data = buf.getvalue()
    data.encode("ascii")  # must be pure ASCII like Pioneer's files
    with open(CSV_PATH, "w", newline="", encoding="ascii") as f:
        f.write(data)
    return data

# ------------------------------------------------------------ validation
def expand_codes(r):
    """Return the effective MIDI codes (hex) a functional row listens to."""
    fn, _, typ, inp, d1, d2, d3, d4 = r[:8]
    if fn.startswith("#") or not fn or typ == "":
        return []
    decks = [d1, d2, d3, d4]
    out = []
    if inp:
        if any(decks):
            for d in decks:
                if d != "":
                    st, data = int(inp[:2], 16), int(inp[2:], 16)
                    out.append(f"{(st & 0xF0) | ((st & 0x0F) + int(d)):02X}{data:02X}")
        else:
            out.append(inp)
    else:
        out += [d for d in decks if d]
    return out

def validate():
    seen = {}
    for r in ROWS:
        for c in expand_codes(r):
            assert re.fullmatch(r"[0-9A-F]{4}", c), (r[0], c)
            assert c not in seen, f"MIDI code {c} used by {seen[c]} and {r[0]}"
            seen[c] = r[0]
    return seen

# ---------------------------------------------------------- hardware tables
def hx(status, ch, data):
    return code(status, ch, data)

def n2(v):  # "0x2B (43)"
    return f"{v} (0x{v:02X})"

def pad_grid(cells):
    """cells: dict pad-> short label. Renders MK1 layout (pad 13-16 top row)."""
    rows = []
    for top in (13, 9, 5, 1):
        rows.append([f"{p}: {cells[p]}" for p in range(top, top + 4)])
    width = max(len(c) for r in rows for c in r)
    line = "+" + "+".join(["-" * (width + 2)] * 4) + "+"
    out = [line]
    for r in rows:
        out.append("| " + " | ".join(c.ljust(width) for c in r) + " |")
        out.append(line)
    return "\n".join(out)

PAD_PAGES = []  # (letter, title, deck, list of (pad, ch0, note, function, desc))
def pad_page(letter, title, deck, items):
    PAD_PAGES.append((letter, title, deck, items))

def hotcue_padfx(letter, deck):
    ch = CH_PAD[deck]
    items = []
    for p in range(1, 9):
        items.append((p, ch, PAD_BASE["HotCue"] + p - 1, f"PAD{p}_HotCue", f"Hot Cue {p}"))
    for p in range(1, 9):
        items.append((p + 8, ch, PAD_BASE["PadFx1"] + p - 1, f"PAD{p}_PadFx1", f"Pad FX 1 · slot {p}"))
    pad_page(letter, f"DECK {deck} · HOT CUE + PAD FX 1", deck, items)

def jump_loop(letter, deck):
    ch = CH_PAD[deck]
    items = []
    for p in range(1, 9):
        items.append((p, ch, PAD_BASE["BeatJump"] + p - 1, f"PAD{p}_BeatJump", f"Beat Jump {BJ[p - 1]}"))
    for p in range(1, 9):
        items.append((p + 8, ch, PAD_BASE["BeatLoop"] + p - 1, f"PAD{p}_BeatLoop", f"Beat Loop slot {p}"))
    pad_page(letter, f"DECK {deck} · BEAT JUMP + BEAT LOOP", deck, items)

def padfx2_delete(letter, deck):
    items = []
    for p in range(1, 9):
        items.append((p, CH_PAD[deck], PAD_BASE["PadFx2"] + p - 1, f"PAD{p}_PadFx2", f"Pad FX 2 · slot {p}"))
    for p in range(1, 9):
        items.append((p + 8, CH_PADS[deck], PAD_BASE["HotCue"] + p - 1, f"PAD{p}_HotCue+Shift", f"Borrar Hot Cue {p}"))
    pad_page(letter, f"DECK {deck} · PAD FX 2 + BORRAR HOT CUE", deck, items)

hotcue_padfx("A", 1)
hotcue_padfx("B", 2)
jump_loop("C", 1)
jump_loop("D", 2)
padfx2_delete("E", 1)
padfx2_delete("F", 2)
pad_page("G", "SAMPLER · PLAY (slots 1-16 del banco activo)", 1,
         [(p, CH_PAD[1], PAD_BASE["Sampler"] + p - 1, f"PAD{p}_Sampler", f"Sample {p} ▶") for p in range(1, 17)])
pad_page("H", "SAMPLER · STOP (slots 1-16 del banco activo)", 1,
         [(p, CH_PADS[1], PAD_BASE["Sampler"] + p - 1, f"PAD{p}_Sampler+Shift", f"Sample {p} ■") for p in range(1, 17)])

# knob pages: list of (name, knobs[8], buttons[8]); each knob: (mode, ch0, cc, function, desc)
ABS, REL = "Absolute", "Relative"
KNOB_PAGES = [
    ("FX1 · BEAT FX 1 + COLOR FX",
     [(ABS, CH_FX1, 0x02, "FX1-1", "FX1 slot 1 · level/depth"),
      (ABS, CH_FX1, 0x03, "FX1-2", "FX1 slot 2 (modo multi)"),
      (ABS, CH_FX1, 0x04, "FX1-3", "FX1 slot 3 (modo multi)"),
      (ABS, CH_FX1, 0x05, "FX1-1Select", "Selector de efecto FX1 (truco KnobSlider)"),
      (ABS, CH_GLB, 0x17, "CFXParameterCH1", "Color FX canal 1"),
      (ABS, CH_GLB, 0x18, "CFXParameterCH2", "Color FX canal 2"),
      (ABS, CH_GLB, 0x19, "CFXParameterCH3", "Color FX canal 3"),
      (ABS, CH_GLB, 0x1A, "CFXParameterCH4", "Color FX canal 4")],
     [("Gate", CH_FX1, 0x47, "FX1-1On", "FX1 slot 1 ON/OFF"),
      ("Gate", CH_FX1, 0x48, "FX1-2On", "FX1 slot 2 ON/OFF"),
      ("Gate", CH_FX1, 0x49, "FX1-3On", "FX1 slot 3 ON/OFF"),
      ("Gate", CH_FX1, 0x4A, "FX1BeatDown", "FX1 beat ◄"),
      ("Gate", CH_FX1, 0x4B, "FX1BeatUp", "FX1 beat ►"),
      ("Toggle", CH_FX1, 0x10, "FX1Assign.CH1", "FX1 → canal 1"),
      ("Toggle", CH_FX1, 0x11, "FX1Assign.CH2", "FX1 → canal 2"),
      ("Toggle", CH_FX1, 0x14, "FX1Assign.MASTER", "FX1 → master")]),
    ("FX2 · BEAT FX 2",
     [(ABS, CH_FX2, 0x02, "FX2-1", "FX2 slot 1 · level/depth"),
      (ABS, CH_FX2, 0x03, "FX2-2", "FX2 slot 2 (modo multi)"),
      (ABS, CH_FX2, 0x04, "FX2-3", "FX2 slot 3 (modo multi)"),
      (ABS, CH_FX2, 0x05, "FX2-1Select", "Selector de efecto FX2 (truco KnobSlider)"),
      None, None, None, None],
     [("Gate", CH_FX2, 0x47, "FX2-1On", "FX2 slot 1 ON/OFF"),
      ("Gate", CH_FX2, 0x48, "FX2-2On", "FX2 slot 2 ON/OFF"),
      ("Gate", CH_FX2, 0x49, "FX2-3On", "FX2 slot 3 ON/OFF"),
      ("Gate", CH_FX2, 0x4A, "FX2BeatDown", "FX2 beat ◄"),
      ("Gate", CH_FX2, 0x4B, "FX2BeatUp", "FX2 beat ►"),
      ("Toggle", CH_FX2, 0x10, "FX2Assign.CH1", "FX2 → canal 1"),
      ("Toggle", CH_FX2, 0x11, "FX2Assign.CH2", "FX2 → canal 2"),
      ("Toggle", CH_FX2, 0x14, "FX2Assign.MASTER", "FX2 → master")]),
    ("FX SELECT · + MIXER (gain/EQ)",
     [(ABS, CH_D1, 0x04, "Gain", "Deck 1 · Gain"),
      (ABS, CH_D1, 0x07, "EQHigh", "Deck 1 · EQ High"),
      (ABS, CH_D1, 0x0B, "EQMid", "Deck 1 · EQ Mid"),
      (ABS, CH_D1, 0x0F, "EQLow", "Deck 1 · EQ Low"),
      (ABS, CH_D2, 0x04, "Gain", "Deck 2 · Gain"),
      (ABS, CH_D2, 0x07, "EQHigh", "Deck 2 · EQ High"),
      (ABS, CH_D2, 0x0B, "EQMid", "Deck 2 · EQ Mid"),
      (ABS, CH_D2, 0x0F, "EQLow", "Deck 2 · EQ Low")],
     [("Gate", CH_FX1, dict(FX_SELECT)[n], f"FX1-1Select.{n}", f"FX1 = {n}") for n in FX_SEL_ON_BUTTONS]),
    ("COLOR FX type + QUANTIZE",
     [None, None, None, None, None, None, None, None],
     [("Gate", CH_GLB, 0x00, "CFX1On", "Color FX = SPACE"),
      ("Gate", CH_GLB, 0x01, "CFX2On", "Color FX = D-ECHO"),
      ("Gate", CH_GLB, 0x02, "CFX3On", "Color FX = CRUSH"),
      ("Gate", CH_GLB, 0x03, "CFX4On", "Color FX = PITCH"),
      ("Gate", CH_GLB, 0x04, "CFX5On", "Color FX = NOISE"),
      ("Gate", CH_GLB, 0x05, "CFX6On", "Color FX = FILTER"),
      ("Gate", CH_D1, 0x35, "Quantize", "Deck 1 · Quantize"),
      ("Gate", CH_D2, 0x35, "Quantize", "Deck 2 · Quantize")]),
]

# global buttons: (hw name, zone, mode, ch0, note, function, desc)
GLOBAL_BUTTONS = [
    ("CONTROL", "Arriba-izq.", "Gate", CH_GLB, 0x65, "Back", "Biblioteca: atrás / cerrar carpeta"),
    ("STEP", "Arriba-izq.", "Gate", CH_GLB, 0x7A, "SwitchActiveWindow", "BROWSE VIEW (navegador grande on/off)"),
    ("BROWSE", "Arriba-izq.", "Gate", CH_GLB, 0x46, "Load", "Cargar track en **Deck 1**"),
    ("SAMPLING", "Arriba-izq.", "Gate", CH_GLB, 0x47, "Load", "Cargar track en **Deck 2**"),
    ("◄ ► (bajo BROWSE)", "Arriba-izq.", "—", None, None, "—", "Reservados por Controller Editor: cambian la **página de knobs** (SHIFT+◄► = plantilla)"),
    ("F1", "Arriba-izq.", "Gate", CH_GLB, 0x36, "PlayPausePreview", "Preview del track seleccionado"),
    ("F2", "Arriba-izq.", "Gate", CH_GLB, 0x67, "AddToTagList", "Agregar track a la Tag List"),
    ("NOTE REPEAT", "Master", "Gate", CH_FX1, 0x43, "FX1ReleaseFXOn", "**RELEASE FX** (echo out / brake / backspin) mientras se mantiene"),
    ("SCENE", "Columna central", "Gate", CH_D1, 0x0B, "PlayPause", "Deck 1 · Play/Pause"),
    ("PATTERN", "Columna central", "Gate", CH_D2, 0x0B, "PlayPause", "Deck 2 · Play/Pause"),
    ("KEYBOARD (PAD MODE)", "Columna central", "Gate", CH_D1, 0x0C, "Cue", "Deck 1 · Cue"),
    ("NAVIGATE", "Columna central", "Gate", CH_D2, 0x0C, "Cue", "Deck 2 · Cue"),
    ("DUPLICATE", "Columna central", "Gate", CH_D1, 0x58, "Sync", "Deck 1 · Beat Sync"),
    ("SELECT", "Columna central", "Gate", CH_D2, 0x58, "Sync", "Deck 2 · Beat Sync"),
    ("SOLO", "Columna central", "Gate", CH_D1, 0x14, "4BeatLoop", "Deck 1 · Auto loop 4 beats"),
    ("MUTE", "Columna central", "Gate", CH_D2, 0x14, "4BeatLoop", "Deck 2 · Auto loop 4 beats"),
    ("A – H (GROUPS)", "Grupos", "—", None, None, "—", "Reservados: seleccionan la **capa de pads** (Pad Page A–H)"),
    ("LOOP", "Transporte", "Gate", CH_GLB, 0x79, "Forward", "Biblioteca: abrir carpeta / entrar"),
    ("◄ (transporte)", "Transporte", "Gate", CH_GLB, 0x38, "BrowseUp", "Biblioteca: subir un track"),
    ("► (transporte)", "Transporte", "Gate", CH_GLB, 0x3A, "BrowseDown", "Biblioteca: bajar un track"),
    ("GRID", "Transporte", "Toggle", CH_FX1, 0x16, "FX1Assign.SAMPLER", "Mandar el Beat FX 1 al **sampler** (latch)"),
    ("PLAY", "Transporte", "Gate", CH_FX1, 0x47, "FX1-1On", "Beat FX 1 ON/OFF (mismo que botón 1 de la página FX1)"),
    ("REC", "Transporte", "Gate", CH_FX2, 0x47, "FX2-1On", "Beat FX 2 ON/OFF (mismo que botón 1 de la página FX2)"),
    ("ERASE", "Transporte", "Gate", CH_GLB, 0x69, "SamplerCue", "Sampler a los audífonos (CUE)"),
    ("SHIFT", "Transporte", "—", None, None, "—", "Reservado por Controller Editor (SHIFT+CONTROL = modo MIDI, SHIFT+◄► = plantilla)"),
]

MASTER_KNOBS = [
    ("SWING", ABS, CH_GLB, 0x03, "SamplerVolume", "Volumen general del sampler"),
]

def conf(fn):
    return "✅" if VERIFIED.get(fn, False) else "⚠️"

def write_md(all_codes):
    L = []
    A = L.append
    A("# MASCHINE MK1 → rekordbox · Mapa MIDI profesional (sampler · FX · performance)\n")
    A("Archivo de mapeo: `Maschine_MK1_rekordbox.midi.csv` (formato oficial de rekordbox, 15 columnas, importable desde el panel MIDI).  ")
    A("Este documento explica **qué manda cada control del Maschine** (para configurarlo en Controller Editor) y **qué hace en rekordbox**.\n")
    A("> Leyenda de confianza por función: ✅ = nombre tomado tal cual de los mapeos oficiales de Pioneer (DDJ-FLX10 / DDJ-GRV6) · ⚠️ = deducido por patrón (funciona con alta probabilidad; si rekordbox no lo reconoce, borra esa fila del CSV).\n")

    A("## 1. Concepto\n")
    A("El MK1 en **modo MIDI** no tiene lógica condicional, así que cada *capa* se construye con lo que el hardware sí ofrece nativamente:\n")
    A("| Recurso del MK1 | Cómo se usa | Capas |")
    A("|---|---|---|")
    A("| **Pad Pages** (botones GROUP A–H) | 8 capas de 16 pads, cada una manda notas en un canal/rango distinto | A–H |")
    A("| **Knob Pages** (botones PAGE ◄ ►) | 4 páginas de 8 knobs + 8 botones de display | 1–4 |")
    A("| Botones globales (22) | Siempre activos, independientes de la página | — |")
    A("| Knob master SWING | Siempre activo (VOLUME y TEMPO sin asignar) | — |")
    A("")
    A("Cada función de rekordbox recibe **un código MIDI único** (regla de rekordbox: un código = una función), por eso no dependemos del botón SHIFT de rekordbox: la capa la decide el Maschine.\n")
    A("Decks: la plantilla cubre **Deck 1 y Deck 2**; el CSV ya trae los códigos de Deck 3/4 (offsets 2,3 y canales de pads 12–15) por si un día haces una segunda plantilla a 4 decks.\n")
    A("### Chuleta del panel\n")
    A("```")
    A("MASCHINE MK1 · plantilla REKORDBOX")
    A("")
    A("CONTROL = Back (biblioteca)     STEP = Browse View       B1..B8 (sobre displays) = botones de la PÁGINA DE KNOBS")
    A("BROWSE  = Load Deck 1           SAMPLING = Load Deck 2   K1..K8 (bajo displays)  = knobs de la PÁGINA DE KNOBS")
    A("◄ ►     = cambiar página de knobs (SHIFT+◄► = plantilla)")
    A("F1      = Preview track         F2 = Tag track")
    A("")
    A("SWING = Sampler Volume      NOTE REPEAT = RELEASE FX (mantener)      VOLUME / TEMPO = sin asignar")
    A("")
    A("GROUP A..H = CAPA DE PADS:")
    A("  A D1 HotCue+PadFX1   B D2 HotCue+PadFX1   C D1 Jump+Loop   D D2 Jump+Loop")
    A("  E D1 PadFX2+Borrar   F D2 PadFX2+Borrar   G Sampler PLAY   H Sampler STOP")
    A("")
    A("SCENE = Play D1    PATTERN = Play D2    KEYBOARD = Cue D1     NAVIGATE = Cue D2")
    A("DUPLICATE = Sync D1  SELECT = Sync D2   SOLO = 4Beat Loop D1  MUTE = 4Beat Loop D2")
    A("")
    A("LOOP = Forward (abrir carpeta)   ◄ = Browse Up   ► = Browse Down   GRID = FX1 -> Sampler (latch)")
    A("PLAY = FX1 ON/OFF      REC = FX2 ON/OFF      ERASE = Sampler Cue     SHIFT = reservado")
    A("")
    A("PÁGINAS DE KNOBS: 1 FX1 + Color FX depth | 2 FX2 | 3 FX1 selección directa + Gain/EQ | 4 Color FX type + Quantize")
    A("```\n")

    A("## 2. Plan de canales MIDI\n")
    A("| Uso | Canal (Controller Editor, 1–16) | Status hex | Tipo |")
    A("|---|---|---|---|")
    A("| Deck 1 (botones / knobs de deck) | 1 | `90` / `B0` | Note / CC |")
    A("| Deck 2 | 2 | `91` / `B1` | Note / CC |")
    A("| Deck 3 / Deck 4 (reservado) | 3 / 4 | `92` `93` / `B2` `B3` | Note / CC |")
    A("| Beat FX 1 | 5 | `94` / `B4` | Note / CC |")
    A("| Beat FX 2 | 6 | `95` / `B5` | Note / CC |")
    A("| Global: browser, sampler, mixer, Color FX | 7 | `96` / `B6` | Note / CC |")
    A("| Pads Deck 1 · capa normal / capa \"shift\" (borrar, stop) | 8 / 9 | `97` / `98` | Note |")
    A("| Pads Deck 2 · normal / shift | 10 / 11 | `99` / `9A` | Note |")
    A("| Pads Deck 3 y 4 (reservado) | 12–15 | `9B`–`9E` | Note |")
    A("")
    A("Rango de notas de los pads (igual que Pioneer): HOT CUE `00–0F` · PAD FX1 `10–1F` · BEAT JUMP `20–2F` · SAMPLER `30–3F` · KEYBOARD `40–4F` · PAD FX2 `50–5F` · BEAT LOOP `60–6F` · KEY SHIFT `70–7F`.\n")

    A("## 3. Capas de pads (GROUP A–H)\n")
    A("Numeración física del MK1: el pad **1 está abajo a la izquierda** y el **16 arriba a la derecha** (fila inferior 1-4, luego 5-8, 9-12 y arriba 13-16).\n")
    A("| GROUP | Capa | Pads 1–8 (dos filas inferiores) | Pads 9–16 (dos filas superiores) |")
    A("|---|---|---|---|")
    A("| **A** | Deck 1 | Hot Cue 1–8 | Pad FX 1 · slots 1–8 (momentáneo) |")
    A("| **B** | Deck 2 | Hot Cue 1–8 | Pad FX 1 · slots 1–8 |")
    A("| **C** | Deck 1 | Beat Jump ◄1 ►1 ◄2 ►2 ◄4 ►4 ◄8 ►8 | Beat Loop slots 1–8 |")
    A("| **D** | Deck 2 | Beat Jump | Beat Loop |")
    A("| **E** | Deck 1 | Pad FX 2 · slots 1–8 | **Borrar** Hot Cue 1–8 |")
    A("| **F** | Deck 2 | Pad FX 2 · slots 1–8 | Borrar Hot Cue 1–8 |")
    A("| **G** | Sampler | Slots 1–8 ▶ | Slots 9–16 ▶ (banco activo) |")
    A("| **H** | Sampler | Slots 1–8 ■ stop | Slots 9–16 ■ stop |")
    A("")
    A("Los tamaños de Beat Jump / Beat Loop siguen el **rango activo** en el panel PAD de rekordbox (por defecto Beat Jump 1-2-4-8 beats y Beat Loop ¼ … 32 beats).\n")
    A("Los botones GROUP y PAGE no mandan MIDI (los consume Controller Editor), así que el modo de pad que muestra la pantalla de rekordbox no cambia solo: no importa, cada función es explícita (`PAD1_HotCue`, `PAD1_Sampler`…) y se ejecuta sin importar el modo visible.\n")
    for letter, title, deck, items in PAD_PAGES:
        A(f"### GROUP {letter} — {title}\n")
        cells = {p: d for (p, _, _, _, d) in items}
        A("```")
        A(pad_grid(cells))
        A("```")
        A("")
        A("| Pad | Controller Editor (Note · canal · nota) | Código | Función rekordbox | Acción |")
        A("|---|---|---|---|---|")
        for (p, ch, note, fn, d) in items:
            A(f"| {p} | Note · ch **{ch1(ch)}** · nota **{note}** (0x{note:02X}) | `{hx(NOTE, ch, note)}` | `{fn}` {conf(fn)} | {d} |")
        A("")

    A("## 4. Páginas de knobs (PAGE ◄ ►)\n")
    A("Cada página tiene los **8 knobs** bajo los displays y los **8 botones** sobre los displays (Botón 1 = izquierda). Los knobs del MK1 solo mandan valores **Absolute** (0-127) en Controller Editor: no existe modo Relative. Por eso no hay funciones tipo *Rotary* (Browse, Zoom, Loop) y la navegación de la biblioteca va con botones.\n")
    for i, (name, knobs, buttons) in enumerate(KNOB_PAGES, start=1):
        A(f"### Página {i} — {name}\n")
        A("| Knob | Controller Editor (CC · canal · nº · modo) | Código | Función rekordbox | Acción |")
        A("|---|---|---|---|---|")
        for k, item in enumerate(knobs, start=1):
            if item is None:
                A(f"| K{k} | — | — | *(libre)* | Sin asignar |")
                continue
            mode, ch, ccn, fn, d = item
            A(f"| K{k} | CC · ch **{ch1(ch)}** · nº **{ccn}** (0x{ccn:02X}) · **{mode}** | `{hx(CC, ch, ccn)}` | `{fn}` {conf(fn)} | {d} |")
        A("")
        A("| Botón | Controller Editor (Note · canal · nota · modo) | Código | Función rekordbox | Acción |")
        A("|---|---|---|---|---|")
        for b, (mode, ch, note, fn, d) in enumerate(buttons, start=1):
            A(f"| B{b} | Note · ch **{ch1(ch)}** · nota **{note}** (0x{note:02X}) · **{mode}** | `{hx(NOTE, ch, note)}` | `{fn}` {conf(fn)} | {d} |")
        A("")

    A("## 5. Botones globales (no dependen de página)\n")
    A("| Botón MK1 | Zona | Controller Editor | Código | Función rekordbox | Acción |")
    A("|---|---|---|---|---|---|")
    for (hw, zone, mode, ch, note, fn, d) in GLOBAL_BUTTONS:
        if ch is None:
            A(f"| **{hw}** | {zone} | — | — | — | {d} |")
        else:
            A(f"| **{hw}** | {zone} | Note · ch {ch1(ch)} · nota {note} (0x{note:02X}) · {mode} | `{hx(NOTE, ch, note)}` | `{fn}` {conf(fn)} | {d} |")
    A("")

    A("## 6. Knobs master (VOLUME · TEMPO · SWING)\n")
    A("| Knob | Controller Editor | Código | Función rekordbox | Acción |")
    A("|---|---|---|---|---|")
    for (hw, mode, ch, ccn, fn, d) in MASTER_KNOBS:
        A(f"| **{hw}** | CC · ch {ch1(ch)} · nº {ccn} (0x{ccn:02X}) · {mode} | `{hx(CC, ch, ccn)}` | `{fn}` {conf(fn)} | {d} |")
    A("")

    A("## 7. Configuración en Controller Editor (paso a paso)\n")
    A("1. Abre **Controller Editor**, selecciona el MASCHINE (MK1) y crea/renombra la plantilla **REKORDBOX** (ya la tienes como `01 - REKORDBOX`).")
    A("2. Inspector → pestaña **Pages**: activa **Enable Pad Pages** y crea las 8 Pad Pages con nombres `A D1 CUE+FX`, `B D2 CUE+FX`, `C D1 JUMP+LOOP`, `D D2 JUMP+LOOP`, `E D1 FX2+DEL`, `F D2 FX2+DEL`, `G SAMPLER PLAY`, `H SAMPLER STOP`. Crea 4 Knob Pages: `FX1`, `FX2`, `FXSEL+MIX`, `CFX TYPE`.")
    A("3. **Pads** (en cada Pad Page): Type **Note** · Channel y Note según las tablas de la sección 3 · Mode **Gate** (Note On al golpear, Note Off al soltar — imprescindible para Pad FX momentáneo) · acción **Press** (presión) en **Off**.")
    A("4. **Botones** (globales y los 8 de cada Knob Page): Type **Note** · Mode **Gate** · Value 127. Excepción: los botones `FXnAssign.*` (botones 6-8 de las páginas FX1/FX2 y GRID) en modo **Toggle** (rekordbox trata la asignación de FX como un interruptor).")
    A("5. **Knobs**: Type **Control Change** · Channel/Number según tablas · Mode **Absolute** (rango 0-127) en todos.")
    A("6. **LEDs** (opcional, recomendado): en cada pad/botón pon *LED On* = **Remote/MIDI** para que rekordbox encienda hot cues cargados, samples sonando y FX activos (el CSV ya manda el mismo código por MIDI OUT).")
    A("7. En el Maschine: **SHIFT + CONTROL** entra al modo MIDI · **SHIFT + PAGE ◄ ►** elige plantilla · **PAGE ◄ ►** cambia página de knobs · **GROUP A–H** cambia capa de pads. No hace falta tener Controller Editor abierto; el servicio NI Hardware Agent carga la plantilla.\n")

    A("## 8. Importar en rekordbox\n")
    A("1. rekordbox en modo **PERFORMANCE** → botón **MIDI** (arriba a la derecha).")
    A("2. Dispositivo: *Maschine Controller* (en macOS puede aparecer como *Maschine Controller Virtual Input*). Si no aparece, cierra el software MASCHINE: no puede estar usando el controlador a la vez.")
    A("3. **IMPORT** → `Maschine_MK1_rekordbox.midi.csv`. rekordbox sobreescribe el mapeo del dispositivo y lo guarda al cerrar la ventana.")
    A("4. Prueba cada sección con **LEARN apagado**; la columna MIDI IN de la lista debe coincidir con el código de las tablas de este documento.\n")

    A("## 9. Ajustes recomendados dentro de rekordbox\n")
    A("- **PAD FX**: configura los bancos PAD FX 1 (Group A/B, pads 9-16) y PAD FX 2 (Group E/F, pads 1-8) con tus combinaciones (p. ej. Echo ½, Roll ⅛, Spiral 1, Filter LPF, Trans ¼, Reverb, Pitch, Vinyl Brake).")
    A("- **RELEASE FX** (NOTE REPEAT): elige el tipo en el panel FX1 (Vinyl Brake / Echo / Back Spin).")
    A("- **SAMPLER**: abre el panel SAMPLER en rekordbox → 16 slots por banco, 4 bancos (cámbialos desde la pantalla del sampler en rekordbox). Define por slot *one-shot* o *loop*; para loops usa la capa **H** para detenerlos. Sube el volumen del sampler con **SWING** antes de disparar (el encoder arranca en 0 al cargar la plantilla).")
    A("- **Beat FX multi/single**: los knobs 2-3 y botones 2-3 de las páginas FX solo actúan en modo *multi* (3 slots). En modo *single* usa knob 1 + botón 1 + beat ◄ ►.")
    A("- **Color FX**: elige el tipo con los botones 1-6 de la página 4 y la profundidad con los knobs 5-8 de la página 1. Como son encoders absolutos, **céntralos (valor 64 en el display) antes de activar un Color FX** o arrancarán desde el extremo.")
    A("- **Gain/EQ (página 3)**: sólo tiene sentido si mezclas dentro de rekordbox. Mismo aviso: lleva cada encoder a 64 antes de usarlo.\n")

    A("## 10. Verificación y problemas típicos\n")
    A("| Síntoma | Causa / solución |")
    A("|---|---|")
    A("| Nada responde | rekordbox no está en PERFORMANCE, el dispositivo seleccionado no es el Maschine, o el Maschine no está en modo MIDI (SHIFT+CONTROL). |")
    A("| Un pad/botón hace otra cosa | El display derecho del MK1 muestra el último evento (`EVENT: CH.x – NOTE – nn`); compáralo con la columna *Código* de este documento. |")
    A("| Pad FX / Release FX se queda pegado | El control no manda Note Off: en Controller Editor confirma Mode **Gate** (no Trigger/Toggle). Si tu versión manda Note Off como `8n` y rekordbox lo ignora, cambia ese control a Type **Control Change** (Gate, 127/0) y en el CSV sustituye `9nxx` por `Bnxx` en esa fila. |")
    A("| Navego la biblioteca y no avanza | ◄ / ► del transporte = BrowseUp / BrowseDown, LOOP = Forward (abrir carpeta). Antes pulsa STEP para ver la Browse View. |")
    A("| El FX se asigna y se desasigna solo | Los botones `FXnAssign.*` deben estar en **Toggle**, no Gate. |")
    A("| rekordbox rechaza el import | Borra las filas ⚠️ (sección *Deducidas/Reservados* y los `FX2-*`) y vuelve a importar; el resto son nombres oficiales de Pioneer. |")
    A("| Quiero velocidad en el sampler | rekordbox sólo acepta *Velocity Sampler* con pads que manden Note + CC (tipo `Value`); no está incluido. Se puede añadir usando la acción *Press* del pad como CC. |")
    A("")

    A("## 11. Resumen de códigos (todas las filas funcionales del CSV)\n")
    A("| Código(s) MIDI | Función | Tipo | Dónde |")
    A("|---|---|---|---|")
    for r in ROWS:
        codes = expand_codes(r)
        if not codes:
            continue
        A(f"| `{'` `'.join(codes)}` | `{r[0]}` {conf(r[0])} | {r[2]} | {r[14]} |")
    A("")
    A("---")
    A("Fuentes del formato: mapeos oficiales `DDJ-FLX10.midi.csv` / `DDJ-GRV6.midi.csv` (rekordbox 7), *MIDI LEARN Operation Guide* (AlphaTheta), *Controller Editor Manual* (Native Instruments, cap. MASCHINE: Pad Pages via GROUP, Knob Pages via PAGE, SHIFT y PAGE no asignables), DJ TechTools *Hacking Rekordbox FX* (comandos `FX1-1Select.NAME`, `FX1Assign.*`, truco KnobSlider).")
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

if __name__ == "__main__":
    data = write_csv()
    codes = validate()
    write_md(codes)
    func_rows = sum(1 for r in ROWS if expand_codes(r))
    print(f"CSV: {CSV_PATH}\n  lines={data.count(chr(10))} functional_rows={func_rows} unique_codes={len(codes)}")
    print(f"MD : {MD_PATH}")
