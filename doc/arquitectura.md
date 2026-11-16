# Arquitectura

## Las piezas

```mermaid
flowchart LR
    UI["Frontend<br/>HTML + CSS + JS"] -- "HTTP / JSON" --> C["BancoController<br/>(API REST)"]
    C --> S["BancoService<br/>(orquesta)"]
    S -- "lee y guarda saldos" --> DB[("H2<br/>data/banco.mv.db")]
    S -- "ejecuta reglas" --> E["CobolEngine"]
    E --> T["Transpilador<br/>Lexer → Parser → Generador → javac"]
    T -- "lee" --> F["cobol/*.cob"]
```

| Pieza | Dónde está | Qué hace |
|---|---|---|
| Frontend | `src/main/resources/static/` | Las pantallas. Spring las sirve en `/`. |
| API REST | `cuenta/BancoController.java` | Recibe las peticiones HTTP y convierte los errores en JSON. |
| Servicio | `cuenta/BancoService.java` | Valida los datos, bloquea las cuentas, llama al COBOL y guarda los resultados. |
| Persistencia | `cuenta/Cuenta.java`, `Movimiento.java`, `Repositorios.java` | Tablas `CUENTA` y `MOVIMIENTO` en H2, usadas con JPA. |
| Motor COBOL | `cobol/CobolEngine.java` | Transpila y compila cada programa una sola vez, y luego lo ejecuta las veces que se pida. |
| Programas COBOL | `src/main/resources/cobol/` | Las reglas del dinero: `DEPOSITO`, `RETIRO`, `TRANSFERENCIA`. |

La regla para repartir el trabajo es esta: **Java decide *cómo* se guarda el dinero y COBOL decide
*qué* pasa con el saldo.** El servicio no hace sumas ni restas. Le pasa los saldos al programa COBOL
y guarda lo que el programa devuelva.

## Recorrido de una consignación

Ejemplo: Ana consigna $20.000.

```mermaid
sequenceDiagram
    participant U as Frontend
    participant C as Controller
    participant S as BancoService
    participant DB as H2
    participant E as CobolEngine
    U->>C: POST /api/cuentas/3001234567/consignar {"monto":20000}
    C->>S: consignar("3001234567", 20000)
    S->>S: valida el monto (no nulo, máx. 2 decimales)
    S->>DB: SELECT ... FOR UPDATE (bloquea la cuenta)
    DB-->>S: saldo = 500000.00
    S->>E: ejecutar("DEPOSITO", {SALDO: 500000, MONTO: 20000})
    E-->>S: {SALDO: 520000, MONTO: 20000, CODIGO: 0}
    S->>DB: actualiza el saldo y guarda el movimiento
    S-->>C: cuenta actualizada
    C-->>U: {"telefono":"3001234567","nombre":"Ana","saldo":520000.00}
```

1. El frontend manda el monto.
2. El servicio revisa que el monto tenga sentido como número.
3. Bloquea la fila de la cuenta en la base de datos para que nadie más la cambie mientras tanto.
4. Llama al programa COBOL `DEPOSITO` con el saldo actual y el monto.
5. El programa responde con el nuevo saldo y un **CODIGO**:
   - `0`: todo bien.
   - `1`: monto inválido → HTTP 400.
   - `2`: fondos insuficientes → HTTP 422.
6. Si el código es 0, se guarda el nuevo saldo y se registra el movimiento. Si el código es otro, se
   lanza un error, la transacción se deshace y no cambia nada.

Retirar funciona igual con el programa `RETIRO`. Transferir usa `TRANSFERENCIA`, que recibe los dos
saldos (origen y destino) y devuelve los dos ya actualizados.

## Por qué el saldo no se pierde

- La base H2 está configurada **en archivo** (`spring.datasource.url=jdbc:h2:file:./data/banco`),
  no en memoria. Todo lo que se guarda queda en `data/banco.mv.db`.
- Cada operación es una **transacción** (`@Transactional`): o se guarda todo (saldo y movimiento),
  o no se guarda nada.
- Las tablas se crean solas la primera vez (`ddl-auto=update`). Las cuentas de prueba solo se crean
  si la base está vacía.

## Dos operaciones al mismo tiempo

Si dos peticiones llegan a la vez sobre la misma cuenta, las dos podrían leer el mismo saldo y una
pisaría a la otra. Para evitarlo, el servicio lee la cuenta con un **bloqueo pesimista**
(`SELECT ... FOR UPDATE`): la segunda petición espera hasta que la primera termine.

En una transferencia se bloquean **dos** cuentas. Siempre se bloquean en el mismo orden (primero el
teléfono menor) para que dos transferencias cruzadas (A→B y B→A) no se queden esperándose una a la
otra para siempre (*deadlock*).

## Frontend

Son tres archivos (`index.html`, `app.css`, `app.js`) sin frameworks y sin paso de compilación.

- **Ingreso / registro**: con el teléfono. La sesión se recuerda en `localStorage`.
- **Inicio**: el saldo, los botones de acción y los últimos movimientos.
- **Consignar / Retirar / Transferir**: formularios que validan antes de enviar y muestran el error que devuelva el servidor.
- **Compilador**: muestra el `.cob` y el Java generado lado a lado.

Los íconos son SVG escritos a mano. No hay animaciones ni librerías externas, para que cargue rápido.
