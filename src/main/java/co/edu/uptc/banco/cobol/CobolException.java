package co.edu.uptc.banco.cobol;

/** Error lexico o sintactico en un programa COBOL. El mensaje incluye la linea. */
public class CobolException extends RuntimeException {
    public CobolException(int linea, String mensaje) {
        super("Error en la línea " + linea + ": " + mensaje);
    }
}
