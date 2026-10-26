# ---------- Clones de suma_lista (a.py) ----------

# Clon con while en vez de for (cambia la estructura del bucle)
def suma_con_while(numeros):
    total = 0
    i = 0
    while i < len(numeros):
        total = total + numeros[i]
        i = i + 1
    return total


# Clon con otra constante inicial: despues de normalizar (LIT) es identico
def suma_con_base(valores):
    acumulado = 100
    for v in valores:
        acumulado = acumulado + v
    return acumulado


# Clon con docstring (limitacion: el docstring suma tokens)
def suma_documentada(items):
    """Suma todos los elementos de la lista."""
    s = 0
    for it in items:
        s = s + it
    return s


# Clon semantico: hace lo mismo pero con otra estructura (no deberia detectarse)
def suma_builtin(numeros):
    return sum(numeros)


# ---------- No clones con forma parecida (casos dificiles) ----------

# Mismo esqueleto (acumulador + for + if) pero otro proposito
def maximo(numeros):
    mayor = numeros[0]
    for n in numeros:
        if n > mayor:
            mayor = n
    return mayor


# Parecida a suma_positivos, pero cuenta en vez de sumar
def contar_pares(numeros):
    cantidad = 0
    for n in numeros:
        if n % 2 == 0:
            cantidad = cantidad + 1
    return cantidad


# Acumulador + for, pero multiplica
def factorial(n):
    resultado = 1
    for i in range(2, n + 1):
        resultado = resultado * i
    return resultado


# ---------- No clones claramente distintos ----------

def invertir_cadena(texto):
    invertida = ""
    for c in texto:
        invertida = c + invertida
    return invertida


def buscar_indice(lista, objetivo):
    for i in range(len(lista)):
        if lista[i] == objetivo:
            return i
    return -1


def promedio(numeros):
    if len(numeros) == 0:
        return 0
    return sum(numeros) / len(numeros)


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a