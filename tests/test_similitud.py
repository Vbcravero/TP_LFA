import ast
import sys
import os

# Permite importar los módulos que están en la carpeta de arriba
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from normalizacion import normalizar
from similitud import serializar, jaccard, levenshtein_normalizada, METRICAS


def tokens(codigo):
    """Toma el código de UNA función y devuelve su secuencia de tokens normalizada."""
    nodo = ast.parse(codigo).body[0]
    return serializar(normalizar(nodo))


UMBRAL_JACCARD = METRICAS["jaccard"][1]
UMBRAL_LEV = METRICAS["levenshtein"][1]

BASE = """
def suma_lista(numeros):
    total = 0
    for n in numeros:
        total = total + n
    return total
"""


# ---------- Casos positivos (clones) ----------

def test_clon_con_variables_renombradas():
    clon = """
def acumular(valores):
    resultado = 0
    for v in valores:
        resultado = resultado + v
    return resultado
"""
    assert jaccard(tokens(BASE), tokens(clon)) == 1.0
    assert levenshtein_normalizada(tokens(BASE), tokens(clon)) == 1.0


def test_clon_con_lineas_reordenadas():
    clon = """
def suma_y_cuenta(lista):
    cantidad = 0
    total = 0
    for x in lista:
        total = total + x
        cantidad = cantidad + 1
    return total
"""
    assert jaccard(tokens(BASE), tokens(clon)) >= UMBRAL_JACCARD
    assert levenshtein_normalizada(tokens(BASE), tokens(clon)) >= UMBRAL_LEV


# ---------- Casos negativos (funciones distintas) ----------

def test_funciones_distintas_es_par():
    distinta = """
def es_par(x):
    if x % 2 == 0:
        return True
    return False
"""
    assert jaccard(tokens(BASE), tokens(distinta)) < UMBRAL_JACCARD
    assert levenshtein_normalizada(tokens(BASE), tokens(distinta)) < UMBRAL_LEV


def test_funciones_distintas_saludar():
    distinta = """
def saludar(nombre):
    print("Hola " + nombre)
"""
    assert jaccard(tokens(BASE), tokens(distinta)) < UMBRAL_JACCARD
    assert levenshtein_normalizada(tokens(BASE), tokens(distinta)) < UMBRAL_LEV