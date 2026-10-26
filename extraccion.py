import ast
import os
from dataclasses import dataclass


@dataclass
class FuncionExtraida:
    nombre: str
    archivo: str
    linea: int
    nodo: ast.AST


def extraer_funciones(directorio):
    """Recorre recursivamente `directorio` y devuelve todas las funciones
    definidas en archivos .py."""
    funciones = []
    for raiz, _, archivos in os.walk(directorio):
        for nombre_archivo in archivos:
            if not nombre_archivo.endswith(".py"):
                continue
            ruta = os.path.join(raiz, nombre_archivo)
            funciones.extend(_extraer_de_archivo(ruta))
    return funciones


def _extraer_de_archivo(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            codigo = f.read()
        arbol = ast.parse(codigo, filename=ruta)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"[aviso] se saltea {ruta}: {e}")
        return []

    encontradas = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            encontradas.append(
                FuncionExtraida(
                    nombre=nodo.name,
                    archivo=ruta,
                    linea=nodo.lineno,
                    nodo=nodo,
                )
            )
    return encontradas


if __name__ == "__main__":
    for fn in extraer_funciones("ejemplos"):
        print(f"{fn.archivo}:{fn.nombre} (línea {fn.linea})")