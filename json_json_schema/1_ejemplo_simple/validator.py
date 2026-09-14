# -*- coding: utf-8 -*-
# Valida catalogo.json contra las reglas de catalogo.schema.json.
# Aqui el fichero de datos es UN SOLO documento (un objeto), no una lista,
# asi que no hace falta recorrer nada: se valida de una vez.
# Necesita la libreria jsonschema:  pip install jsonschema

import json
import jsonschema

# 1) Leemos los dos ficheros JSON.
with open("catalogo.schema.json", encoding="utf-8") as f:
    schema = json.load(f)

with open("catalogo.json", encoding="utf-8") as f:
    catalogo = json.load(f)

# 2) Creamos el validador.
# El FormatChecker es opcional: sin el, las reglas "format" (como "date")
# se ignoran. Lo ponemos para que la fecha se compruebe de verdad.
validador = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())

# 3) iter_errors devuelve TODOS los errores del documento (lista vacia si es valido).
errores = list(validador.iter_errors(catalogo))

if len(errores) == 0:
    print("catalogo.json: VALIDO")
else:
    print(f"catalogo.json: NO VALIDO ({len(errores)} errores)")
    for error in errores:
        # json_path dice donde esta el fallo ($ = el documento entero,
        # $.productos[0].precio = el precio del primer producto)
        # y message explica que regla se ha incumplido.
        print(f"   {error.json_path} -> {error.message}")
