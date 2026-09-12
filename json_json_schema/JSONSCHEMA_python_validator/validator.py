# -*- coding: utf-8 -*-
# Valida varios ficheros de datos, cada uno contra su schema de la carpeta schemas/.
#
# Dos cosas nuevas respecto a otros ejemplos mas sencillos:
#   1) Los dos schemas usan versiones distintas de JSON Schema (draft-04 y
#      2020-12), asi que dejamos que la libreria elija el validador adecuado.
#   2) file.schema.json hace "$ref" a otro schema (geo.schema.json), asi que
#      hay que enseñarle a jsonschema donde buscar los ficheros referenciados.
#
# Necesita la libreria jsonschema:  pip install jsonschema

import json
import os

import jsonschema
from referencing import Registry, Resource

CARPETA_SCHEMAS = "schemas"

# Que fichero de datos hay que validar contra que schema.
PAREJAS = [
    ("example.json", "example.schema.json"),
    ("file.json", "file.schema.json"),
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

for fichero_datos, fichero_schema in PAREJAS:

    datos = leer_json(fichero_datos)
    schema = leer_json(os.path.join(CARPETA_SCHEMAS, fichero_schema))

    # validator_for mira el "$schema" del fichero y elige la version correcta
    # de JSON Schema. Luego creamos el validador pasandole el registro.
    ClaseValidador = jsonschema.validators.validator_for(schema)
    validador = ClaseValidador(schema, registry=registro)

    # iter_errors devuelve TODOS los errores (lista vacia si el fichero es valido).
    errores = list(validador.iter_errors(datos))

    print(f"{fichero_datos}  (schema: {fichero_schema}, {ClaseValidador.__name__})")

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
