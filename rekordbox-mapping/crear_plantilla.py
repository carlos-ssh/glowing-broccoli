#!/usr/bin/env python3
"""Genera la plantilla de Controller Editor (MASCHINE MK1, .ncm) a partir de generador.py.

Usa las mismas tablas (GLOBAL_BUTTONS, MASTER_KNOBS, KNOB_PAGES, PAD_PAGES) que el
CSV y el MAPA, asi los tres archivos nunca se desincronizan.

Salida: REKORDBOX.ncm  (Controller Editor -> Templates -> Edit -> Import)
"""
import os
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import generador as g

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "REKORDBOX.ncm")

# Controles de grupo A-H: se copian tal cual de la plantilla actual del usuario si existe.
NCS = os.path.expanduser("~/Library/Application Support/Native Instruments/Controller Editor/Maschine.ncs")

# Nombre del boton en el MAPA -> id del control en Controller Editor
BTN_ID = {
    "CONTROL": "Control", "STEP": "Step", "BROWSE": "Browse", "SAMPLING": "Sample",
    "F1": "F1", "F2": "F2", "NOTE REPEAT": "Repeat",
    "SCENE": "Scene", "PATTERN": "Pattern", "KEYBOARD (PAD MODE)": "Keyboard",
    "NAVIGATE": "Navigate", "DUPLICATE": "Duplicate", "SELECT": "Select",
    "SOLO": "Solo", "MUTE": "Mute", "LOOP": "Loop",
    "◄ (transporte)": "Prev.", "► (transporte)": "Next", "GRID": "Grid",
    "PLAY": "Play", "REC": "Record", "ERASE": "Erase",
}
KNOB_ID = {"VOLUME": "Volume", "TEMPO": "Tempo", "SWING": "Swing"}

PAD_PAGE_NAMES = {
    "A": "A D1 CUE+FX", "B": "B D2 CUE+FX", "C": "C D1 JUMP+LOOP", "D": "D D2 JUMP+LOOP",
    "E": "E D1 FX2+DEL", "F": "F D2 FX2+DEL", "G": "G SAMPLER PLAY", "H": "H SAMPLER STOP",
}
KNOB_PAGE_NAMES = ["FX1", "FX2", "FXSEL+MIX", "CFX TYPE"]

I = "  "


def button(ind, bid, ch, note, mode, name=None, disabled=False):
    beh = "toggle" if mode == "Toggle" else "gate"
    s = [f'{ind}<button version="1" id="{escape(bid)}">']
    if disabled:
        s.append(f"{ind}{I}<disabled/>")
    if name:
        s.append(f"{ind}{I}<name>{escape(name)}</name>")
    s += [
        f"{ind}{I}<note>{note}</note>",
        f"{ind}{I}<channel>{ch}</channel>",
        f"{ind}{I}<off>0</off>",
        f"{ind}{I}<on>127</on>",
        f"{ind}{I}<last>0</last>",
        f'{ind}{I}<behavior onIfDown="on">{beh}</behavior>',
        f"{ind}{I}<reaction>ondown</reaction>",
        f"{ind}</button>",
    ]
    return s


def knob(ind, kid, ch, cc, name=None, disabled=False):
    s = [f'{ind}<knob version="1" id="{escape(kid)}">']
    if disabled:
        s.append(f"{ind}{I}<disabled/>")
    if name:
        s.append(f"{ind}{I}<name>{escape(name)}</name>")
    s += [
        f"{ind}{I}<controller>{cc}</controller>",
        f"{ind}{I}<channel>{ch}</channel>",
        f"{ind}{I}<min>0</min>",
        f"{ind}{I}<max>127</max>",
        f"{ind}{I}<default>0</default>",
        f"{ind}{I}<last>0</last>",
        f"{ind}{I}<range>360</range>",
        f"{ind}{I}<steps>20</steps>",
        f"{ind}{I}<bipolar>off</bipolar>",
        f"{ind}</knob>",
    ]
    return s


def pad(ind, pid, ch, note, name=None):
    s = [f'{ind}<pad subtype="trigger" version="1" id="{pid}">']
    if name:
        s.append(f"{ind}{I}<name>{escape(name)}</name>")
    s += [
        f"{ind}{I}<note>{note}</note>",
        f"{ind}{I}<channel>{ch}</channel>",
        f"{ind}{I}<min>0</min>",
        f"{ind}{I}<max>127</max>",
        f"{ind}{I}<default>0</default>",
        f"{ind}{I}<last>0</last>",
        f"{ind}{I}<lastExt>0</lastExt>",
        f'{ind}{I}<behavior onIfDown="on">gate</behavior>',
        f"{ind}{I}<reaction>ondown</reaction>",
        f"{ind}</pad>",
    ]
    return s


def group_buttons_from_ncs():
    """Botones A-H tal como estan en la plantilla actual (no se tocan)."""
    out = []
    if not os.path.exists(NCS):
        return out
    root = ET.parse(NCS).getroot()
    for b in root.iter("button"):
        if b.get("id") in list("ABCDEFGH") and b in list(root.find(".//controls")):
            out += ["    " + ln for ln in ET.tostring(b, encoding="unicode").strip().splitlines()]
    return out


def build():
    L = ['<?xml version="1.0" encoding="UTF-8" standalone="no" ?>',
         '<ni-controller-midi-map version="1">',
         f'{I}<midi-map name="REKORDBOX" port="internal" type="Maschine">',
         f"{I*2}<handleGroupControls/>",
         f"{I*2}<velocitycurve>3</velocitycurve>",
         f"{I*2}<controls>"]
    ind = I * 3
    done = set()
    for hw, zone, mode, ch, note, fn, desc in g.GLOBAL_BUTTONS:
        if ch is None or hw not in BTN_ID:
            continue
        L += button(ind, BTN_ID[hw], ch, note, mode, name=hw.split(" (")[0])
        done.add(BTN_ID[hw])
    missing = {v for v in BTN_ID.values()} - done
    assert not missing, missing
    for hw, mode, ch, ccn, fn, desc in g.MASTER_KNOBS:
        L += knob(ind, KNOB_ID[hw], ch, ccn, name=hw)
    # VOLUME y TEMPO: el MK1 no tiene modo Relative, se desactivan para no mandar CC absolutos
    for kid in ("Volume", "Tempo"):
        L += knob(ind, kid, 0, 0, disabled=True)
    L += group_buttons_from_ncs()
    L.append(f"{I*2}</controls>")

    L.append(f"{I*2}<pages>")
    L.append(f"{I*3}<current_index>0</current_index>")
    for pname, (title, knobs, buttons) in zip(KNOB_PAGE_NAMES, g.KNOB_PAGES):
        L.append(f'{I*3}<page name="{escape(pname)}">')
        for n, (mode, ch, note, fn, desc) in enumerate(buttons, start=1):
            L += button(I * 4, f"Button{n}", ch, note, mode, name=fn)
        for n, item in enumerate(knobs, start=1):
            if item is None:
                L += knob(I * 4, f"Knob{n}", 0, 0, disabled=True)
            else:
                _, ch, ccn, fn, desc = item
                L += knob(I * 4, f"Knob{n}", ch, ccn, name=fn)
        L.append(f"{I*3}</page>")
    L.append(f"{I*2}</pages>")

    L.append(f"{I*2}<groups>")
    L.append(f"{I*3}<current_index>0</current_index>")
    for letter, title, deck, items in g.PAD_PAGES:
        L.append(f'{I*3}<group name="{escape(PAD_PAGE_NAMES[letter])}">')
        for p, ch, note, fn, desc in sorted(items, key=lambda x: x[0]):
            L += pad(I * 4, f"Pad{p}", ch, note, name=fn)
        L.append(f"{I*3}</group>")
    L.append(f"{I*2}</groups>")
    L += [f"{I}</midi-map>", "</ni-controller-midi-map>", ""]
    return "\n".join(L)


def check(path):
    root = ET.parse(path).getroot()
    mm = root.find("midi-map")
    pages = mm.find("pages").findall("page")
    groups = mm.find("groups").findall("group")
    n_pages, n_groups = len(pages), len(groups)
    pads = sum(len(gr.findall("pad")) for gr in groups)
    assert n_pages == 4 and n_groups == 8 and pads == 8 * 16, (n_pages, n_groups, pads)
    for gr in groups:
        assert len(gr.findall("pad")) == 16, gr.get("name")
        seen = {(p.findtext("channel"), p.findtext("note")) for p in gr.findall("pad")}
        assert len(seen) == 16, f"codigos repetidos en {gr.get('name')}"
    for pg in pages:
        assert len(pg.findall("button")) == 8 and len(pg.findall("knob")) == 8, pg.get("name")
    return n_pages, n_groups, pads, len(mm.find("controls"))


if __name__ == "__main__":
    xml = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("OK", OUT, "paginas/grupos/pads/controles =", check(OUT))
