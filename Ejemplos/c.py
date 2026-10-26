# Clone con líneas reordenadas
def suma_y_cuenta(lista):
    cantidad = 0
    total = 0
    for x in lista:
        total = total + x
        cantidad = cantidad + 1
    return total


# Clone con una modificación pequeña (agrega una condición)
def suma_positivos(lista):
    total = 0
    for x in lista:
        if x > 0:
            total = total + x
    return total