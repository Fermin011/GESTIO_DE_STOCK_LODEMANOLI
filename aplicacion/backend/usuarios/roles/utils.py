

import json

def lista_a_dict(claves: list, valores: list) -> dict:
    """
    Convierte dos listas (claves y valores) en un diccionario.
    Útil para generar el JSON de permisos a partir de listas.

    :param claves: Lista con los nombres de las claves.
    :param valores: Lista con los valores correspondientes.
    :return: Diccionario combinado.
    """
    if len(claves) != len(valores):
        raise ValueError("Las listas de claves y valores deben tener la misma longitud.")
    return dict(zip(claves, valores))