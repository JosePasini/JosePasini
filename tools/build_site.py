#!/usr/bin/env python3
"""Copia el contenido del juego dentro de docs/ para que GitHub Pages lo sirva.

Correr: python3 tools/build_site.py

GENERADO, NO EDITAR A MANO:
    el <script id="story-data"> de docs/index.html  <- content/story.json
    docs/assets/                                    <- copia de assets/

Pages solo puede servir lo que este dentro de docs/, de ahi la copia del arte.

Cualquier cambio de texto o de arte va en content/story.json o en assets/ y
despues se corre este script. Lo que se edita a mano es solo el sitio en si:
docs/index.html, docs/style.css y docs/app.js.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = ROOT / "content" / "story.json"
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"


def embed_story(raw: str) -> bool:
    """Mete el JSON dentro del <script id="story-data"> de docs/index.html."""
    page = DOCS / "index.html"
    if not page.exists():
        print(f"no encuentro {page}", file=sys.stderr)
        return False

    html = page.read_text(encoding="utf-8")
    open_tag = '<script id="story-data" type="application/json">'
    close_tag = "</script>"
    i = html.find(open_tag)
    if i == -1:
        print('falta <script id="story-data"> en docs/index.html', file=sys.stderr)
        return False
    j = html.find(close_tag, i)

    # Un "</" dentro del script cerraria la etiqueta antes de tiempo; escaparlo
    # sigue siendo JSON valido.
    payload = json.dumps(json.loads(raw), ensure_ascii=False,
                         separators=(",", ":")).replace("</", "<\\/")
    page.write_text(html[:i + len(open_tag)] + payload + html[j:], encoding="utf-8")
    print(f"story.json  -> incrustado en docs/index.html ({len(payload)} bytes)")
    return True


def main() -> int:
    if not STORY.exists():
        print(f"no encuentro {STORY}", file=sys.stderr)
        return 1

    DOCS.mkdir(parents=True, exist_ok=True)

    # El texto va incrustado en la pagina, no como archivo aparte: asi
    # index.html se abre directo desde el disco, sin servidor, y se evita
    # tener una segunda copia del JSON dando vueltas.
    raw = STORY.read_text(encoding="utf-8")
    json.loads(raw)                      # que no se publique un JSON roto
    if not embed_story(raw):
        return 1

    stale = DOCS / "story.json"          # sobra desde que va incrustado
    if stale.exists():
        stale.unlink()

    # assets/: se borra y se vuelve a copiar entero, asi no quedan huerfanos.
    dest = DOCS / "assets"
    if dest.exists():
        shutil.rmtree(dest)

    if ASSETS.exists():
        shutil.copytree(ASSETS, dest)
        svgs = sorted(p.relative_to(dest) for p in dest.rglob("*.svg"))
        print(f"assets/     -> docs/assets/ ({len(svgs)} svg)")
        for lang_dir in sorted(p for p in dest.iterdir() if p.is_dir()):
            n = len(list(lang_dir.glob("*.svg")))
            print(f"              {lang_dir.name}/: {n} svg")
    else:
        dest.mkdir(parents=True, exist_ok=True)
        print("assets/     -> no existe todavia, docs/assets/ queda vacio")

    # Sin esto, GitHub Pages pasa todo por Jekyll.
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
