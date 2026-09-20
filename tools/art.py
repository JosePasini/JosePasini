"""Marco compartido para los paneles SVG del juego.

Todo el arte del README sale de acá, así que todas las escenas comparten
borde, paleta, tipografía y lamparitas de marquesina. La consistencia queda
garantizada por construcción, no por disciplina.

Regla dura: la salida es ASCII puro. Cualquier caracter no-ASCII se escribe
como entidad numérica XML, porque un byte crudo mal escrito rompe el SVG
entero y GitHub lo muestra como imagen quebrada.
"""

import pathlib
import xml.dom.minidom

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"


def set_out_dir(path):
    """Cambia el destino de los SVG, para emitir un set por idioma."""
    global OUT
    OUT = pathlib.Path(path)

# ─────────────────────────── paleta ───────────────────────────
C = {
    "bg_top": "#121721",
    "bg_bot": "#0a0d13",
    "frame": "#2A3550",
    "frame_in": "#1B2437",
    "text": "#C9D4E8",
    "muted": "#6B7A99",
    "amber": "#FFD166",
    "mint": "#7FE7C4",
    "cyan": "#39C2FF",
    "violet": "#7A3BFF",
    "red": "#FF5C7A",
    "panel": "#161B27",
}

MONO = '"SF Mono", Menlo, Consolas, "Courier New", monospace'
SANS = '"Helvetica Neue", Helvetica, Arial, sans-serif'


def esc(s):
    """Pasa cualquier caracter no-ASCII a entidad numérica."""
    out = []
    for ch in s:
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ord(ch) < 128:
            out.append(ch)
        else:
            out.append("&#%d;" % ord(ch))
    return "".join(out)


# defs y estilos que usa todo panel
COMMON_DEFS = """
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_top}"/>
      <stop offset="100%" stop-color="{bg_bot}"/>
    </linearGradient>
    <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8FE3FF"/>
      <stop offset="45%" stop-color="{cyan}"/>
      <stop offset="55%" stop-color="#1E6BFF"/>
      <stop offset="100%" stop-color="{violet}"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#ffffff" opacity="0.022"/>
    </pattern>
""".format(**C)

COMMON_STYLE = """
    .lbl {{ font-family: {mono}; font-size: 13px; letter-spacing: 3px; fill: {muted}; }}
    .hdr {{ font-family: {mono}; font-size: 17px; letter-spacing: 4px; fill: {mint}; }}
    .big {{ font-family: {sans}; font-weight: 800; font-size: 34px; letter-spacing: 2px; fill: url(#chrome); }}
    .body {{ font-family: {mono}; font-size: 13px; fill: {text}; }}
    .dim  {{ font-family: {mono}; font-size: 12px; fill: {muted}; }}
    .sweep {{ animation: sweep 6s ease-in-out infinite; }}
    @keyframes sweep {{
      0%   {{ transform: translateX(-900px); }}
      55%  {{ transform: translateX(900px); }}
      100% {{ transform: translateX(900px); }}
    }}
    /* Quien pidio menos movimiento ve el panel quieto. Apagar la animacion no
       alcanza: varios elementos arrancan invisibles y solo aparecen al animarse,
       asi que hay que fijarles el estado de reposo o el panel queda vacio.
       No se toca la opacidad en general, porque muchas formas dependen de una
       opacidad parcial deliberada. */
    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      .letter, .plane, .chk, .note, .mus,
      .l0, .l1, .l2 {{ opacity: 1 !important; }}
      .trace {{ stroke-dashoffset: 0 !important; }}
      .sub {{ opacity: 0 !important; }}
      .sub.s0 {{ opacity: 1 !important; }}
    }}
""".format(mono=MONO, sans=SANS, **C)


def panel(name, w, h, defs="", style="", body="", bulbs="top"):
    """Arma un panel completo y lo escribe validado en assets/.

    bulbs: "all" para las cuatro esquinas (pantalla de titulo), "top" para que
    no choquen con el texto al pie, "none" para nada.
    """
    bulb_markup = ""
    if bulbs != "none":
        pts = [(34, 26), (62, 26), (w - 62, 26), (w - 34, 26)]
        if bulbs == "all":
            pts += [(34, h - 26), (62, h - 26), (w - 62, h - 26), (w - 34, h - 26)]
        dots = "".join('<circle cx="%d" cy="%d" r="2.5"/>' % p for p in pts)
        bulb_markup = '<g fill="%s" opacity="0.7">%s</g>' % (C["amber"], dots)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{alt}">
  <defs>{common_defs}{defs}
    <clipPath id="clip"><rect width="{w}" height="{h}" rx="14"/></clipPath>
  </defs>
  <style>{common_style}{style}</style>

  <rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
  <rect x="1.5" y="1.5" width="{w1}" height="{h1}" rx="13" fill="none" stroke="{frame}" stroke-width="3"/>
  <rect x="13" y="13" width="{w2}" height="{h2}" rx="8" fill="none" stroke="{frame_in}" stroke-width="1.5"/>
  {bulbs}

  {body}

  <rect width="{w}" height="{h}" rx="14" fill="url(#scan)"/>
  <g clip-path="url(#clip)">
    <rect class="sweep" x="0" y="0" width="150" height="{h}" fill="#8FE3FF" opacity="0.04"/>
  </g>
</svg>
""".format(w=w, h=h, w1=w - 3, h1=h - 3, w2=w - 26, h2=h - 26,
           alt=esc(name.replace("-", " ")), common_defs=COMMON_DEFS, defs=defs,
           common_style=COMMON_STYLE, style=style, bulbs=bulb_markup, body=body,
           **C)

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / (name + ".svg")
    dest.write_text(svg, encoding="utf-8")

    # si no parsea, no se publica
    xml.dom.minidom.parse(str(dest))
    return dest
