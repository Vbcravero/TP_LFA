def acumular(valores):
    resultado = 0
    for v in valores:
        resultado = resultado + v
    return resultado


def saludar(nombre):
    print("Hola " + nombre)