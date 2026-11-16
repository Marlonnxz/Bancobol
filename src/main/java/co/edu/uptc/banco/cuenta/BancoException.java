package co.edu.uptc.banco.cuenta;

import org.springframework.http.HttpStatus;

public class BancoException extends RuntimeException {
    final HttpStatus estado;

    public BancoException(HttpStatus estado, String mensaje) {
        super(mensaje);
        this.estado = estado;
    }
}
