"""Genera los paneles SVG en los dos idiomas desde content/story.json.

Salida: assets/<lang>/<nombre>.svg

Todo el texto sale del JSON. Si una cadena tiene que cambiar, se cambia alla.
Correr: python3 tools/build_art.py
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from art import esc, panel, set_out_dir, C  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORY = json.loads((ROOT / "content" / "story.json").read_text(encoding="utf-8"))
W = 880


# ════════════════════════════ pantalla de titulo ════════════════════════════
def title(T):
    style = """
    .t { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
         font-weight: 800; font-size: 74px; letter-spacing: 6px; text-anchor: middle; }
    .s { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 16px;
         letter-spacing: 7px; text-anchor: middle; fill: #7FE7C4; }
    .start { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px;
             letter-spacing: 4px; text-anchor: middle; fill: #FFD166;
             animation: blink 1.4s steps(1) infinite; }
    @keyframes blink { 0%,55% { opacity: 1; } 56%,100% { opacity: 0; } }
    .coin { animation: float 2.6s ease-in-out infinite; }
    @keyframes float { 0%,100% { transform: translateY(0); }
                       50% { transform: translateY(-5px); } }
    """
    body = (
        '<text class="t" x="440" y="112" fill="url(#chrome)" filter="url(#glow)">%s</text>'
        '<text class="s" x="440" y="152">%s</text>'
        '<g transform="translate(440,186)"><g class="coin">'
        '<circle r="11" fill="none" stroke="#FFD166" stroke-width="2"/>'
        '<text y="6" text-anchor="middle" font-family="monospace" font-size="13"'
        ' font-weight="700" fill="#FFD166">$</text></g></g>'
        '<text class="start" x="440" y="224">%s</text>'
        % (esc(T["name"]), esc(T["sub"]), esc(T["start"]))
    )
    return panel("title", W, 250, style=style, body=body, bulbs="all")


# ════════════════════════════ mapa del recorrido ════════════════════════════
def mapa(T):
    xs = [130, 350, 570, 760]
    out = []
    for (name, year), x in zip(T["stops"], xs):
        last = x == xs[-1]
        col = C["amber"] if last else C["cyan"]
        out.append(
            '<circle cx="%d" cy="108" r="7" fill="%s" opacity="0.18"/>'
            '<circle cx="%d" cy="108" r="4" fill="%s"/>'
            '<text class="stop" x="%d" y="88">%s</text>'
            '<text class="yr" x="%d" y="136">%s</text>'
            % (x, col, x, col, x, esc(name), x, esc(year))
        )
        if last:
            out.append('<circle class="pulse" cx="%d" cy="108" r="7" fill="none"'
                       ' stroke="%s" stroke-width="2"/>' % (x, C["amber"]))
    style = """
    .stop { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 11px;
            letter-spacing: 2px; fill: #C9D4E8; text-anchor: middle; }
    .yr   { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 10px;
            fill: #6B7A99; text-anchor: middle; }
    .route { stroke-dasharray: 6 7; animation: march 2.4s linear infinite; }
    @keyframes march { to { stroke-dashoffset: -26; } }
    .plane { animation: fly 9s ease-in-out infinite; }
    @keyframes fly {
      0% { transform: translateX(0); opacity: 0; } 8% { opacity: 1; }
      88% { opacity: 1; } 100% { transform: translateX(630px); opacity: 0; }
    }
    .pulse { animation: ring 2s ease-out infinite; }
    @keyframes ring { 0% { r: 7; opacity: .9; } 100% { r: 20; opacity: 0; } }
    """
    body = (
        '<text class="hdr" x="34" y="44">%s</text>'
        '<line class="route" x1="130" y1="108" x2="760" y2="108"'
        ' stroke="#2A3550" stroke-width="2"/>%s'
        '<g class="plane"><path transform="translate(122,96)"'
        ' d="M0 8 L20 2 L17 9 L20 16 Z" fill="#7FE7C4" opacity="0.95"/></g>'
        '<text class="dim" x="34" y="176">%s</text>'
        % (esc(T["header"]), "".join(out), esc(T["footer"]))
    )
    return panel("mapa", W, 210, style=style, body=body)


# ════════════════════════════ cap 1 - Mendoza ════════════════════════════
def ch1(T):
    peaks = "M 520 150 L 570 104 L 600 126 L 645 84 L 690 128 L 725 110 L 780 150 Z"
    rays = "".join('<line x1="0" y1="0" x2="0" y2="-26" stroke="#FFD166"'
                   ' stroke-width="2" opacity="0.55" transform="rotate(%d)"/>' % (a * 45)
                   for a in range(8))
    style = """
    .sun { animation: spin 26s linear infinite; transform-origin: 0 0; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .heat { animation: wobble 3.4s ease-in-out infinite; }
    @keyframes wobble { 0%,100% { opacity: .25; } 50% { opacity: .6; } }
    .tab { animation: tabs 4s ease-in-out infinite; }
    @keyframes tabs { 0%,100% { opacity: .35; } 50% { opacity: 1; } }
    """
    lines = "".join('<text class="dim" x="34" y="%d">%s</text>' % (122 + i * 20, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>'
        '<text class="big" x="34" y="92">%s</text>%s'
        '<g transform="translate(482,58)"><g class="sun">%s</g>'
        '<circle r="11" fill="#FFD166" opacity="0.9"/></g>'
        '<path d="%s" fill="#1B2437" stroke="#2A3550" stroke-width="1.5"/>'
        '<g class="heat"><path d="M 520 158 q 30 -6 60 0 t 60 0 t 60 0 t 60 0"'
        ' fill="none" stroke="#7FE7C4" stroke-width="1.5"/></g>'
        '<g transform="translate(372,104)">'
        '<rect width="120" height="42" rx="4" fill="#161B27" stroke="#2A3550"/>'
        '<g class="tab" fill="#39C2FF">'
        '<rect x="7" y="7" width="16" height="5" rx="2"/>'
        '<rect x="27" y="7" width="16" height="5" rx="2"/>'
        '<rect x="47" y="7" width="16" height="5" rx="2"/>'
        '<rect x="67" y="7" width="16" height="5" rx="2"/>'
        '<rect x="87" y="7" width="16" height="5" rx="2"/></g>'
        '<rect x="7" y="20" width="70" height="3" rx="1" fill="#2A3550"/>'
        '<rect x="7" y="28" width="96" height="3" rx="1" fill="#2A3550"/></g>'
        % (esc(T["header"]), esc(T["big"]), lines, rays, peaks)
    )
    return panel("ch1-mendoza", W, 200, style=style, body=body)


# ════════════════════════════ cap 2 - la facultad ════════════════════════════
def ch2(T):
    bars = []
    for i, label in enumerate(T["rows"]):
        y = 86 + i * 32
        bars.append(
            '<text class="body" x="34" y="%d">%s</text>' % (y + 4, esc(label))
            + '<rect x="240" y="%d" width="420" height="9" rx="4" fill="#161B27"'
              ' stroke="#2A3550"/>' % (y - 5)
            + '<rect class="fill f%d" x="240" y="%d" width="420" height="9" rx="4"'
              ' fill="#7FE7C4" opacity="0.85"/>' % (i, y - 5)
            + '<text class="dim" x="676" y="%d">%s</text>' % (y + 4, esc(T["status"]))
        )
    style = """
    .fill { transform-origin: 240px 0; animation: grow 5s ease-out infinite; }
    .f0 { animation-delay: 0s; } .f1 { animation-delay: .5s; } .f2 { animation-delay: 1s; }
    @keyframes grow { 0% { transform: scaleX(0); } 35% { transform: scaleX(1); }
                      92% { transform: scaleX(1); } 100% { transform: scaleX(0); } }
    """
    body = ('<text class="hdr" x="34" y="44">%s</text>%s'
            '<text class="dim" x="34" y="176">%s</text>'
            % (esc(T["header"]), "".join(bars), esc(T["footer"])))
    return panel("ch2-utn", W, 215, style=style, body=body)


# ════════════════════════════ cap 3 - el challenge ════════════════════════════
def ch3(T):
    style = """
    .flap { transform-origin: 50% 0%; animation: open 5s ease-in-out infinite; }
    @keyframes open { 0%,12% { transform: rotateX(0deg); }
                      30%,88% { transform: rotateX(178deg); }
                      100% { transform: rotateX(0deg); } }
    .letter { animation: slide 5s ease-in-out infinite; }
    @keyframes slide { 0%,24% { transform: translateY(0); opacity: 0; }
                       44% { transform: translateY(-26px); opacity: 1; }
                       88% { transform: translateY(-26px); opacity: 1; }
                       100% { transform: translateY(0); opacity: 0; } }
    .cur { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }
    """
    lines = "".join('<text class="dim" x="250" y="%d">%s</text>' % (116 + i * 20, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>'
        '<g transform="translate(34,100)"><g class="letter">'
        '<rect x="18" y="4" width="132" height="58" rx="3" fill="#161B27" stroke="#2A3550"/>'
        '<rect x="28" y="16" width="70" height="4" rx="2" fill="#7FE7C4" opacity="0.8"/>'
        '<rect x="28" y="28" width="104" height="3" rx="1.5" fill="#2A3550"/>'
        '<rect x="28" y="38" width="88" height="3" rx="1.5" fill="#2A3550"/>'
        '<rect x="28" y="48" width="96" height="3" rx="1.5" fill="#2A3550"/></g>'
        '<rect y="30" width="168" height="62" rx="4" fill="#1B2437" stroke="#2A3550"'
        ' stroke-width="1.5"/><g class="flap">'
        '<path d="M0 30 L84 74 L168 30 Z" fill="#212a3d" stroke="#2A3550"'
        ' stroke-width="1.5"/></g></g>'
        '<text class="body" x="250" y="92">%s</text>%s'
        '<rect class="cur" x="250" y="186" width="8" height="2" fill="#FFD166"/>'
        % (esc(T["header"]), esc(T["subject"]), lines)
    )
    return panel("ch3-challenge", W, 228, style=style, body=body)


# ════════════════════════════ cap 4 - escala ════════════════════════════
def ch4(T):
    calm = [(0, 20), (40, 22), (80, 19), (120, 23), (160, 21), (200, 24)]
    spike = [(240, 30), (280, 44), (320, 38), (360, 58), (400, 72), (440, 66), (470, 78)]
    pts = " ".join("%d,%d" % (x, 80 - y) for x, y in calm + spike)
    style = """
    .alert { animation: pulse 1.1s ease-in-out infinite; }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .25; } }
    .trace { stroke-dasharray: 700; stroke-dashoffset: 700;
             animation: draw 4.5s ease-in-out infinite; }
    @keyframes draw { 0% { stroke-dashoffset: 700; } 60% { stroke-dashoffset: 0; }
                      95% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 700; } }
    """
    lines = "".join('<text class="body" x="560" y="%d">%s</text>' % (90 + i * 22, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>'
        '<g class="alert"><circle cx="746" cy="39" r="5" fill="#FF5C7A"/></g>'
        '<text class="dim" x="762" y="44">%s</text>'
        '<g transform="translate(34,64)">'
        '<rect width="500" height="90" rx="6" fill="#161B27" stroke="#2A3550"/>'
        '<polyline class="trace" points="%s" fill="none" stroke="#FF5C7A"'
        ' stroke-width="2" transform="translate(14,4)"/>'
        '<text class="dim" x="14" y="82">%s</text></g>%s'
        % (esc(T["header"]), esc(T["time"]), pts, esc(T["chart"]), lines)
    )
    return panel("ch4-escala", W, 200, style=style, body=body)


# ════════════════════════════ cap 5 - el avion ════════════════════════════
def ch5(T):
    # El arco va bajo: antes cruzaba justo por encima del bloque de texto.
    arc = "M 70 190 Q 440 70 810 165"
    rain = "".join('<line class="drop d%d" x1="%d" y1="0" x2="%d" y2="13"'
                   ' stroke="#39C2FF" stroke-width="1.4" opacity="0.5"/>'
                   % (i % 4, 596 + i * 17, 593 + i * 17) for i in range(12))
    style = """
    .path { stroke-dasharray: 5 8; animation: march 2.6s linear infinite; }
    @keyframes march { to { stroke-dashoffset: -26; } }
    .plane { offset-path: path("M 70 190 Q 440 70 810 165"); offset-rotate: auto;
             animation: fly 8s ease-in-out infinite; }
    @keyframes fly { 0% { offset-distance: 0%; opacity: 0; } 10% { opacity: 1; }
                     90% { opacity: 1; } 100% { offset-distance: 100%; opacity: 0; } }
    .drop { animation: fall 1.1s linear infinite; }
    .d0 { animation-delay: 0s; } .d1 { animation-delay: .28s; }
    .d2 { animation-delay: .55s; } .d3 { animation-delay: .82s; }
    @keyframes fall { 0% { transform: translateY(0); opacity: .55; }
                      100% { transform: translateY(58px); opacity: 0; } }
    """
    lines = "".join('<text class="%s" x="180" y="%d">%s</text>'
                    % ("body" if i < 2 else "dim", 84 + i * 22, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>'
        '<path class="path" d="%s" fill="none" stroke="#2A3550" stroke-width="2"/>'
        '<g class="plane"><path d="M-10 -6 L10 0 L-10 6 L-6 0 Z" fill="#7FE7C4"/></g>'
        '<circle cx="70" cy="190" r="4" fill="#FFD166"/>'
        '<text class="dim" x="70" y="212" text-anchor="middle">%s</text>'
        '<circle cx="810" cy="165" r="4" fill="#39C2FF"/>'
        '<text class="dim" x="810" y="187" text-anchor="middle">%s</text>'
        '<g transform="translate(0,66)">%s</g>%s'
        % (esc(T["header"]), arc, esc(T["from"]), esc(T["to"]), rain, lines)
    )
    return panel("ch5-avion", W, 240, style=style, body=body)


# ════════════════════════════ cap 6 - el idioma ════════════════════════════
def ch6(T):
    subs = "".join('<text class="sub s%d" x="440" y="112" text-anchor="middle">%s</text>'
                   % (i, esc(s)) for i, s in enumerate(T["subs"]))
    style = """
    .sub { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 19px;
           fill: #C9D4E8; opacity: 0; animation: cycle 13s ease-in-out infinite; }
    .s0 { animation-delay: 0s; } .s1 { animation-delay: 3.25s; }
    .s2 { animation-delay: 6.5s; } .s3 { animation-delay: 9.75s; }
    @keyframes cycle { 0% { opacity: 0; } 4%,21% { opacity: 1; }
                       25% { opacity: 0; } 100% { opacity: 0; } }
    .bar { transform-origin: 34px 0; animation: creep 13s ease-out infinite; }
    @keyframes creep { 0% { transform: scaleX(.42); } 92% { transform: scaleX(.78); }
                       100% { transform: scaleX(.42); } }
    """
    body = (
        '<text class="hdr" x="34" y="44">%s</text>%s'
        '<rect x="34" y="146" width="812" height="8" rx="4" fill="#161B27" stroke="#2A3550"/>'
        '<rect class="bar" x="34" y="146" width="812" height="8" rx="4" fill="#7FE7C4"'
        ' opacity="0.8"/><text class="dim" x="34" y="180">%s</text>'
        % (esc(T["header"]), subs, esc(T["footer"]))
    )
    return panel("ch6-idioma", W, 210, style=style, body=body)


# ════════════════════════════ cap 8 - hoy ════════════════════════════
def ch8(T):
    out = []
    for i, row in enumerate(T["rows"]):
        cmd, res = row[0], row[1]
        y = 84 + i * 34
        out.append('<text class="cmd l%d" x="34" y="%d">%s</text>' % (i, y, esc(cmd))
                   + '<text class="res l%d" x="34" y="%d">%s</text>'
                     % (i, y + 16, esc("  " + res)))
    style = """
    .cmd { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 14px; fill: #7FE7C4; }
    .res { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 12px; fill: #C9D4E8; }
    .l0, .l1, .l2 { opacity: 0; animation: typ 7s steps(1) infinite; }
    .l0 { animation-delay: .2s; } .l1 { animation-delay: 1.4s; } .l2 { animation-delay: 2.6s; }
    @keyframes typ { 0% { opacity: 0; } 6%,92% { opacity: 1; } 100% { opacity: 0; } }
    .cur { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 0%,50% { opacity: 1; } 51%,100% { opacity: 0; } }
    """
    body = ('<text class="hdr" x="34" y="44">%s</text>%s'
            '<rect class="cur" x="34" y="190" width="9" height="2" fill="#FFD166"/>'
            % (esc(T["header"]), "".join(out)))
    return panel("ch7-levry", W, 215, style=style, body=body)


# ════════════════════════════ proyectos ════════════════════════════
def p_takegig(T):
    pins = [(180, 92), (300, 140), (420, 78), (560, 126), (680, 96), (760, 150)]
    marks = "".join(
        '<circle class="ping p%d" cx="%d" cy="%d" r="6" fill="none" stroke="#7FE7C4"'
        ' stroke-width="2"/><circle cx="%d" cy="%d" r="4" fill="#7FE7C4"/>'
        % (i, x, y, x, y) for i, (x, y) in enumerate(pins))
    grid = ("".join('<line x1="%d" y1="60" x2="%d" y2="176"/>' % (x, x)
                    for x in range(80, 860, 60))
            + "".join('<line x1="80" y1="%d" x2="850" y2="%d"/>' % (y, y)
                      for y in range(70, 180, 28)))
    style = """
    .ping { animation: ping 2.6s ease-out infinite; }
    .p0{animation-delay:0s} .p1{animation-delay:.42s} .p2{animation-delay:.84s}
    .p3{animation-delay:1.26s} .p4{animation-delay:1.68s} .p5{animation-delay:2.1s}
    @keyframes ping { 0% { r: 6; opacity: .9; } 100% { r: 24; opacity: 0; } }
    .you { animation: bob 2.2s ease-in-out infinite; }
    @keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
    .grid line { stroke: #1B2437; stroke-width: 1; }
    """
    body = (
        '<text class="hdr" x="34" y="44">%s</text><g class="grid">%s</g>%s'
        # el marcador propio: pin chico y etiqueta al costado, no texto adentro
        '<g transform="translate(470,108)"><g class="you">'
        '<circle r="13" fill="none" stroke="#FFD166" stroke-width="2" opacity="0.5"/>'
        '<circle r="6" fill="#FFD166"/>'
        '<text x="21" y="5" font-family="SF Mono, Menlo, monospace" font-size="12"'
        ' fill="#FFD166">%s</text></g></g>'
        '<text class="dim" x="34" y="196">%s</text>'
        % (esc(T["header"]), grid, marks, esc(T["you"]), esc(T["footer"]))
    )
    return panel("p-takegig", W, 215, style=style, body=body)


def p_buensabor(T):
    out = []
    for i, row in enumerate(T["layers"]):
        name, note = row[0], row[1]
        y = 70 + i * 38
        out.append('<rect x="140" y="%d" width="240" height="28" rx="5" fill="#161B27"'
                   ' stroke="#2A3550"/>'
                   '<text class="body" x="156" y="%d" fill="#7FE7C4">%s</text>'
                   '<text class="dim" x="400" y="%d">%s</text>'
                   % (y, y + 19, esc(name), y + 19, esc(note)))
    style = """
    .pkt { animation: flow 5s ease-in-out infinite; }
    @keyframes flow { 0% { transform: translateY(0); opacity: 0; } 8% { opacity: 1; }
                      92% { opacity: 1; } 100% { transform: translateY(138px); opacity: 0; } }
    """
    body = ('<text class="hdr" x="34" y="44">%s</text>%s'
            '<g class="pkt"><circle cx="118" cy="84" r="5" fill="#FFD166"/></g>'
            '<text class="dim" x="34" y="248">%s</text>'
            % (esc(T["header"]), "".join(out), esc(T["footer"])))
    return panel("p-elbuensabor", W, 262, style=style, body=body)


def p_tripulacion(T):
    cells = "".join('<rect x="%d" y="%d" width="34" height="34" rx="4" fill="#161B27"'
                    ' stroke="#2A3550"/>' % (34 + c * 40, 70 + r * 40)
                    for r in range(3) for c in range(7))
    style = """
    .tok { animation: hop 6s steps(1) infinite; }
    @keyframes hop { 0% { transform: translate(0,0); } 16% { transform: translate(40px,0); }
      32% { transform: translate(80px,0); } 48% { transform: translate(120px,0); }
      64% { transform: translate(160px,0); } 80% { transform: translate(200px,0); }
      100% { transform: translate(240px,0); } }
    .die { animation: roll 6s ease-in-out infinite; }
    @keyframes roll { 0%,100% { transform: rotate(0deg); } 12% { transform: rotate(96deg); }
                      24% { transform: rotate(-12deg); } }
    """
    lines = "".join('<text class="%s" x="420" y="%d">%s</text>'
                    % ("body" if i == 0 else "dim", 88 + i * 22, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>%s'
        '<g class="tok"><circle cx="51" cy="87" r="10" fill="#FFD166"/></g>'
        '<g transform="translate(360,92)"><g class="die">'
        '<rect x="-17" y="-17" width="34" height="34" rx="6" fill="#1B2437" stroke="#7FE7C4"/>'
        '<circle cx="-7" cy="-7" r="2.6" fill="#7FE7C4"/>'
        '<circle cx="7" cy="7" r="2.6" fill="#7FE7C4"/>'
        '<circle cx="0" cy="0" r="2.6" fill="#7FE7C4"/></g></g>%s'
        % (esc(T["header"]), cells, lines)
    )
    return panel("p-latripulacion", W, 215, style=style, body=body)


def egg_guitarra(T):
    strings = "".join('<line x1="60" y1="%d" x2="560" y2="%d" stroke="#2A3550"'
                      ' stroke-width="1.4"/>' % (72 + i * 17, 72 + i * 17)
                      for i in range(6))
    frets = "".join('<line x1="%d" y1="66" x2="%d" y2="163" stroke="#1B2437"'
                    ' stroke-width="2"/>' % (60 + i * 71, 60 + i * 71) for i in range(8))
    dots = [(202, 89), (273, 106), (131, 123), (344, 72)]
    marks = "".join('<circle class="note n%d" cx="%d" cy="%d" r="6" fill="#FFD166"/>'
                    % (i, x, y) for i, (x, y) in enumerate(dots))
    style = """
    .note { opacity: 0; animation: press 4.2s ease-in-out infinite; }
    .n0{animation-delay:0s} .n1{animation-delay:.5s}
    .n2{animation-delay:1s} .n3{animation-delay:1.5s}
    @keyframes press { 0% { opacity: 0; } 10%,60% { opacity: 1; } 100% { opacity: 0; } }
    .mus { animation: rise 4s ease-out infinite; }
    .m1 { animation-delay: 1.2s; } .m2 { animation-delay: 2.4s; }
    @keyframes rise { 0% { transform: translateY(0) rotate(0deg); opacity: 0; }
                      20% { opacity: .9; }
                      100% { transform: translateY(-46px) rotate(16deg); opacity: 0; } }
    """
    lines = "".join('<text class="body" x="600" y="%d">%s</text>' % (86 + i * 22, esc(s))
                    for i, s in enumerate(T["lines"]))
    body = (
        '<text class="hdr" x="34" y="44">%s</text>%s%s%s'
        '<g fill="#7FE7C4" font-family="serif" font-size="22">'
        '<text class="mus" x="600" y="150">%s</text>'
        '<text class="mus m1" x="628" y="150">%s</text>'
        '<text class="mus m2" x="656" y="150">%s</text></g>%s'
        '<text class="dim" x="34" y="196">%s</text>'
        % (esc(T["header"]), strings, frets, marks,
           esc("\u266a"), esc("\u266b"), esc("\u266a"), lines, esc(T["footer"]))
    )
    return panel("egg-guitarra", W, 215, style=style, body=body)


# ════════════════════════════ final ════════════════════════════
def final(T):
    stars = "".join('<circle class="star t%d" cx="%d" cy="%d" r="2.4" fill="#FFD166"/>'
                    % (i % 4, x, y) for i, (x, y) in enumerate(
                        [(120, 70), (250, 52), (380, 84), (640, 60),
                         (760, 88), (540, 46), (180, 150), (700, 152)]))
    style = """
    .star { animation: tw 2.4s ease-in-out infinite; }
    .t0{animation-delay:0s} .t1{animation-delay:.6s}
    .t2{animation-delay:1.2s} .t3{animation-delay:1.8s}
    @keyframes tw { 0%,100% { opacity: .2; transform: scale(.8); }
                    50% { opacity: 1; transform: scale(1.3); } }
    .done { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-weight: 800;
            font-size: 42px; letter-spacing: 3px; text-anchor: middle; fill: url(#chrome); }
    .route { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 13px;
             letter-spacing: 3px; text-anchor: middle; fill: #FFD166;
             animation: blink 1.5s steps(1) infinite; }
    @keyframes blink { 0%,60% { opacity: 1; } 61%,100% { opacity: 0; } }
    """
    body = ('%s<text class="done" x="440" y="112" filter="url(#glow)">%s</text>'
            '<text class="route" x="440" y="150">%s</text>'
            % (stars, esc(T["done"]), esc(T["route"])))
    return panel("final", W, 200, style=style, body=body, bulbs="all")


CH_FN = {"mendoza": ch1, "utn": ch2, "challenge": ch3, "escala": ch4,
         "avion": ch5, "idioma": ch6, "hoy": ch8}
PR_FN = {"takegig": p_takegig, "elbuensabor": p_buensabor,
         "latripulacion": p_tripulacion, "guitarra": egg_guitarra}


def main():
    total = 0
    for lang in STORY["langs"]:
        set_out_dir(ROOT / "assets" / lang)
        made = []
        for key, fn in (("title", title), ("mapa", mapa), ("final", final)):
            made.append(fn(STORY["standalone_art"][key][lang]).name)
        for ch in STORY["chapters"]:
            fn = CH_FN.get(ch["id"])
            if fn and ch["art"] and not ch.get("hidden"):
                made.append(fn(ch["art_text"][lang]).name)
        for pid, pr in STORY["projects"].items():
            if pr.get("hidden"):
                continue
            fn = PR_FN.get(pid)
            if fn:
                made.append(fn(pr["art_text"][lang]).name)
        print("[%s] %2d paneles -> assets/%s/" % (lang, len(made), lang))
        total += len(made)
    print("\n%d SVG generados y validados" % total)


if __name__ == "__main__":
    main()
