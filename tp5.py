"""PSEUDOCODIGO
ACCION EncontrarNum es 
  AMBIENTE
    c : CARACTER
    PROCEDIMIENTO EncontrarDig(char: CARACTER) ES
      SI char = "0" o char = "1" o char = "2" o char = "3" o char = "4" o char = "5" o char = "6" o char = "7" o char = "8" o char = "9" ENTONCES
        escribir("El caracter es un dígito")
      SINO:
        escribir("El caracter no es un dígito")
      FIN SI
    FIN PROCEDIMIENTO
  PROCESO
    escribir("Introduzca el caracter a comparar:")
    leer(c)
    EncontrarDig(c)
FIN ACCION
"""

nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def ComparCar(caracter):
  if caracter in nums:
    print("El caracter es un dígito")
  else:
    print("El caracter no es un dígito")

def EncontrarNum():
  c = input("Introduzca el caracter a comparar: ")
  ComparCar(c)

EncontrarNum()