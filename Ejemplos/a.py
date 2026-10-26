def suma_lista(numeros):
    total = 0
    for n in numeros:
        total = total + n
    return total


def es_par(x):
    if x % 2 == 0:
        return True
    return False