package co.edu.uptc.banco.cuenta;

import java.math.BigDecimal;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/** Cuentas semilla para probar transferencias; solo se crean si la base está vacía. */
@Component
class DatosIniciales implements CommandLineRunner {
    private final CuentaRepository cuentas;

    DatosIniciales(CuentaRepository cuentas) {
        this.cuentas = cuentas;
    }

    @Override
    public void run(String... args) {
        if (cuentas.count() > 0) return;
        Cuenta ana = new Cuenta("3001234567", "Ana");
        ana.setSaldo(new BigDecimal("500000.00"));
        Cuenta luis = new Cuenta("3109876543", "Luis");
        luis.setSaldo(new BigDecimal("150000.00"));
        cuentas.saveAll(java.util.List.of(ana, luis));
    }
}
