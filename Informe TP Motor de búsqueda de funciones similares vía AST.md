# Informe TP: Motor de búsqueda de funciones similares vía AST

Lenguajes Formales y Autómatas 2026 · Oct 26, 2026 · @Valentina

## 1. Diseño

Comparamos funciones de Python por su estructura y no por su texto: el AST que genera `ast.parse` es el árbol de derivación de la gramática de Python aplicado al código, así que comparar ASTs es comparar árboles de derivación, no strings. El sistema es un pipeline de cuatro módulos:

1. **Extracción** (`extraccion.py`): `os.walk` más `ast.parse` sobre cada `.py`; devuelve toda `FunctionDef` y `AsyncFunctionDef` (incluidas anidadas y métodos) con nombre, archivo, línea y subárbol. Los archivos con errores de sintaxis se saltean con un aviso.
2. **Normalización** (`normalizacion.py`): un `ast.NodeTransformer` que elimina los nombres propios de cada función.
3. **Serialización** (`similitud.py`): un recorrido pre-order recursivo con `ast.iter_child_nodes` (`ast.walk` recorre por niveles, así que no sirve) que produce una lista de tokens: tipo de nodo más el valor normalizado en `Name`, `arg` y `Constant`.
4. **Similitud y búsqueda** (`similitud.py`, `buscar_similares.py`): compara la función objetivo contra todas las demás, ordena por score y devuelve las top-K. La CLI usa `--dir`, `--funcion archivo.py:nombre`, `--top` y `--metrica`.

## 2. Normalización

La normalización hace que funciones con la misma estructura queden idénticas aunque difieran en nombres y valores. Trabaja sobre una copia (`copy.deepcopy`), porque `NodeTransformer` modifica el árbol in situ.

- **Variables y parámetros** (`Name`, `arg`): `VAR1`, `VAR2`, ... en orden de primera aparición, con un diccionario por función que preserva las correspondencias.
- **Literales**: números y strings pasan a `LIT`; dos funciones que solo difieren en una constante son candidatas razonables a duplicado.
- **Nombre de la función**: `FUNC`. También se descartan las anotaciones de tipo y los **docstrings**.
- **Builtins** (`print`, `len`, `range`...): se conservan sin normalizar (`dir(builtins)`), para que `print(x)` y `len(x)` no se vean iguales.

Efecto medido: quitar el docstring llevó a `suma_documentada` de 0.79 a 1.00 en Jaccard y de 0.92 a 1.00 en Levenshtein. Conservar builtins tuvo un efecto chico (`saludar` bajó de 0.11 a 0.08 en Jaccard), porque nuestros ejemplos casi no los usan.

## 3. Métrica y umbral

La métrica principal es la similitud de Jaccard sobre trigramas (n=3) de la secuencia de tokens, con umbral 0.40. Como alternativa implementamos la distancia de Levenshtein normalizada (`1 - distancia / max(len(a), len(b))`), con umbral 0.45, seleccionable con `--metrica`.

**Por qué n-gramas y no tokens sueltos.** Con tokens sueltos, dos funciones con los mismos nodos en distinto orden darían 1.0. Los n-gramas capturan qué nodo sigue a cuál, y como un cambio local solo rompe los n-gramas de su frontera, toleran bien el reordenamiento de líneas.

**Elección de n.** En un primer conjunto de 6 funciones probamos n=2, 3 y 4. Con n=2 los no clones llegaron a 0.29 por coincidencias casuales (por ejemplo `Return → Name`); con n=4 el clon con líneas reordenadas cayó a 0.32, demasiado cerca del ruido. Con n=3 los no clones quedaron en 0.11 o menos y los clones en 0.48 o más.

**Validación con 17 funciones** (objetivo: `suma_lista`; umbrales: Jaccard 0.40, Levenshtein 0.45). Ampliamos `ejemplos/` con casos difíciles a propósito; las etiquetas son criterio nuestro.

| Grupo | Funciones | Jaccard (n=3) | Levenshtein |
| --- | --- | --- | --- |
| Clones exactos tras normalizar | `acumular`, `suma_con_base`, `suma_documentada` | 1.00 | 1.00 |
| Clones con cambios | `suma_positivos` / `suma_y_cuenta` / `suma_con_while` | 0.70 / 0.48 / 0.33 | 0.80 / 0.56 / 0.52 |
| Clon semántico | `suma_builtin` | 0.09 | 0.24 |
| No clones, mismo esqueleto | `invertir_cadena` / `contar_pares` / `factorial` / `maximo` | 0.75 / 0.49 / 0.47 / 0.37 | 0.94 / 0.66 / 0.74 / 0.67 |
| No clones distintos | `fibonacci`, `buscar_indice`, `saludar`, `es_par`, `promedio` | 0.26 a 0.06 | 0.57 a 0.24 |

**Precisión y recall.** Se consideran clones las 6 funciones estructuralmente equivalentes (`acumular`, `suma_con_base`, `suma_documentada`, `suma_positivos`, `suma_y_cuenta`, `suma_con_while`). `suma_builtin` es un clon semántico y queda fuera del recall.

| Métrica y umbral | Marcadas como candidatas | Precisión | Recall |
| --- | --- | --- | --- |
| Jaccard 0.30 | 10 | 0.60 | 1.00 |
| **Jaccard 0.40 (elegido)** | 8 | 0.63 | 0.83 |
| Jaccard 0.50 | 5 | 0.80 | 0.67 |
| Levenshtein 0.45 | 11 | 0.55 | 1.00 |

Ya no existe un umbral que separe clones de no clones. Jaccard con 0.40 es un compromiso: detecta 5 de 6 clones con 3 falsos positivos (`invertir_cadena`, `contar_pares`, `factorial`); subir el umbral pierde clones reales y bajarlo suma falsos positivos. Levenshtein separa peor: `invertir_cadena` (0.94) puntúa más alto que clones legítimos como `suma_y_cuenta` (0.56). Por eso Jaccard es la métrica por defecto. La causa es la normalización: muchas funciones comparten el esqueleto «inicializar, `for`, actualizar, `return`» y difieren solo en un operador o en el orden de los operandos, así que la herramienta sirve como filtro de candidatas para revisión humana, priorizando no perder clones sobre la precisión.

**Costo.** Jaccard es O(L) por par de funciones (L = cantidad de tokens) y Levenshtein es O(L²), por la programación dinámica. Con decenas de archivos la diferencia no se nota.

**Validación.** Los umbrales se calibraron con un único objetivo (`suma_lista`) y 17 funciones, así que son estimaciones y no valores validados sobre repositorios reales. La suite de tests (`pytest`) verifica 2 casos positivos (variables renombradas, líneas reordenadas) y 2 negativos (`es_par`, `saludar`) con ambas métricas.

## 4. Limitaciones conocidas

La herramienta detecta bien clones con identificadores renombrados y cambios pequeños, pero con falsos positivos y varios tipos de clon que no detecta:

- **Falsos positivos por esqueleto compartido**: `invertir_cadena` 0.75, `contar_pares` 0.49 y `factorial` 0.47 contra `suma_lista` (Jaccard).
- **Cambios en la estructura del bucle**: `suma_con_while` da 0.33 en Jaccard y no se detecta.
- **Clones semánticos**: `suma_builtin`, que usa `sum()`, da 0.09.
- **Normalización incompleta**: las funciones propias llamadas se normalizan como variables, los atributos (`self.total`) no se normalizan, y `x % 2 == 0` y `x % 3 == 1` son iguales por el `LIT`.
- **Reordenamiento y alcance**: reordenar líneas baja el score (`suma_y_cuenta` da 0.48), y solo se comparan funciones completas, no bloques.
- **Implementación**: umbrales calibrados con 17 funciones y un solo objetivo; la CLI toma la primera coincidencia si hay nombres repetidos, no permite pegar el código, y la búsqueda es O(n²).

## 5. Mejoras posibles

- **Ponderar los n-gramas** (por ejemplo con TF-IDF), para que los del esqueleto común pesen menos y bajen falsos positivos como `invertir_cadena`.
- **Canonicalizar construcciones equivalentes** (un `for` sobre una lista y un `while` con índice) y **normalizar atributos**.
- **Validar los umbrales** con repositorios reales y más objetivos etiquetados a mano, midiendo precisión y recall.
- **Comparar sub-bloques** y no solo funciones completas, y agregar una opción `--codigo` para pasar el código objetivo desde un archivo.
- **Escalar la búsqueda** con MinHash o un índice invertido, para evitar la comparación todos-contra-todos.
