def saludar(nombre):
    """Genera un saludo personalizado.
    
    Args:
        nombre (str): El nombre de la persona a saludar.
    
    Returns:
        str: Un mensaje de saludo que incluye el nombre proporcionado.
    """
    return f"Hola, {nombre}!"

def sumar_lista(numeros):
    """Calcula la suma total de los números en una lista.
    
    Args:
        numeros (list): Una lista de números a sumar.
    
    Returns:
        int or float: La suma total de todos los números en la lista.
    """
    total = 0
    for n in numeros:
        total += n
    return total

def es_palindromo(texto):
    """Verifica si un texto es un palíndromo ignorando espacios y mayúsculas.
    
    Args:
        texto (str): El texto a verificar.
    
    Returns:
        bool: True si el texto es un palíndromo, False en caso contrario.
    """
    texto_limpio = texto.lower().replace(" ", "")
    return texto_limpio == texto_limpio[::-1]