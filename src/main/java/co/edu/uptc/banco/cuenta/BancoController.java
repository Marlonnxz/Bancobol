package co.edu.uptc.banco.cuenta;

import co.edu.uptc.banco.cobol.CobolEngine;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class BancoController {
    record NuevaCuenta(String telefono, String nombre, BigDecimal saldoInicial) {}
    record Monto(BigDecimal monto) {}
    record Transferencia(String origen, String destino, BigDecimal monto) {}
    record ProgramaCobol(String programa, String cobol, String java) {}

    private final BancoService banco;
    private final CobolEngine cobol;

    BancoController(BancoService banco, CobolEngine cobol) {
        this.banco = banco;
        this.cobol = cobol;
    }

    @PostMapping("/cuentas")
    @ResponseStatus(HttpStatus.CREATED)
    public Cuenta crear(@RequestBody NuevaCuenta c) {
        return banco.crear(c.telefono(), c.nombre(), c.saldoInicial());
    }

    @GetMapping("/cuentas/{telefono}")
    public Cuenta consultar(@PathVariable String telefono) {
        return banco.consultar(telefono);
    }

    @GetMapping("/cuentas/{telefono}/movimientos")
    public List<Movimiento> movimientos(@PathVariable String telefono) {
        return banco.movimientos(telefono);
    }

    @PostMapping("/cuentas/{telefono}/consignar")
    public Cuenta consignar(@PathVariable String telefono, @RequestBody Monto m) {
        return banco.consignar(telefono, m.monto());
    }

    @PostMapping("/cuentas/{telefono}/retirar")
    public Cuenta retirar(@PathVariable String telefono, @RequestBody Monto m) {
        return banco.retirar(telefono, m.monto());
    }

    @PostMapping("/transferencias")
    public Cuenta transferir(@RequestBody Transferencia t) {
        return banco.transferir(t.origen(), t.destino(), t.monto());
    }

    @GetMapping("/cobol")
    public List<String> programas() {
        return cobol.programas();
    }

    @GetMapping("/cobol/{programa}")
    public ProgramaCobol programa(@PathVariable String programa) {
        String p = programa.toUpperCase();
        return new ProgramaCobol(p, cobol.fuente(p), cobol.transpilar(p));
    }

    @ExceptionHandler(BancoException.class)
    ResponseEntity<Map<String, String>> manejar(BancoException e) {
        return ResponseEntity.status(e.estado).body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ResponseEntity<Map<String, String>> manejar(IllegalArgumentException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    ResponseEntity<Map<String, String>> manejar(HttpMessageNotReadableException e) {
        return ResponseEntity.badRequest().body(Map.of("error", "Solicitud inválida"));
    }
}
