# -*- coding: utf-8 -*-
# Valida varios ficheros de datos contra file.schema.json.
#
# El schema muestra varias caracteristicas de JSON Schema:
#   1) "$ref" a otro fichero (geo.schema.json) para warehouseLocation, asi
#      que hay que enseñarle a jsonschema donde buscar los ficheros
#      referenciados.
#   2) "$defs" con definiciones reutilizables dentro del propio schema
#      (positiveNumber, manufacturer), referenciadas con "#/$defs/...".
#   3) "format": "date" y "format": "email", que solo se comprueban si le
#      pasamos al validador un FormatChecker.
#
# Necesita la libreria jsonschema:  pip install jsonschema

import json
import os

import jsonschema
from referencing import Registry, Resource

CARPETA_SCHEMAS = "schemas"
FICHERO_SCHEMA = "file.schema.json"

# Ficheros de datos que vamos a validar contra ese mismo schema.
FICHEROS_DATOS = [
    "file.json",
    "file_invalido.json",
]


def leer_json(ruta):
    """Lee un fichero JSON y lo devuelve convertido en datos de Python."""
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def buscar_schema(nombre):
    """
    jsonschema llama a esta funcion cuando un schema hace "$ref" a otro
    fichero. Recibe el nombre referenciado (por ejemplo "geo.schema.json")
    y devuelve su contenido leido de la carpeta schemas/.
    """
    return Resource.from_contents(leer_json(os.path.join(CARPETA_SCHEMAS, nombre)))


# El "registro" es la agenda donde jsonschema busca los schemas externos.
registro = Registry(retrieve=buscar_schema)

schema = leer_json(os.path.join(CARPETA_SCHEMAS, FICHERO_SCHEMA))

# file.schema.json usa JSON Schema 2020-12, asi que usamos ese validador
# directamente. Le pasamos el registro (para el "$ref" externo) y un
# FormatChecker (para que se comprueben los "format": "date"/"email").
validador = jsonschema.Draft202012Validator(
    schema,
    registry=registro,
    format_checker=jsonschema.FormatChecker(),
)

for fichero_datos in FICHEROS_DATOS:

    datos = leer_json(fichero_datos)

    # iter_errors devuelve TODOS los errores (lista vacia si el fichero es valido).
    errores = list(validador.iter_errors(datos))

    print(f"{fichero_datos}  (schema: {FICHERO_SCHEMA})")

    if len(errores) == 0:
        print("   VALIDO")
    else:
        print(f"   NO VALIDO ({len(errores)} errores)")
        for error in errores:
            # json_path dice donde esta el fallo ($ = el documento entero,
            # $.dimensions.length = el campo length dentro de dimensions)
            # y message explica que regla se ha incumplido.
            print(f"   {error.json_path} -> {error.message}")

    print()
