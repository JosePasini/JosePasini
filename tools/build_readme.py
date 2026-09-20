"""Genera README.md (ingles) y README.es.md (espanol) desde content/story.json.

Scroll cinematografico: nada plegado, nada escondido. Cada capitulo es un panel
animado seguido de su texto, y se lee de arriba a abajo.

Correr: python3 tools/build_readme.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORY = json.loads((ROOT / "content" / "story.json").read_text(encoding="utf-8"))
GAME_URL = "https://josepasini.github.io/JosePasini/"
FILES = {"en": "README.md", "es": "README.es.md"}


def art(lang, name, alt, href=None):
    # GitHub envuelve cada <img> en un link al archivo del repo. El <a> lo
    # pisa: sin href el click no va a ningun lado; con href va a donde pidamos.
    img = '<img src="assets/%s/%s.svg" width="880" alt="%s">' % (lang, name, alt)
    if href:
        return '<a href="%s">%s</a>' % (href, img)
    return '<a>%s</a>' % img


def L(node, lang):
    """Saca el valor del idioma pedido, tolerando strings planos."""
    if isinstance(node, dict):
        return node[lang]
    return node


def project_block(pid, pr, lang, ui):
    name = L(pr["name"], lang)
    out = []
    # El panel ya dice PROJECT / NOMBRE, asi que el encabezado no lo repite.
    out.append("#### %s" % name)
    out.append("*%s*" % L(pr["tagline"], lang))
    out.append("")
    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, pr["art"], name))
    out.append("")
    out.append("</div>")
    out.append("")
    for para in L(pr["body"], lang):
        out.append(para)
        out.append("")
    bits = []
    if pr["stack"]:
        bits.append(" &nbsp;·&nbsp; ".join("`%s`" % s for s in pr["stack"]))
    if pr["url"]:
        verb = ui["live"][lang] if pr["url_kind"] == "live" else ui["open_code"][lang]
        bits.append("**[%s &rarr;](%s)**" % (verb, pr["url"]))
    if bits:
        out.append(" &nbsp;&nbsp;|&nbsp;&nbsp; ".join(bits))
        out.append("")
    return out


def chapter_block(ch, lang, ui):
    out = []
    num = "%s %d" % (ui["chapter"][lang], ch["num"])
    out.append('<a id="%s"></a>' % ch["id"])
    out.append("")
    out.append("### %s &nbsp;·&nbsp; %s" % (num, L(ch["title"], lang)))
    out.append("*%s*" % L(ch["tagline"], lang))
    out.append("")
    if ch["art"]:
        out.append('<div align="center">')
        out.append("")
        out.append(art(lang, ch["art"], L(ch["title"], lang)))
        out.append("")
        out.append("</div>")
        out.append("")
    for para in L(ch["body"], lang):
        out.append(para)
        out.append("")
    if ch.get("table"):
        head = L(ch["table"]["head"], lang)
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "|".join([" --- "] * len(head)) + "|")
        for name, url, desc, stack in ch["table"]["rows"]:
            out.append("| [**%s**](%s) | %s | %s |" % (name, url, L(desc, lang), stack))
        out.append("")
    for pid in ch["projects"]:
        pr = STORY["projects"][pid]
        if pr.get("hidden"):
            continue
        out += project_block(pid, pr, lang, ui)
    return out


def build(lang):
    ui, other = STORY["ui"], ("es" if lang == "en" else "en")
    out = []

    # ── marquesina ──
    out.append('<div align="center">')
    out.append("")
    game = GAME_URL + ("" if lang == "en" else "?lang=es")
    out.append(art(lang, "title", "Jose Pasini", href=game))
    out.append("")
    out.append("**%s**" % L(STORY["intro"]["hook"], lang))
    out.append("")
    out.append("[**%s**](%s%s) &nbsp;&nbsp;·&nbsp;&nbsp; [%s](%s) &nbsp;&nbsp;·&nbsp;&nbsp; [%s](#cv)"
               % (ui["play"][lang], GAME_URL, "" if lang == "en" else "?lang=es",
                  ui["lang_switch"][lang], FILES[other], ui["cv_title"][lang]))
    out.append("")
    out.append("</div>")
    out.append("")
    out.append(L(STORY["intro"]["body"], lang))
    out.append("")

    # ── mapa ──
    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, "mapa", ui["the_run"][lang]))
    out.append("")
    out.append("</div>")
    out.append("")

    # ── indice de capitulos ──
    # Ojo: markdown NO se procesa dentro de un bloque HTML, asi que los enlaces
    # del indice van como <a> y no como [texto](#ancla).
    idx = " &nbsp;·&nbsp; ".join(
        '<a href="#%s">%d. %s</a>' % (c["id"], c["num"], L(c["title"], lang))
        for c in STORY["chapters"] if not c.get("hidden"))
    out.append('<div align="center"><sub><b>%s</b> &nbsp;&mdash;&nbsp; %s</sub></div>'
               % (ui["menu"][lang], idx))
    out.append("")

    # ── capitulos ──
    for ch in STORY["chapters"]:
        if ch.get("hidden"):
            continue
        out.append("---")
        out.append("")
        out += chapter_block(ch, lang, ui)

    # ── final ──
    out.append("---")
    out.append("")
    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, "final", ui["the_run"][lang]))
    out.append("")
    out.append("**%s**" % L(STORY["ui"]["outro"], lang))
    out.append("")
    links = STORY["links"]
    out.append('[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](%s)'
               % links["linkedin"])
    out.append("&nbsp;")
    out.append('[![Email](https://img.shields.io/badge/Email-7FE7C4?style=for-the-badge&logo=gmail&logoColor=0a0d13)](%s)'
               % links["email"])
    out.append("&nbsp;")
    out.append('[![LeetCode](https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](%s)'
               % links["leetcode"])
    out.append("")
    out.append("[**%s**](%s%s)" % (ui["play"][lang], GAME_URL,
                                   "" if lang == "en" else "?lang=es"))
    out.append("")
    out.append("</div>")
    out.append("")

    # ── el perfil aburrido, sin plegar ──
    out.append("---")
    out.append("")
    out.append('<a id="cv"></a>')
    out.append("")
    out.append("### %s" % ui["cv_title"][lang])
    out.append("")
    out.append(L(STORY["boring"]["summary"], lang))
    out.append("")
    for label, value in STORY["boring"]["stack"]:
        out.append("- **%s** &nbsp; %s" % (L(label, lang), value))
    out.append("")

    return "\n".join(out)


def main():
    for lang, fname in FILES.items():
        text = build(lang)
        (ROOT / fname).write_text(text, encoding="utf-8")
        print("%-14s %5d bytes  %3d lineas" % (fname, len(text), text.count("\n")))


if __name__ == "__main__":
    main()
