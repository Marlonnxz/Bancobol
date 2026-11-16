package co.edu.uptc.banco.cuenta;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.math.BigDecimal;

@Entity
public class Cuenta {
    @Id
    @Column(length = 10)
    private String telefono;

    @Column(nullable = false)
    private String nombre;

    @Column(nullable = false, precision = 14, scale = 2)
    private BigDecimal saldo = BigDecimal.ZERO.setScale(2);

    protected Cuenta() {
    }

    public Cuenta(String telefono, String nombre) {
        this.telefono = telefono;
        this.nombre = nombre;
    }

    public String getTelefono() { return telefono; }
    public String getNombre() { return nombre; }
    public BigDecimal getSaldo() { return saldo; }
    void setSaldo(BigDecimal saldo) { this.saldo = saldo; }
}
