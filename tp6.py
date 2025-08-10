"""PSEUDOCODIGO
ACCION multiplos11 es
  AMBIENTE
    miles, centenas, decenas, unidades: entero
  PROCESO
    Para num := 1000 hasta 10000 hacer:
      miles := num DIV(1000)
      centenas := (num DIV(100)) MOD(10)
      decenas := (num DIV(100)) MOD(10)
      unidades := num MOD(10)
      Si (miles + centenas) = (decenas + unidades) entonces
        escribir("El número ", num, " es divisible por 11")
      Fin Si
    Fin Para
Fin ACCION
"""

def multiplos11():
  for num in range(1000, 10000):
    miles = int(num / 1000)
    centenas = int((num / 100) % 10)
    decenas = int((num / 10) % 10)
    unidades = int(num % 10)
    if (miles + centenas) == (decenas + unidades):
      print("El numero",num," es divisible por 11")
multiplos11()