# -*- coding: utf-8 -*-
# Valida cada nave de naves.json contra las reglas de nave.schema.json.
# El schema describe UNA nave, pero el fichero tiene una LISTA de naves,
# asi que hay que recorrer la lista y validar de una en una.
# Necesita la libreria jsonschema:  pip install jsonschema

import json
import jsonschema

# 1) Leemos los dos ficheros JSON.
with open("nave.schema.json", encoding="utf-8") as f:
    schema = json.load(f)

with open("naves.json", encoding="utf-8") as f:
    naves = json.load(f)

# 2) Creamos el validador una sola vez y lo reutilizamos.
validador = jsonschema.Draft202012Validator(schema)

# 3) Recorremos la lista. enumerate nos da la posicion y la nave.
for posicion, nave in enumerate(naves, start=1):

    # iter_errors devuelve TODOS los errores de esta nave (lista vacia si es valida).
    errores = list(validador.iter_errors(nave))

    if len(errores) == 0:
        print(f"Nave {posicion} ({nave['nombre']}): VALIDA")
    else:
        print(f"Nave {posicion} ({nave['nombre']}): NO VALIDA")
        for error in errores:
            # json_path dice donde esta el fallo ($ = la nave entera)
            # y message explica que regla se ha incumplido.
            print(f"   {error.json_path} -> {error.message}")
