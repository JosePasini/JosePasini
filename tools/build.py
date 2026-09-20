"""Regenera todo el perfil desde content/story.json.

    python3 tools/build.py

Orden: arte (los dos idiomas) -> READMEs -> copia para el sitio.
content/story.json es la unica fuente de texto. Nada de lo generado se edita a mano.
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
STEPS = [
    ("arte SVG, ingles y espanol", "build_art.py"),
    ("README.md y README.es.md", "build_readme.py"),
    ("copia para GitHub Pages", "build_site.py"),
]


def main():
    failed = []
    for label, script in STEPS:
        path = HERE / script
        if not path.exists():
            print("-- %-32s (falta %s, se omite)" % (label, script), flush=True)
            continue
        print("\n== %s ==" % label, flush=True)
        r = subprocess.run([sys.executable, str(path)], cwd=HERE.parent)
        if r.returncode != 0:
            failed.append(script)

    if failed:
        print("\nFALLARON: %s" % ", ".join(failed))
        return 1
    print("\nlisto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
