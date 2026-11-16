package co.edu.uptc.banco.cuenta;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
public class Movimiento {
    public enum Tipo { CONSIGNACION, RETIRO, TRANSFERENCIA_ENVIADA, TRANSFERENCIA_RECIBIDA }

    @Id
    @GeneratedValue
    private Long id;

    @JsonIgnore
    @Column(nullable = false, length = 10)
    private String telefono;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Tipo tipo;

    @Column(nullable = false, precision = 14, scale = 2)
    private BigDecimal monto;

    private String contraparte;

    @Column(nullable = false, precision = 14, scale = 2)
    private BigDecimal saldoResultante;

    @Column(nullable = false)
    private LocalDateTime fecha = LocalDateTime.now();

    protected Movimiento() {
    }

    Movimiento(String telefono, Tipo tipo, BigDecimal monto, String contraparte, BigDecimal saldoResultante) {
        this.telefono = telefono;
        this.tipo = tipo;
        this.monto = monto;
        this.contraparte = contraparte;
        this.saldoResultante = saldoResultante;
    }

    public Long getId() { return id; }
    public Tipo getTipo() { return tipo; }
    public BigDecimal getMonto() { return monto; }
    public String getContraparte() { return contraparte; }
    public BigDecimal getSaldoResultante() { return saldoResultante; }
    public LocalDateTime getFecha() { return fecha; }
}
