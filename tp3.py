"""
ACCIÓN descomposiciónNum es
  AMBITO
    num, unidades, decenas, centenas: ENTERO
  PROCESO
    Escribir("Introduzca el número a analizar: ")
    Leer(num)
    Si num >= 100 y num <= 1000 entonces
      centenas:= num DIV(100)
      decenas:= (num DIV(10)) MOD(10)
      unidades:= num MOD(10)
      Escribir("Las centenas son: ", centenas)
      Escribir("Las decenas son: ", decenas)
      Escribir("Las unidades son: ", unidades)
      Si num MOD(3) == 0 entonces
        Escribir("El número es múltiplo de 3")
      Sino
        Escribir("El número no es múltiplo de 3")
      FIN Si
    Sino
      Si num < 100 entonces
        Escribir("El número es menor a 100")
      Sino
        Escribir("El número es mayor a 1000")
      FIN Si
    FIN Si
FIN Accion
"""

def descomposicionNum():
  num = int(input("Introduzca el número a analizar: "))
  if (num >= 100 and num <= 1000):
    centenas = int(num % 100)
    decenas = int((num / 10) % 10)
    unidades = int(num % 10)
    print("Las centenas son: ", centenas)
    print("Las decenas son: ", decenas)
    print("Las unidades son: ", unidades)
    if (num % 3 == 0):
      print("El número es múltiplo de 3")
    else:
      print("El número no es múltiplo de 3")
  elif (num < 100):
    print("El número es menor a 100")
  else:
    print("El número es mayor a 1000")
descomposicionNum()
