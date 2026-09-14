# -*- coding: utf-8 -*-
# Valida cada nave contra las reglas de nave.schema.json.
# A diferencia del ejemplo "jsonschema_validate_array", aqui las naves NO
# vienen todas juntas en un unico array: cada nave esta en su propio
# fichero .json dentro de la carpeta "naves".
# Asi que en lugar de recorrer una lista, recorremos los ficheros de esa
# carpeta y validamos uno a uno.
# Necesita la libreria jsonschema:  pip install jsonschema

import glob
import json
import jsonschema

CARPETA_NAVES = "naves"

# 1) Leemos el schema (las reglas), una sola vez.
with open("nave.schema.json", encoding="utf-8") as f:
    schema = json.load(f)

# 2) Creamos el validador una sola vez y lo reutilizamos.
validador = jsonschema.Draft202012Validator(schema)

# 3) Buscamos todos los ficheros .json de la carpeta de naves y los
#    ordenamos para que la salida sea siempre igual.
ficheros = sorted(glob.glob(f"{CARPETA_NAVES}/*.json"))

# 4) Recorremos los ficheros. enumerate nos da la posicion y el nombre.
for posicion, ruta in enumerate(ficheros, start=1):

    with open(ruta, encoding="utf-8") as f:
        nave = json.load(f)

    # iter_errors devuelve TODOS los errores de esta nave (lista vacia si es valida).
    errores = list(validador.iter_errors(nave))

    if len(errores) == 0:
        print(f"Nave {posicion} ({ruta}): VALIDA")
    else:
        print(f"Nave {posicion} ({ruta}): NO VALIDA")
        for error in errores:
            # json_path dice donde esta el fallo ($ = la nave entera)
            # y message explica que regla se ha incumplido.
            print(f"   {error.json_path} -> {error.message}")
