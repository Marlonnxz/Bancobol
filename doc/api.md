# API REST

Base: `http://localhost:8080/api`. Todo se envía y se recibe en JSON.

## Cuentas

| Método | Ruta | Cuerpo | Respuesta |
|---|---|---|---|
| `POST` | `/cuentas` | `{"telefono":"3200000000","nombre":"Pepe"}` | `201` con la cuenta creada |
| `GET` | `/cuentas/{telefono}` | | `200` con la cuenta |
| `GET` | `/cuentas/{telefono}/movimientos` | | `200` con los últimos 50 movimientos, el más reciente primero |

Una cuenta se ve así:

```json
{ "telefono": "3001234567", "nombre": "Ana", "saldo": 520000.00 }
```

## Operaciones

| Método | Ruta | Cuerpo | Programa COBOL que se ejecuta |
|---|---|---|---|
| `POST` | `/cuentas/{telefono}/consignar` | `{"monto": 20000}` | `DEPOSITO` |
| `POST` | `/cuentas/{telefono}/retirar` | `{"monto": 10000}` | `RETIRO` |
| `POST` | `/transferencias` | `{"origen":"3001234567","destino":"3109876543","monto":50000}` | `TRANSFERENCIA` |

Las tres devuelven la cuenta actualizada. En una transferencia es la cuenta **origen**.

Un movimiento se ve así:

```json
{
  "id": 4,
  "tipo": "TRANSFERENCIA_RECIBIDA",
  "monto": 50000.00,
  "contraparte": "3001234567",
  "saldoResultante": 200000.00,
  "fecha": "2026-11-16T09:52:37.768867"
}
```

`tipo` puede ser `CONSIGNACION`, `RETIRO`, `TRANSFERENCIA_ENVIADA` o `TRANSFERENCIA_RECIBIDA`.
`contraparte` es el teléfono de la otra cuenta, o `null` si no hay otra cuenta involucrada.

## Compilador

| Método | Ruta | Respuesta |
|---|---|---|
| `GET` | `/cobol` | `["DEPOSITO","RETIRO","TRANSFERENCIA"]` |
| `GET` | `/cobol/{programa}` | `{"programa":"DEPOSITO","cobol":"...","java":"..."}` |

## Errores

Todos los errores tienen la misma forma:

```json
{ "error": "Fondos insuficientes" }
```

| Código | Cuándo |
|---|---|
| `400` | Teléfono que no tiene 10 dígitos, monto menor o igual a cero, más de 2 decimales, transferirse a sí mismo, JSON mal formado |
| `404` | La cuenta o el programa COBOL no existe |
| `409` | Ya existe una cuenta con ese teléfono |
| `422` | Fondos insuficientes |

## Probar con curl

```bash
curl localhost:8080/api/cuentas/3001234567

curl -H "Content-Type: application/json" -d '{"monto":20000}' \
     localhost:8080/api/cuentas/3001234567/consignar

curl -H "Content-Type: application/json" \
     -d '{"origen":"3001234567","destino":"3109876543","monto":50000}' \
     localhost:8080/api/transferencias
```
