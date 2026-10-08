"""Extrae balance, cuenta de resultados y flujos de efectivo de las cuentas anuales
consolidadas de Inditex (PDF en data/raw) a un CSV en formato largo.

Salida: data/processed/statements_long.csv
Columnas: pdf, statement, page, section, label, note, col, value
  col = 'current' (ejercicio del PDF) o 'prior' (comparativo).
"""
import re
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "statements_long.csv"

# (nombre, texto que identifica la pagina de datos, texto que identifica el fin)
STATEMENTS = {
    "pyg": "RESULTADOS DE EXPLOTACIÓN (EBIT)",
    "balance": "TOTAL ACTIVO",
    "flujos": "Flujos derivados de las actividades de explotación",
}

# Un '-' suelto en el PDF significa cero.
NUM = r"(?:\(?-?[\d]+(?:\.\d{3})*(?:,\d+)?\)?|-)"
ROW = re.compile(rf"^(?P<label>.+?)\s+(?:\((?P<note>\d{{1,2}})\)\s+|-\s+)?(?P<a>{NUM})\s+(?P<b>{NUM})$")


def to_number(token: str) -> float:
    if token == "-":
        return 0.0
    neg = token.startswith("(") and token.endswith(")")
    token = token.strip("()").replace(".", "").replace(",", ".")
    value = float(token)
    return -value if neg else value


def clean_label(label: str) -> str:
    return re.sub(r"^(?:-\s+)+", "", label).strip()


SECTION_HEADERS = {
    "ACTIVOS NO CORRIENTES", "ACTIVOS CORRIENTES", "PATRIMONIO NETO",
    "PASIVOS NO CORRIENTES", "PASIVOS CORRIENTES",
}


def parse_page(text: str):
    """Rows con su seccion del balance (p. ej. 'Deuda financiera' esta en PASIVOS NO CORRIENTES
    y tambien en PASIVOS CORRIENTES; sin la seccion no se pueden distinguir)."""
    section = ""
    for line in text.splitlines():
        m = ROW.match(line.strip())
        if not m:
            continue
        label = clean_label(m["label"])
        if label in ("", "-"):  # lineas de relleno '- - -'
            continue
        if label.upper() in SECTION_HEADERS:
            section = label.upper()
        yield section, label, m["note"], to_number(m["a"]), to_number(m["b"])


def find_pages(pdf, marker: str):
    """Paginas con el marcador, ignorando indices y notas (exige tabla con cifras)."""
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if marker in text and "(Cifras en millones de euros)" in text:
            yield i + 1, text


def main():
    rows = []
    for pdf_path in sorted(RAW.glob("CCAA_consolidadas_FY*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            for statement, marker in STATEMENTS.items():
                # Nos quedamos con la primera pagina que cumple: es el estado principal,
                # las notas posteriores repiten partidas sueltas.
                found = next(find_pages(pdf, marker), None)
                if not found:
                    print(f"AVISO {pdf_path.name}: no se encontro {statement}")
                    continue
                page_no, text = found
                for section, label, note, cur, pri in parse_page(text):
                    base = dict(pdf=pdf_path.name, statement=statement, page=page_no,
                                section=section, label=label, note=note)
                    rows.append({**base, "col": "current", "value": cur})
                    rows.append({**base, "col": "prior", "value": pri})
                print(f"OK {pdf_path.name}: {statement} (pag {page_no})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False, encoding="utf-8")
    print(f"\n{len(df)} filas -> {OUT}")


if __name__ == "__main__":
    main()
