# El COBOL del proyecto

## Qué es COBOL, en dos líneas

COBOL es un lenguaje de 1959 pensado para negocios. Se lee casi como inglés (`ADD MONTO TO SALDO`)
y sigue funcionando en muchos bancos. Un programa COBOL se divide en **divisiones**:

| División | Para qué sirve |
|---|---|
| `IDENTIFICATION DIVISION` | Da el nombre del programa |
| `DATA DIVISION` | Declara las variables |
| `PROCEDURE DIVISION` | Contiene las instrucciones |

## El subconjunto que acepta el transpilador

Solo se acepta una parte de COBOL: la que hace falta para las reglas bancarias.

### Variables

```cobol
01 SALDO   PIC S9(12)V99 VALUE 0.
```

- `01` es el nivel de la variable (se aceptan `01` y `77`).
- `PIC` describe el formato del número: `S` = con signo, `9(12)` = 12 dígitos enteros, `V99` = 2 decimales.
- `VALUE` es el valor inicial (opcional). También se acepta `VALUE ZERO`.
- Todas las variables son **numéricas**. En Java se convierten en `BigDecimal` con 2 decimales,
  que es el tipo correcto para manejar dinero sin errores de redondeo.
- Los nombres pueden llevar guiones (`SALDO-ORIGEN`). En Java el guion se cambia por guion bajo (`SALDO_ORIGEN`).

### Instrucciones

| COBOL | Qué hace | Java generado (aprox.) |
|---|---|---|
| `MOVE 1 TO CODIGO` | asigna | `CODIGO = 1` |
| `ADD MONTO TO SALDO` | suma | `SALDO = SALDO.add(MONTO)` |
| `SUBTRACT MONTO FROM SALDO` | resta | `SALDO = SALDO.subtract(MONTO)` |
| `COMPUTE X = (A + B) * 2` | expresión con `+ - * /` y paréntesis | `X = A.add(B).multiply(2)` |
| `IF ... ELSE ... END-IF` | condición | `if (...) { } else { }` |
| `DISPLAY 'TEXTO' SALDO` | imprime en la consola del servidor | `System.out.println(...)` |
| `STOP RUN` | termina el programa | `break programa;` |

Condiciones: `>`, `<`, `=`, `>=`, `<=`, `NOT =`, combinadas con `AND` y `OR`.
Los comentarios empiezan con `*>`. El formato es libre: no hay columnas fijas como en el COBOL antiguo.

### Limitaciones (lo que no se acepta)

- `PIC` solo fija los 2 decimales: no recorta un número que tenga más dígitos de los declarados.
- Todo `IF` se cierra con `END-IF`. En COBOL real un punto también lo cierra; aquí no.
- No hay `PERFORM`, párrafos, variables de texto, tablas (`OCCURS`) ni archivos.
- `MOVE` y `ADD` reciben un solo destino.
- No se pueden poner paréntesis alrededor de condiciones.

Si se usa algo de esto, el transpilador responde con un error que dice la línea exacta.

## Los tres programas bancarios

Están en `src/main/resources/cobol/` y todos siguen el mismo **contrato**:

- Reciben los saldos y el monto.
- Devuelven los saldos (actualizados o no) y una variable **`CODIGO`**:
  - `0` = la operación se hizo,
  - `1` = el monto es inválido (cero o negativo),
  - `2` = fondos insuficientes.
- Si hay error, **no tocan los saldos**.

### DEPOSITO.cob

```cobol
PROCEDURE DIVISION.
    IF MONTO <= 0
        MOVE 1 TO CODIGO
        DISPLAY 'DEPOSITO RECHAZADO: MONTO INVALIDO'
    ELSE
        ADD MONTO TO SALDO
        MOVE 0 TO CODIGO
        DISPLAY 'DEPOSITO OK, NUEVO SALDO: ' SALDO
    END-IF.
    STOP RUN.
```

### RETIRO.cob

Igual que el depósito, pero antes de restar revisa que haya suficiente:

```cobol
    IF MONTO > SALDO
        MOVE 2 TO CODIGO
    ELSE
        SUBTRACT MONTO FROM SALDO
        MOVE 0 TO CODIGO
    END-IF.
```

### TRANSFERENCIA.cob

Trabaja con dos saldos a la vez:

```cobol
01 SALDO-ORIGEN   PIC S9(12)V99 VALUE 0.
01 SALDO-DESTINO  PIC S9(12)V99 VALUE 0.
...
    IF MONTO > SALDO-ORIGEN
        MOVE 2 TO CODIGO
    ELSE
        COMPUTE SALDO-ORIGEN = SALDO-ORIGEN - MONTO
        COMPUTE SALDO-DESTINO = SALDO-DESTINO + MONTO
        MOVE 0 TO CODIGO
    END-IF.
```

## Cambiar una regla

Para cambiar una regla del banco basta con editar el `.cob` y reiniciar la app. **No hay que tocar
Java.** Por ejemplo, para cobrar $1.000 de comisión en cada retiro:

```cobol
    IF MONTO + 1000 > SALDO
        MOVE 2 TO CODIGO
    ELSE
        COMPUTE SALDO = SALDO - MONTO - 1000
        MOVE 0 TO CODIGO
    END-IF.
```

Así es como funciona el sistema: la lógica de negocio está en el lenguaje "del banco" y Java solo la
ejecuta. Si quieres que este cambio quede también en las pruebas, agrega un caso en `CobolEngineTest`.
