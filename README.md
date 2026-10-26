# Motor de búsqueda de funciones similares vía AST

Trabajo Práctico grupal — **Lenguajes Formales y Autómatas**, UCSE 2026.

Herramienta que recorre un directorio con archivos `.py`, extrae todas las funciones
definidas, las representa mediante su **Árbol de Sintaxis Abstracta (AST) normalizado**
y busca cuáles son *estructuralmente* similares a una función dada. Replica a escala
reducida el principio detrás de herramientas reales de detección de código duplicado
(SonarQube, PMD/CPD) o de similitud entre entregas (MOSS, JPlag).

La idea de fondo: el AST que devuelve `ast.parse` es el **árbol de derivación** de la
gramática de Python aplicada al código fuente. Comparar funciones por su AST es
comparar árboles de derivación, no strings.

## Requisitos

- Python 3.9 o superior (se usa `ast.unparse`, disponible desde 3.9).
- Sin dependencias externas para la herramienta.
- `pytest` solo para correr la suite de tests:

```
pip install pytest
```

## Uso

```
python buscar_similares.py --dir <directorio> --funcion <archivo.py:nombre> [--top N] [--metrica jaccard|levenshtein]
```

| Opción | Descripción | Default |
| --- | --- | --- |
| `--dir` | Directorio a recorrer recursivamente buscando `.py` | *(requerido)* |
| `--funcion` | Función objetivo, formato `archivo.py:nombre` | *(requerido)* |
| `--top` | Cantidad de resultados a mostrar | `5` |
| `--metrica` | Métrica de similitud a usar | `jaccard` |

### Ejemplo

```
python buscar_similares.py --dir ./Ejemplos --funcion a.py:suma_lista --top 8
```

```
Objetivo: Ejemplos/a.py:suma_lista (línea 1)
Métrica: jaccard | umbral: 0.4 | top: 8

1.00  Ejemplos/b.py:acumular (línea 1)              <-- candidata a duplicado
1.00  Ejemplos/d.py:suma_con_base (línea 14)        <-- candidata a duplicado
1.00  Ejemplos/d.py:suma_documentada (línea 22)     <-- candidata a duplicado
0.75  Ejemplos/d.py:invertir_cadena (línea 65)      <-- candidata a duplicado
0.70  Ejemplos/c.py:suma_positivos (línea 12)       <-- candidata a duplicado
0.49  Ejemplos/d.py:contar_pares (línea 47)         <-- candidata a duplicado
0.48  Ejemplos/c.py:suma_y_cuenta (línea 2)         <-- candidata a duplicado
0.47  Ejemplos/d.py:factorial (línea 56)            <-- candidata a duplicado
```

`invertir_cadena` es un falso positivo conocido y está explicado en el informe: tras
normalizar, lo único que la separa de `suma_lista` es el orden de los operandos del
`BinOp`, porque `""` y `0` quedaron reducidos a `LIT` y el `+` es el mismo nodo `Add`.

## Estructura

```
extraccion.py        # recorre el directorio y extrae las FunctionDef / AsyncFunctionDef
normalizacion.py     # NodeTransformer: variables -> VARn, literales -> LIT, nombre -> FUNC
similitud.py         # serialización pre-order del AST + métricas + motor de búsqueda
buscar_similares.py  # interfaz de línea de comandos
explore_AST.py       # exploración previa del módulo ast (ast.dump / walk / unparse)
Ejemplos/            # repositorio de prueba: 17 funciones con clones y no-clones
tests/               # suite de pytest
```

Cada módulo es ejecutable por separado (`python normalizacion.py`, etc.) y muestra su
etapa del pipeline sobre `Ejemplos/`, útil para inspeccionar el proceso paso a paso.

## Cómo funciona

1. **Extracción** — `os.walk` + `ast.parse` sobre cada `.py`. Devuelve toda `FunctionDef`
   y `AsyncFunctionDef` (incluidas anidadas y métodos) con nombre, archivo, línea y
   subárbol. Los archivos con error de sintaxis se saltean con un aviso.
2. **Normalización** — sobre una copia del subárbol (`copy.deepcopy`), un
   `ast.NodeTransformer` reemplaza variables y parámetros por `VAR1`, `VAR2`, ... en
   orden de primera aparición (preservando las correspondencias dentro de la función),
   los literales por `LIT`, y el nombre de la función por `FUNC`. Se descartan docstrings
   y anotaciones de tipo. Los builtins (`print`, `len`, `range`, ...) se conservan.
3. **Serialización** — recorrido **pre-order** recursivo con `ast.iter_child_nodes` que
   produce una lista lineal de tokens (tipo de nodo + valor normalizado en `Name`, `arg`
   y `Constant`). No se usa `ast.walk` porque recorre por niveles y pierde el orden
   estructural del árbol.
4. **Búsqueda** — compara el objetivo contra todas las demás funciones (todos-contra-todos,
   O(n²)), ordena por score y devuelve el top-K.

## Métricas y umbrales

| Métrica | Fórmula | Umbral | Costo por par |
| --- | --- | --- | --- |
| **Jaccard** (default) | sobre trigramas (n=3) de la secuencia de tokens | `0.40` | O(L) |
| Levenshtein normalizada | `1 - distancia / max(len(a), len(b))` | `0.45` | O(L²) |

Por encima del umbral, dos funciones se reportan como **candidatas a duplicado**. La
justificación de `n=3`, la calibración de los umbrales y la comparación de precisión y
recall entre ambas métricas están en el informe.

## Tests

```
pytest
```

La suite cubre 2 casos positivos (clon con variables renombradas, clon con líneas
reordenadas) y 2 casos negativos (`es_par`, `saludar`), verificados contra las dos
métricas y sus umbrales.

## Limitaciones conocidas

La herramienta funciona como **filtro de candidatas para revisión humana**, no como
detector exacto. En resumen:

- Falsos positivos por esqueleto compartido (`inicializar → for → actualizar → return`).
- No detecta cambios en la estructura del bucle (`for` reescrito como `while`).
- No detecta clones semánticos (`sum(numeros)` vs. el bucle acumulador equivalente).
- Los atributos (`self.total`) no se normalizan, y `x % 2 == 0` y `x % 3 == 1` quedan
  iguales por efecto de `LIT`.
- Los umbrales se calibraron con un único objetivo y 17 funciones: son estimaciones.

El detalle completo, con los scores medidos de cada caso y las mejoras posibles, está en
el informe.

## Informe

`Informe TP Motor de búsqueda de funciones similares vía AST.docx` — decisiones de
diseño, métrica elegida y por qué, validación con precisión y recall, limitaciones y
mejoras posibles.

## Integrantes

- Valentina Cravero
- Nicolás Miretti
