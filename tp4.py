"""PSEUDOCODIGO
ACCION calcDesc():
  AMBIENTE
    precio, precioFinal: REAL
    Desc1 = 0.05
    Desc2 = 0.10
    minDesc1 = 20000
    minDesc2 = 35000
  PROCESO
    Para i:=1 hasta 20 hacer:
      esc("Introduzca el precio del ", i, "producto: ")
      leer(precio)
      Si precio >= minDesc1 y precio < minDes2 entonces:
        precioFinal := precio * (1 - Desc1)
      Sino
        Si precio >= minDesc2 entonces:
          precioFinal := precio * (1 - Desc2)
        Sino 
          precioFinal := precio
        Fin Si
      Fin Si
      esc("El precio final del producto es $", precioFinal)
    Fin Para
Fin ACCION
"""
def calcDesc():
  DESC1 = 0.95
  DESC2 = 0.90
  for i in range(1, 20, 1):
    print("Introduzca el precio del ", i, "producto: ")
    precio = float(input())
    if precio >= 20000 and precio < 35000:
      precio = precio * DESC1
    elif precio >= 35000:
      precio = precio * DESC2
    print("El precio final del producto es de: ", precio)
calcDesc()