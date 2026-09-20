"""Genera README.md (ingles) y README.es.md (espanol) desde content/story.json.

El README es la marquesina: titulo, mapa, anclas al juego y el CV corto.
La historia vive en GitHub Pages, no aca.

Correr: python3 tools/build_readme.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORY = json.loads((ROOT / "content" / "story.json").read_text(encoding="utf-8"))
GAME_URL = "https://josepasini.github.io/JosePasini/"
FILES = {"en": "README.md", "es": "README.es.md"}


def game_url(lang, chapter=None):
    q = "" if lang == "en" else "?lang=es"
    h = ("#ch=%s" % chapter) if chapter else ""
    return GAME_URL + q + h


def art(lang, name, alt, href=None):
    # GitHub envuelve cada <img> en un link al archivo del repo. El <a> lo
    # pisa: sin href el click no va a ningun lado; con href va a donde pidamos.
    img = '<img src="assets/%s/%s.svg" width="880" alt="%s">' % (lang, name, alt)
    if href:
        return '<a href="%s">%s</a>' % (href, img)
    # GitHub descarta <a> vacio y pone el link al archivo. #cv deja el click aca.
    return '<a href="#cv">%s</a>' % img


def L(node, lang):
    if isinstance(node, dict):
        return node[lang]
    return node


def badge(name):
    logos = {
        "Java": "openjdk", "Go": "go", "Spring Boot": "springboot", "Python": "python",
        "Node.js": "nodedotjs", "PostgreSQL": "postgresql", "MySQL": "mysql",
        "MongoDB": "mongodb", "BigQuery": "googlebigquery", "SQLite": "sqlite",
        "TypeScript": "typescript", "React": "react", "Next.js": "nextdotjs",
        "Vue": "vuedotjs", "Docker": "docker", "GraphQL": "graphql",
        "Vercel": "vercel", "Jenkins": "jenkins", "Datadog": "datadog",
        "Kibana": "kibana", "Grafana": "grafana",
    }
    label = name.strip()
    msg = label.replace("-", "--").replace("_", "__").replace(" ", "%20")
    logo = logos.get(label)
    extra = ("&logo=%s&logoColor=7FE7C4" % logo) if logo else ""
    return ('<a href="#cv"><img src="https://img.shields.io/badge/%s-161B27?style=for-the-badge%s" alt="%s"></a>'
            % (msg, extra, label))


def cat_badge(name):
    # Menta, no el negro de las tecnologias: el titulo tiene que ganarle a los chips.
    msg = name.strip().upper().replace("-", "--").replace(" ", "%20")
    return ('<a href="#cv"><img src="https://img.shields.io/badge/%s-7FE7C4?style=for-the-badge&color=7FE7C4" alt="%s"></a>'
            % (msg, name))


def build(lang):
    ui, other = STORY["ui"], ("es" if lang == "en" else "en")
    play = game_url(lang)
    out = []

    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, "title", "Jose Pasini", href=play))
    out.append("")
    out.append("**%s**" % L(STORY["intro"]["hook"], lang))
    out.append("")
    out.append("[**%s**](%s) &nbsp;&nbsp;·&nbsp;&nbsp; [%s](%s) &nbsp;&nbsp;·&nbsp;&nbsp; [%s](#cv)"
               % (ui["play"][lang], play, ui["lang_switch"][lang], FILES[other],
                  ui["cv_title"][lang]))
    out.append("")
    out.append("</div>")
    out.append("")
    out.append(L(STORY["intro"]["body"], lang))
    out.append("")

    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, "mapa", ui["the_run"][lang], href=play))
    out.append("")
    out.append("</div>")
    out.append("")

    idx = " &nbsp;·&nbsp; ".join(
        '<a href="%s">%d. %s</a>' % (game_url(lang, c["id"]), c["num"], L(c["title"], lang))
        for c in STORY["chapters"] if not c.get("hidden"))
    out.append('<div align="center"><sub><b>%s</b> &nbsp;&mdash;&nbsp; %s</sub></div>'
               % (ui["menu"][lang], idx))
    out.append("")

    out.append("---")
    out.append("")
    out.append('<div align="center">')
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
    out.append("</div>")
    out.append("")

    out.append("---")
    out.append("")
    out.append('<a id="cv"></a>')
    out.append("")
    out.append("### %s" % ui["cv_title"][lang])
    out.append("")
    out.append('<div align="center">')
    out.append("")
    out.append(art(lang, "cv", ui["cv_title"][lang]))
    out.append("")
    out.append("</div>")
    out.append("")
    out.append(L(STORY["boring"]["summary"], lang))
    out.append("")
    out.append("| | |")
    out.append("| :---: | :--- |")
    for label, value in STORY["boring"]["stack"]:
        chips = " ".join(badge(p.strip()) for p in value.split(",") if p.strip())
        out.append("| %s | %s |" % (cat_badge(L(label, lang)), chips))
    out.append("")

    return "\n".join(out)


def main():
    for lang, fname in FILES.items():
        text = build(lang)
        (ROOT / fname).write_text(text, encoding="utf-8")
        print("%-14s %5d bytes  %3d lineas" % (fname, len(text), text.count("\n")))


if __name__ == "__main__":
    main()
