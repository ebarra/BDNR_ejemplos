# -*- coding: utf-8 -*-
"""
=======================================================================
  EJEMPLO: VALIDAR UN ARRAY DE DOCUMENTOS CON JSON SCHEMA
=======================================================================

Tenemos dos ficheros:

  * nave.schema.json -> las REGLAS (el JSON Schema) que debe cumplir la
                        ficha de UNA nave de la flota.
  * naves.json       -> una LISTA (array) con las fichas de varias naves.

Ojo a la idea clave: el schema describe UN documento, pero el fichero de
datos contiene MUCHOS. Por eso no se valida la lista de golpe: hay que
recorrerla y validar cada documento por separado.

De las naves del fichero solo UNA cumple todas las reglas. El programa
las revisa una a una y explica en castellano por que fallan las demas.

Para ejecutarlo:      python validator_completo.py
Necesita la libreria: pip install jsonschema
"""

import json
import os
import sys

import jsonschema


# Nombres de los ficheros de entrada. Si cambias de ejemplo, cambia solo
# estas dos lineas y el resto del programa sigue funcionando igual.
FICHERO_SCHEMA = "nave.schema.json"
FICHERO_DATOS = "naves.json"

# Como llamamos a cada documento cuando hablamos con el usuario.
NOMBRE_DOCUMENTO = "NAVE"

# Campo que usamos como "etiqueta" para reconocer cada documento.
CAMPO_ETIQUETA = "nombre"


# ---------------------------------------------------------------------
# 1) COLORES PARA LA CONSOLA
# ---------------------------------------------------------------------
# Los "codigos de escape ANSI" son textos magicos que la terminal no
# imprime, sino que interpreta como "a partir de aqui pinta en rojo".
# En Windows hay que despertar ese soporte con os.system("").

if os.name == "nt":
    os.system("")

ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
GRIS = "\033[90m"
NEGRITA = "\033[1m"
FIN = "\033[0m"          # vuelve al color normal

ANCHO = 70               # ancho de las lineas decorativas


def titulo(texto):
    """Imprime un titulo grande enmarcado en una caja."""
    print()
    print(AZUL + "=" * ANCHO + FIN)
    print(AZUL + NEGRITA + "  " + texto + FIN)
    print(AZUL + "=" * ANCHO + FIN)


def separador():
    """Imprime una linea fina de separacion."""
    print(GRIS + "-" * ANCHO + FIN)


# ---------------------------------------------------------------------
# 2) TRADUCTOR DE ERRORES
# ---------------------------------------------------------------------
# La libreria 'jsonschema' nos dice que regla se ha incumplido usando una
# palabra clave (validator): "type", "minimum", "required"...
# Este diccionario traduce esa palabra clave a una explicacion humana.

EXPLICACIONES = {
    "type":                 "El TIPO de dato no es el esperado (5 es numero, \"5\" es texto y true es booleano).",
    "minimum":              "El numero es DEMASIADO PEQUENO.",
    "maximum":              "El numero es DEMASIADO GRANDE.",
    "minLength":            "El texto es DEMASIADO CORTO (le faltan caracteres).",
    "maxLength":            "El texto es DEMASIADO LARGO.",
    "minItems":             "La lista tiene DEMASIADO POCOS elementos (puede estar vacia).",
    "maxItems":             "La lista tiene DEMASIADOS elementos.",
    "enum":                 "El valor no esta en la LISTA DE VALORES PERMITIDOS.",
    "pattern":              "El texto no encaja con el PATRON (expresion regular) exigido.",
    "required":             "FALTA un campo OBLIGATORIO.",
    "additionalProperties": "SOBRA un campo: el schema no permite campos extra.",
    "format":               "El formato del valor no es correcto.",
    "uniqueItems":          "Hay elementos REPETIDOS en la lista y no se permiten.",
}


def explicar(error):
    """Devuelve una frase en castellano que explica el error recibido."""
    return EXPLICACIONES.get(error.validator, "Regla incumplida: " + str(error.validator))


def campo_del_mensaje(mensaje):
    """
    Saca el nombre del campo que aparece entre comillas simples en el
    mensaje original de la libreria. Ejemplos de mensaje:
        'operativa' is a required property
        Additional properties are not allowed ('capitan' was unexpected)
    Devuelve None si el mensaje no lleva ningun nombre entrecomillado.
    """
    trozos = mensaje.split("'")
    if len(trozos) >= 3:
        return trozos[1]
    return None


def ruta_legible(error):
    """
    Convierte la ruta interna del error en algo comodo de leer.

    'error.path' es una cola con los pasos hasta el dato que falla.
    Por ejemplo, para el segundo elemento de destinos devuelve: destinos -> [1]
    Si la cola esta vacia, el fallo afecta al documento entero: en ese caso
    intentamos al menos nombrar el campo que falta o que sobra.
    """
    if len(error.path) == 0:
        culpable = campo_del_mensaje(error.message)
        if error.validator == "required" and culpable is not None:
            return "falta el campo '" + culpable + "'"
        if error.validator == "additionalProperties" and culpable is not None:
            return "sobra el campo '" + culpable + "'"
        return "(el documento completo)"

    pasos = []
    for paso in error.path:
        if isinstance(paso, int):
            pasos.append("[" + str(paso) + "]")   # posicion dentro de un array
        else:
            pasos.append(str(paso))               # nombre de un campo
    return " -> ".join(pasos)


def valor_legible(error):
    """
    Devuelve el valor concreto que ha provocado el error.
    Si el error afecta al documento entero no lo repetimos (ya se ha
    impreso mas arriba): basta con avisar de que es el documento completo.
    """
    if len(error.path) == 0:
        return "(el documento completo, ver arriba)"
    return json.dumps(error.instance, ensure_ascii=False)


# ---------------------------------------------------------------------
# 3) CARGA DE FICHEROS
# ---------------------------------------------------------------------
# Usamos encoding="utf-8" para que no den problemas las tildes ni la enye.

def cargar_json(nombre_fichero):
    """Lee un fichero JSON y lo convierte en datos de Python."""
    try:
        with open(nombre_fichero, "r", encoding="utf-8") as fichero:
            return json.load(fichero)
    except FileNotFoundError:
        print(ROJO + "ERROR: no encuentro el fichero '" + nombre_fichero + "'." + FIN)
        print("Ejecuta el programa desde la carpeta donde estan los ficheros.")
        sys.exit(1)
    except json.JSONDecodeError as problema:
        print(ROJO + "ERROR: '" + nombre_fichero + "' no es un JSON bien formado." + FIN)
        print("Detalle: " + str(problema))
        sys.exit(1)


# ---------------------------------------------------------------------
# 4) PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------

titulo("VALIDADOR DE LA FLOTA")

schema = cargar_json(FICHERO_SCHEMA)
documentos = cargar_json(FICHERO_DATOS)

print("Schema cargado ......: " + NEGRITA + FICHERO_SCHEMA + FIN)
print("Documentos cargados .: " + NEGRITA + str(len(documentos)) + FIN +
      " naves en " + FICHERO_DATOS)

# Recordamos que reglas hay que cumplir. Todo esto se saca leyendo el
# propio schema, asi que si cambias el schema este resumen cambia solo.
print()
print(AMARILLO + NEGRITA + "REGLAS QUE DEBE CUMPLIR UN DOCUMENTO VALIDO:" + FIN)
print("  * Campos obligatorios: " + ", ".join(schema["required"]))
print("  * No se admiten campos que no aparezcan en el schema.")

for campo, reglas in schema["properties"].items():
    # Mostramos cada campo con su tipo y sus restricciones adicionales.
    restricciones = []
    for clave, valor in reglas.items():
        if clave != "type":
            restricciones.append(str(clave) + "=" + json.dumps(valor, ensure_ascii=False))

    linea = "  * " + campo.ljust(14) + " tipo " + str(reglas.get("type"))
    if len(restricciones) > 0:
        linea = linea + "  |  " + ", ".join(restricciones)
    print(linea)

# Creamos el validador UNA sola vez y lo reutilizamos para cada documento.
# Usamos Draft202012Validator porque es la version que declara el schema.
validador = jsonschema.Draft202012Validator(schema)

validos = []   # aqui guardaremos los numeros de los documentos que pasen el filtro

titulo("REVISION DOCUMENTO A DOCUMENTO")

for posicion, documento in enumerate(documentos):

    # 'posicion' empieza en 0, pero a las personas les hablamos desde el 1.
    numero = posicion + 1
    etiqueta = documento.get(CAMPO_ETIQUETA, "(sin " + CAMPO_ETIQUETA + ")")

    separador()
    print(NEGRITA + NOMBRE_DOCUMENTO + " #" + str(numero) + "  ->  " + str(etiqueta) + FIN)

    # Mostramos el documento tal cual, con sangria, para poder mirarlo.
    print(GRIS + json.dumps(documento, indent=4, ensure_ascii=False) + FIN)

    # iter_errors() devuelve TODOS los errores del documento, no solo el
    # primero. sorted(...) los ordena para que la salida salga siempre igual.
    errores = sorted(validador.iter_errors(documento), key=str)

    if len(errores) == 0:
        print(VERDE + NEGRITA + "  [VALIDA] Cumple TODAS las reglas del schema." + FIN)
        validos.append(numero)
    else:
        print(ROJO + NEGRITA + "  [NO VALIDA] Errores encontrados: " + str(len(errores)) + FIN)

        for indice, error in enumerate(errores, start=1):
            print(ROJO + "   " + str(indice) + ") Campo afectado : " +
                  ruta_legible(error) + FIN)
            print("      Regla incumplida: " + NEGRITA + str(error.validator) + FIN +
                  " = " + json.dumps(error.validator_value, ensure_ascii=False))
            print("      Valor encontrado: " + valor_legible(error))
            print("      Que significa   : " + AMARILLO + explicar(error) + FIN)
            print("      Mensaje original: " + GRIS + error.message + FIN)

separador()


# ---------------------------------------------------------------------
# 5) RESUMEN FINAL
# ---------------------------------------------------------------------

titulo("RESUMEN")

total = len(documentos)
correctos = len(validos)

print("Documentos revisados ..: " + str(total))
print("Documentos validos ....: " + VERDE + str(correctos) + FIN)
print("Documentos rechazados .: " + ROJO + str(total - correctos) + FIN)
print()

if correctos == 1:
    ganador = documentos[validos[0] - 1]
    print(VERDE + NEGRITA + "RESULTADO" + FIN)
    print("El unico documento que valida contra el schema es el " +
          NEGRITA + "#" + str(validos[0]) + FIN + ": " +
          VERDE + NEGRITA + str(ganador[CAMPO_ETIQUETA]) + FIN)
elif correctos == 0:
    print(ROJO + NEGRITA + "Ningun documento ha superado la validacion." + FIN)
else:
    print(AMARILLO + NEGRITA + "Atencion: han pasado " + str(correctos) +
          " documentos: " + str(validos) + FIN)

print()
