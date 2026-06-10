def saludar(nombre):
    return f"Hola, {nombre}!"

def sumar_lista(numeros):
    total = 0
    for n in numeros:
        total += n
    return total

def es_palindromo(texto):
    texto_limpio = texto.lower().replace(" ", "")
    return texto_limpio == texto_limpio[::-1]
