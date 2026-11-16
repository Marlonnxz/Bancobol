package co.edu.uptc.banco.cuenta;

import co.edu.uptc.banco.cobol.CobolDll;
import co.edu.uptc.banco.cuenta.Movimiento.Tipo;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Persiste cuentas y movimientos; las reglas de saldo viven en los programas COBOL de banco.dll. */
@Service
public class BancoService {
    private static final BigDecimal MAXIMO = new BigDecimal("999999999999.99"); // PIC 9(12)V99

    private final CuentaRepository cuentas;
    private final MovimientoRepository movimientos;
    private final CobolDll cobol;

    BancoService(CuentaRepository cuentas, MovimientoRepository movimientos, CobolDll cobol) {
        this.cuentas = cuentas;
        this.movimientos = movimientos;
        this.cobol = cobol;
    }

    @Transactional
    public Cuenta crear(String telefono, String nombre, BigDecimal saldoInicial) {
        validarTelefono(telefono);
        if (nombre == null || nombre.isBlank()) throw new BancoException(HttpStatus.BAD_REQUEST, "El nombre es obligatorio");
        if (cuentas.existsById(telefono)) throw new BancoException(HttpStatus.CONFLICT, "Ya existe una cuenta con ese teléfono");
        BigDecimal valor = normalizar(saldoInicial == null ? BigDecimal.ZERO : saldoInicial);
        Map<String, BigDecimal> r = ejecutar("APERTURA", Map.of("MONTO", valor));
        Cuenta cuenta = new Cuenta(telefono, nombre.trim());
        cuenta.setSaldo(r.get("SALDO"));
        cuentas.save(cuenta);
        if (valor.signum() > 0)
            movimientos.save(new Movimiento(telefono, Tipo.CONSIGNACION, valor, null, cuenta.getSaldo()));
        return cuenta;
    }

    @Transactional(readOnly = true)
    public Cuenta consultar(String telefono) {
        Cuenta cuenta = cuentas.findById(telefono).orElseThrow(() -> noExiste(telefono));
        ejecutar("CONSULTA", Map.of("SALDO", cuenta.getSaldo()));
        return cuenta;
    }

    @Transactional(readOnly = true)
    public List<Movimiento> movimientos(String telefono) {
        if (!cuentas.existsById(telefono)) throw noExiste(telefono);
        return movimientos.findTop50ByTelefonoOrderByIdDesc(telefono);
    }

    @Transactional
    public Cuenta consignar(String telefono, BigDecimal monto) {
        return operar("DEPOSITO", Tipo.CONSIGNACION, telefono, monto);
    }

    @Transactional
    public Cuenta retirar(String telefono, BigDecimal monto) {
        return operar("RETIRO", Tipo.RETIRO, telefono, monto);
    }

    @Transactional
    public Cuenta transferir(String origen, String destino, BigDecimal monto) {
        validarTelefono(origen);
        validarTelefono(destino);
        if (origen.equals(destino)) throw new BancoException(HttpStatus.BAD_REQUEST, "No puedes transferirte a ti mismo");
        BigDecimal valor = normalizar(monto);
        // Bloqueo en orden fijo para evitar interbloqueos entre transferencias cruzadas
        boolean origenPrimero = origen.compareTo(destino) < 0;
        Cuenta primera = bloquear(origenPrimero ? origen : destino);
        Cuenta segunda = bloquear(origenPrimero ? destino : origen);
        Cuenta cOrigen = origenPrimero ? primera : segunda;
        Cuenta cDestino = origenPrimero ? segunda : primera;

        Map<String, BigDecimal> r = ejecutar("TRANSFERENCIA", Map.of(
                "SALDO-ORIGEN", cOrigen.getSaldo(), "SALDO-DESTINO", cDestino.getSaldo(), "MONTO", valor));
        if (r.get("SALDO-DESTINO").compareTo(MAXIMO) > 0)
            throw new BancoException(HttpStatus.BAD_REQUEST, "La cuenta destino superaría el saldo máximo");
        cOrigen.setSaldo(r.get("SALDO-ORIGEN"));
        cDestino.setSaldo(r.get("SALDO-DESTINO"));
        movimientos.save(new Movimiento(origen, Tipo.TRANSFERENCIA_ENVIADA, valor, destino, cOrigen.getSaldo()));
        movimientos.save(new Movimiento(destino, Tipo.TRANSFERENCIA_RECIBIDA, valor, origen, cDestino.getSaldo()));
        return cOrigen;
    }

    private Cuenta operar(String programa, Tipo tipo, String telefono, BigDecimal monto) {
        BigDecimal valor = normalizar(monto);
        Cuenta cuenta = bloquear(telefono);
        Map<String, BigDecimal> r = ejecutar(programa, Map.of("SALDO", cuenta.getSaldo(), "MONTO", valor));
        if (r.get("SALDO").compareTo(MAXIMO) > 0)
            throw new BancoException(HttpStatus.BAD_REQUEST, "El saldo superaría el máximo permitido");
        cuenta.setSaldo(r.get("SALDO"));
        movimientos.save(new Movimiento(telefono, tipo, valor, null, cuenta.getSaldo()));
        return cuenta;
    }

    /** Llama al programa COBOL de la DLL y traduce su CODIGO de retorno. */
    private Map<String, BigDecimal> ejecutar(String programa, Map<String, BigDecimal> entrada) {
        Map<String, BigDecimal> r = cobol.ejecutar(programa, entrada);
        return switch (r.get("CODIGO").intValue()) {
            case 0 -> r;
            case 1 -> throw new BancoException(HttpStatus.BAD_REQUEST, programa.equals("APERTURA")
                    ? "El saldo inicial no puede ser negativo" : "El monto debe ser mayor a cero");
            case 2 -> throw new BancoException(HttpStatus.UNPROCESSABLE_ENTITY, "Fondos insuficientes");
            case 3 -> throw new BancoException(HttpStatus.CONFLICT, "El saldo de la cuenta es inconsistente");
            default -> throw new IllegalStateException("Código COBOL desconocido: " + r.get("CODIGO"));
        };
    }

    private static BigDecimal normalizar(BigDecimal monto) {
        if (monto == null) throw new BancoException(HttpStatus.BAD_REQUEST, "El monto es obligatorio");
        if (monto.stripTrailingZeros().scale() > 2) throw new BancoException(HttpStatus.BAD_REQUEST, "El monto admite máximo 2 decimales");
        if (monto.compareTo(MAXIMO) > 0) throw new BancoException(HttpStatus.BAD_REQUEST, "El monto excede el máximo permitido");
        return monto.setScale(2, RoundingMode.UNNECESSARY);
    }

    private Cuenta bloquear(String telefono) {
        validarTelefono(telefono);
        return cuentas.bloquear(telefono).orElseThrow(() -> noExiste(telefono));
    }

    private static void validarTelefono(String telefono) {
        if (telefono == null || !telefono.matches("\\d{10}"))
            throw new BancoException(HttpStatus.BAD_REQUEST, "El teléfono debe tener 10 dígitos");
    }

    private static BancoException noExiste(String telefono) {
        return new BancoException(HttpStatus.NOT_FOUND, "No existe la cuenta " + telefono);
    }
}
