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

# Métricas
def ngramas(tokens, n=3):
    """Devuelve el conjunto de n-gramas (tuplas de n tokens consecutivos)."""
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(tokens_a, tokens_b, n=3):
    """Similitud de Jaccard entre dos secuencias, sobre sus n-gramas."""
    a = ngramas(tokens_a, n)
    b = ngramas(tokens_b, n)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def distancia_levenshtein(a, b):
    """Cantidad mínima de inserciones, borrados y reemplazos de tokens
    para convertir la secuencia `a` en `b` (programación dinámica)."""
    anterior = list(range(len(b) + 1))
    for i, tok_a in enumerate(a, start=1):
        actual = [i]
        for j, tok_b in enumerate(b, start=1):
            costo = 0 if tok_a == tok_b else 1
            actual.append(min(
                anterior[j] + 1,          # borrar tok_a
                actual[j - 1] + 1,        # insertar tok_b
                anterior[j - 1] + costo,  # reemplazar (o coincidir)
            ))
        anterior = actual
    return anterior[-1]


def levenshtein_normalizada(tokens_a, tokens_b):
    """Similitud en [0, 1] basada en la distancia de edición."""
    mayor = max(len(tokens_a), len(tokens_b))
    if mayor == 0:
        return 1.0
    return 1 - distancia_levenshtein(tokens_a, tokens_b) / mayor

# Motor de búsqueda
N = 3  # tamaño de n-grama para Jaccard

# Cada métrica con su umbral de "candidata a duplicado"
METRICAS = {
    "jaccard": (lambda a, b: jaccard(a, b, N), 0.40),
    "levenshtein": (levenshtein_normalizada, 0.45),
}

def buscar_similares(objetivo, candidatas, top_k=5, metrica="jaccard"):
    """Devuelve las top_k funciones más similares a `objetivo` como lista
    de (score, FuncionExtraida), usando la métrica indicada."""
    from normalizacion import normalizar

    funcion_metrica, _ = METRICAS[metrica]
    tokens_obj = serializar(normalizar(objetivo.nodo))
    resultados = []
    for fn in candidatas:
        if fn is objetivo:
            continue
        tokens_fn = serializar(normalizar(fn.nodo))
        resultados.append((funcion_metrica(tokens_obj, tokens_fn), fn))
    resultados.sort(key=lambda r: r[0], reverse=True)
    return resultados[:top_k]


if __name__ == "__main__":
    from extraccion import extraer_funciones

    funciones = extraer_funciones("Ejemplos")
    objetivo = next(f for f in funciones if f.nombre == "suma_lista")

    for metrica, (_, umbral) in METRICAS.items():
        print(f"\n=== {metrica} (umbral {umbral}) ===")
        for score, fn in buscar_similares(objetivo, funciones, top_k=5, metrica=metrica):
            marca = "  <-- candidata a duplicado" if score >= umbral else ""
            print(f"{score:.2f}  {fn.archivo}:{fn.nombre} (línea {fn.linea}){marca}")