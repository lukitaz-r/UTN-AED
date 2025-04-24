"""PSEUDOCODIGO
ACCION envios es
  AMBIENTE
    precioInicial, precioFinal: REAL
    PISO_ENVIO = 10000.00
    ADICIONAL = 800.00
  PROCESO
    Escribir("Ingrese el precio del producto: ")
    Leer(precioInicial)
    Si (precioInicial >  PISO_ENVIO)
      Escribir("Tu envío es gratis 🚚💨")
      precioFinal := precioInicial
    Sino
      Escribir("Tu envio tendrá un coste agregado de: $",  ADICIONAL, " 🚚💨")
      precioFinal := precioInicial +  ADICIONAL
    Escribir("El precio final es de: $", precioFinal)
"""

def envios():
  PISO_ENVIO = 10000.0
  ADICIONAL = 800.0
  precioFinal = 0
  precioInicial = float(input("Ingrese el precio del producto: "))
  if (precioInicial > PISO_ENVIO):
    print("Tu envío es gratis 🚚💨")
    precioFinal = precioInicial
  else:
    print("Tu envio tendrá un coste agregado de: $",  ADICIONAL, "🚚💨")
    precioFinal = precioInicial +  ADICIONAL
  print("El precio final es de: $", precioFinal)

envios()

# $ python tp2.py
# Ingrese el precio del producto: 700
# Tu envio tendrá un coste agregado de: $ 800.0  🚚💨
# El precio final es de: $ 1500.0