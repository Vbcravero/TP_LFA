import ast
import copy


class Normalizador(ast.NodeTransformer):
    def __init__(self):
        self.mapa = {}  # nombre original -> "VARn"

    def _token(self, nombre):
        if nombre not in self.mapa:
            self.mapa[nombre] = f"VAR{len(self.mapa) + 1}"
        return self.mapa[nombre]

    def visit_FunctionDef(self, nodo):
        nodo.name = "FUNC"  # el nombre de la función no debe influir
        self.generic_visit(nodo)
        return nodo

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_arg(self, nodo):
        nodo.arg = self._token(nodo.arg)
        nodo.annotation = None  # ignoramos anotaciones de tipo
        return nodo

    def visit_Name(self, nodo):
        nodo.id = self._token(nodo.id)
        return nodo

    def visit_Constant(self, nodo):
        nodo.value = "LIT"
        return nodo


def normalizar(nodo_funcion):
    """Devuelve una COPIA normalizada del AST de una función."""
    copia = copy.deepcopy(nodo_funcion)
    return Normalizador().visit(copia)


if __name__ == "__main__":
    from extraccion import extraer_funciones

    for fn in extraer_funciones("ejemplos"):
        arbol = normalizar(fn.nodo)
        ast.fix_missing_locations(arbol)
        print(f"--- {fn.nombre} ---")
        print(ast.unparse(arbol))
        print()