# BancoCOBOL: documentación

BancoCOBOL es una billetera digital pequeña, parecida a las apps de pago por celular. Permite:

- crear una cuenta con un número de teléfono,
- abrir la cuenta con un **saldo inicial**,
- **consultar** el saldo,
- **consignar** (meter dinero),
- **retirar** (sacar dinero),
- **transferir** dinero a otra cuenta,
- ver el historial de movimientos.

Lo que la hace distinta es que **las reglas del dinero están escritas en COBOL**, no en Java.
Las cinco operaciones (`APERTURA`, `CONSULTA`, `DEPOSITO`, `RETIRO`, `TRANSFERENCIA`) se compilan
con GnuCOBOL en una **DLL** (`dll/banco.dll`) que Java llama con JNA. Además, el proyecto incluye un
**transpilador** propio que lee ese mismo COBOL y lo traduce a Java, para ver qué hace cada programa.

## Índice

| Documento | Qué explica |
|---|---|
| [arquitectura.md](arquitectura.md) | Las piezas del sistema y el recorrido completo de una operación |
| [cobol.md](cobol.md) | El COBOL que se acepta y los cinco programas bancarios |
| [dll.md](dll.md) | Cómo se compila `banco.dll` con GnuCOBOL y cómo la llama Java con JNA |
| [transpilador.md](transpilador.md) | Cómo el COBOL se convierte en Java, fase por fase (lexer, parser, AST, generador, compilador) |
| [api.md](api.md) | Los endpoints REST, con ejemplos |

Si solo vas a leer uno, lee [transpilador.md](transpilador.md): es la parte central del proyecto.

## Por qué se hizo así

El proyecto es para la materia de **Lenguajes Formales**. La idea es aplicar la teoría a algo concreto:

- **Expresiones regulares y autómatas**: el *lexer* reconoce palabras, números y símbolos.
- **Gramáticas libres de contexto**: el *parser* revisa que el programa siga una gramática y arma un árbol.
- **Traducción dirigida por la sintaxis**: el *generador* recorre ese árbol y escribe código Java.

Se eligió COBOL porque es el lenguaje clásico de la banca: muchos bancos todavía tienen su núcleo en
COBOL y lo modernizan traduciéndolo a lenguajes como Java. Este proyecto hace una versión pequeña de eso.

Las operaciones se ejecutan desde una **DLL compilada con GnuCOBOL**, como en la banca real, donde
el núcleo COBOL se llama desde aplicaciones más nuevas. El **transpilador** a Java se construyó para
ver y entender todas las fases de un compilador sobre los mismos programas.

## Alcance

**Lo que sí hace**

- Cuentas identificadas por un teléfono de 10 dígitos, con saldo inicial 0.
- Cinco operaciones en COBOL dentro de `banco.dll`: apertura con saldo inicial, consulta de saldo,
  consignación, retiro y transferencia. Con validaciones: el monto debe ser mayor que cero, no se
  puede retirar más de lo que hay y no se puede transferir a la misma cuenta.
- Interfaz gráfica con **gestión de timeouts**: cada petición se cancela a los 8 s y la sesión se
  cierra tras 2 minutos sin actividad, con un aviso de 30 s antes.
- El saldo **se guarda en disco**: si se apaga y se vuelve a prender la app, el dinero sigue ahí.
- Historial de los últimos 50 movimientos por cuenta.
- Una pantalla "Compilador" que muestra cada programa COBOL al lado del Java que se generó a partir de él.

**Lo que no hace, a propósito**

- **No tiene contraseñas ni seguridad.** Basta con escribir un teléfono para entrar a esa cuenta.
  Es un proyecto académico; no debe manejar dinero real.
- No usa COBOL completo, solo un subconjunto pequeño (ver [cobol.md](cobol.md)).
- Está pensada para correr en un solo servidor, con una base de datos local (H2).

## Cómo ejecutarlo

Se necesita:

- un **JDK 21 o superior** (no un JRE: la pantalla Compilador usa `javac` mientras la app corre),
- **Maven**,
- **GnuCOBOL** de MSYS2: `pacman -S mingw-w64-x86_64-gnucobol` (queda en `C:\msys64\mingw64\bin`).

```powershell
.\compilar-dll.ps1     # compila los .cob en dll/banco.dll
mvn spring-boot:run     # levanta la app en http://localhost:8080
mvn test                # pruebas del transpilador y de la DLL
```

Si MSYS2 está en otra carpeta, se cambia `banco.cobol.runtime` en `application.properties` y se
pasa `-Runtime <carpeta>\mingw64\bin` al script.

Ya vienen dos cuentas de prueba: **3001234567** (Ana, $500.000) y **3109876543** (Luis, $150.000).
Los datos quedan en `./data/banco.mv.db`. Para empezar de cero, se borra la carpeta `data/`.

## Glosario rápido

| Término | Significado |
|---|---|
| **Transpilador** | Programa que traduce código de un lenguaje a otro del mismo nivel (aquí, de COBOL a Java). |
| **Compilador** | Programa que traduce código fuente a algo que la máquina ejecuta. Aquí, `cobc` pasa el COBOL a la DLL y `javac` pasa el Java a bytecode. |
| **DLL** | *Dynamic Link Library*: librería de Windows con funciones que otro programa carga y llama mientras corre. |
| **JNA** | *Java Native Access*: librería que permite a Java llamar funciones de una DLL sin escribir código en C. |
| **Timeout** | Tiempo máximo que se espera algo antes de cancelarlo. |
| **Token** | La unidad mínima de un texto: una palabra, un número, un símbolo. |
| **AST** | *Abstract Syntax Tree*, el árbol que representa la estructura del programa. |
| **Spring Boot** | Framework de Java que se usa para el servidor web y la base de datos. |
| **H2** | Base de datos que se guarda en un archivo dentro del proyecto. No hay que instalarla. |
