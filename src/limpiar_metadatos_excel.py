"""Quita de un .xlsx los metadatos que revelan datos del equipo: la ruta absoluta donde se guardó por última vez y el
campo «último en modificar». No toca las hojas, las fórmulas ni los valores calculados.

Uso:  python src/limpiar_metadatos_excel.py [ruta.xlsx]     (por defecto excel/Inditex_Valoracion.xlsx)
Ejecutar siempre DESPUÉS de guardar el libro en Excel, porque Excel vuelve a escribir esos datos al guardar.
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def limpiar(ruta: Path) -> None:
    tmp = ruta.with_suffix(".tmp")
    with zipfile.ZipFile(ruta) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "xl/workbook.xml":
                txt = data.decode("utf-8")
                # Bloque <mc:AlternateContent> que contiene x15ac:absPath (ruta absoluta de la carpeta)
                txt = re.sub(r"<mc:AlternateContent[^>]*>\s*<mc:Choice[^>]*>\s*<x15ac:absPath[^>]*/>\s*</mc:Choice>\s*</mc:AlternateContent>", "", txt)
                data = txt.encode("utf-8")
            elif item.filename == "docProps/core.xml":
                txt = data.decode("utf-8")
                txt = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", "<cp:lastModifiedBy></cp:lastModifiedBy>", txt)
                data = txt.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(ruta)


if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "excel" / "Inditex_Valoracion.xlsx"
    limpiar(destino)
    print("metadatos limpiados en", destino)
