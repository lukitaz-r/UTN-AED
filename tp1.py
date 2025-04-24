import math

"""PSEUDOCODIGO
ACCION precioFuturo es
  AMBIENTE
    precioActual, precioFuturo: Real
    añoActual, añoFuturo: Entero
    inflacion = 0,04
  PROCESO
    Escribir("Este algoritmo calcula el precio futuro de un articulo")
    Escribir("Ingrese el precio actual del articulo")
    Leer(precioActual)
    Escribir("Ingrese el año actual")
    Leer(añoActual)
    Escribir("Ingrese el año futuro")
    Leer(añoFuturo)
    precioFuturo := precioActual * (1 + inflacion) ^ (añoFuturo - añoActual)
    Escribir("El precio futuro del articulo es: ", precioFuturo)
"""

def precioFuturo():
  print("Este algoritmo calcula el precio futuro de un articulo")
  precioActual = float(input("Ingrese el precio actual del articulo: "))
  añoActual = int(input("Ingrese el año actual: "))
  añoFuturo = int(input("Ingrese el año futuro: "))
  inflacion = 0.04
  precioFuturo = precioActual * (1 + inflacion) ** (añoFuturo - añoActual)
  print("El precio futuro del articulo es: ", (precioFuturo))

# precioFuturo()

"""PSEUDOCODIGO
ACCION calcDiscriminante es
  AMBITO
    a, b, c, discriminante: REAL
  PROCESO
    Escribir("Este programa te ayuda a calcular el discriminante de una función cuadratica, por favor siga las instrucciones al pie de la letra.")
    Escribir("Introduzca el valor de 'a':")
    Leer(a)
    Escribir("Introduzca el valor de 'b':")
    Leer(b)
    Escribir("Introduzca el valor de 'c':")
    Leer(c)
    discriminante := b**2 - 4*a*c
    Escribir("El valor del discriminante es:", discriminante)
"""

def calDiscriminante():
  print("Este programa te ayuda a calcular el discriminante de una función cuadratica, por favor siga las instrucciones al pie de la letra.")
  a = float(input("Introduzca el valor de 'a': "))
  b = float(input("Introduzca el valor de 'b': "))
  c = float(input("Introduzca el valor de 'c': "))
  discriminante = b**2 - 4*a*c
  print("El valor del discriminante es:", discriminante)

calDiscriminante()