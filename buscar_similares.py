import argparse
import os
import sys

from extraccion import extraer_funciones
from similitud import buscar_similares, METRICAS


def parsear_argumentos():
    p = argparse.ArgumentParser(
        description="Busca funciones estructuralmente similares vía AST."
    )
    p.add_argument("--dir", required=True,
                   help="directorio a recorrer (busca .py recursivamente)")
    p.add_argument("--funcion", required=True,
                   help="función objetivo, con formato archivo.py:nombre")
    p.add_argument("--top", type=int, default=5,
                   help="cantidad de resultados (default: 5)")
    p.add_argument("--metrica", choices=METRICAS.keys(), default="jaccard",
                   help="métrica de similitud (default: jaccard)")
    return p.parse_args()


def encontrar_objetivo(funciones, spec):
    """Busca la función indicada como 'archivo.py:nombre'."""
    if ":" not in spec:
        sys.exit("Error: --funcion debe tener el formato archivo.py:nombre")
    archivo, nombre = spec.rsplit(":", 1)
    archivo = os.path.normpath(archivo)

    coincidencias = [
        f for f in funciones
        if f.nombre == nombre
        and os.path.normpath(f.archivo).endswith(archivo)
    ]
    if not coincidencias:
        sys.exit(f"Error: no se encontró la función '{spec}' en el directorio.")
    return coincidencias[0]


def main():
    args = parsear_argumentos()

    funciones = extraer_funciones(args.dir)
    if not funciones:
        sys.exit(f"No se encontraron funciones en '{args.dir}'.")

    objetivo = encontrar_objetivo(funciones, args.funcion)
    _, umbral = METRICAS[args.metrica]

    print(f"Objetivo: {objetivo.archivo}:{objetivo.nombre} (línea {objetivo.linea})")
    print(f"Métrica: {args.metrica} | umbral: {umbral} | top: {args.top}\n")

    for score, fn in buscar_similares(objetivo, funciones, args.top, args.metrica):
        marca = "  <-- candidata a duplicado" if score >= umbral else ""
        print(f"{score:.2f}  {fn.archivo}:{fn.nombre} (línea {fn.linea}){marca}")


if __name__ == "__main__":
    main()