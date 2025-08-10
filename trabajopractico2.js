/*1.01.Dada una secuencia de letras del alfabeto que finaliza con una marca '*', contar cuantas letras "A" hay en la
secuencia.
Accion contA es
  Ambiente 
    alf: secuencia de caracter
    letra: caracter
    cont: entero
  Proceso
    cont:=0
    arrancar(alf)
    avanzar(alf, letra)
    mientras letra <> "*" hacer
      si letra = "A" entonces
          cont:=cont+1
      fin si
      avanzar(alf, letra)
    fin mientras
    escribir("La cantidad de letras A que hay en la secuencia es: ", cont)
Fin Accion
*/

const arr = "ABSCDRKSASJDJKESASSESAA3IESAAASKAAAJAESJAAAJASEAJAAAEOPLSALDER*"
let i = 0
let contA = 1
while (arr[i] !== "*") { 
  console.log(arr[i])
  if (arr[i] === "A") {
    contA = contA + 1
  } 
  i = i + 1
}
console.log(`Hay ${contA} letras A en la secuencia
  `)
 

/*1.02.Dada una secuencia de letras del alfabeto que finaliza con la letra "Z", contar cuantas consonantes hay en la
secuencia.

Accion ContSonantes es
  Ambiente
    Vocales= ("A","E","I","O,"U")
    sec: secuencia de caracter
    n: caracter
    cont: entero
  Proceso
    ARR(sec)
    AVZ(sec,n)
    cont:=0
    repetir
      si n No en Vocales entonces
        cont:= cont + 1
      FinSi
      AVZ(sec,n)
    Hasta que n = "Z"
    escribir ("La cantidad  de consonantes que hay en la secuencia es: ", cont)
FinAccion
*/

const arr2 = "AJSKELSKDKRSLALERWERZ"
const vocales = ["a", "e", "i", "o", "u"]
i = 0
let contConso = 0
do {
  console.log(arr2[i])
  if (!(arr2[i] in vocales)) contConso = contConso + 1
  i++
} while (arr2[i] != "Z")

console.log(`hay ${contConso} consonantes en la secuencia`)

/*1.03. Se dispone de una secuencia de caracteres y se desea obtener una secuencia de salida que resulte de copiar la
secuencia de entrada, descartando el caracter "$".

Accion copiasec ES
    Ambiente
      entr,sali: secuencia de caracter
      L: caracter
    Proceso
      arr(entr)
      avz(entr, L)
      crear(sali)
      Mientras NoFDS(entr) hacer 
        Si L <> "$" entonces
          escribir(sali, L)
        FinSi
        avz(entr, L)
      FinMientras
      cerrar()
      escribir("La secuencia de salida es: ", sali)
Fin Accion

*/ 

const arr3 = "iefjeoijfoejfofj$ojdopfjepofepfe$$$$$opffjkopfrp$$@sdedodekjp"
let res = ""

for (let i = 0; i < arr3.length; i++) {
  console.log(arr3[i])
  if (arr3[i] !== "$") {
    res = res + [arr3[i]]
  }
}

console.log(res)

/*1.04. Se dispone de una secuencia de números de socios, y se desea saber la cantidad de socios que están
registrados.

Accion NumerosSocios es 
| 34564 | 91218 | 310101 |
  Ambiente
    sec: secuencia de numeros enteros
    v: entero
    cont: entero
  Proceso
    arr(sec)
    avz(sec, v)
    cont := 0
    Mientras NoFDS(sec) hacer
      cont:= cont + 1
      avz(sec, v)
    Fin Mientras
    escribir("La cantidad de socios registrados es de, cont")
Fin Acción
*/ 