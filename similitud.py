import ast


def serializar(nodo):
    """Recorrido pre-order del AST normalizado -> lista de tokens."""
    tokens = []
    _visitar(nodo, tokens)
    return tokens


def _visitar(nodo, tokens):
    # 1) El nodo en sí: su tipo
    tokens.append(type(nodo).__name__)

    # 2) Tokens propios del nodo (los valores normalizados)
    if isinstance(nodo, ast.Name):
        tokens.append(nodo.id)          # VAR1, VAR2...
    elif isinstance(nodo, ast.arg):
        tokens.append(nodo.arg)         # VAR1, VAR2...
    elif isinstance(nodo, ast.Constant):
        tokens.append(str(nodo.value))  # LIT

    # 3) Los hijos, en orden
    for hijo in ast.iter_child_nodes(nodo):
        _visitar(hijo, tokens)


if __name__ == "__main__":
    from extraccion import extraer_funciones
    from normalizacion import normalizar

    for fn in extraer_funciones("ejemplos"):
        tokens = serializar(normalizar(fn.nodo))
        print(f"--- {fn.nombre} ({len(tokens)} tokens) ---")
        print(tokens)
        print()