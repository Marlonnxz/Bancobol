package co.edu.uptc.banco.cobol;

import java.util.ArrayList;
import java.util.List;

/**
 * Fase 1: analisis lexico. Convierte el texto COBOL (formato libre) en una lista de tokens.
 * Las palabras se normalizan a mayusculas; los comentarios empiezan con "*>".
 */
public class Lexer {

    public enum Tipo { PALABRA, NUMERO, CADENA, PIC, SIMBOLO, PUNTO, FIN }

    public record Token(Tipo tipo, String texto, int linea) {
        boolean es(String s) { return (tipo == Tipo.PALABRA || tipo == Tipo.SIMBOLO) && texto.equals(s); }
    }

    private final String src;
    private int pos = 0;
    private int linea = 1;
    private final List<Token> tokens = new ArrayList<>();

    public Lexer(String src) {
        this.src = src;
    }

    public List<Token> tokens() {
        while (true) {
            saltarEspaciosYComentarios();
            if (pos >= src.length()) break;
            char c = src.charAt(pos);
            if (esPic()) {
                leerPic();
            } else if (Character.isLetter(c)) {
                leerPalabra();
            } else if (Character.isDigit(c)) {
                leerNumero();
            } else if (c == '\'' || c == '"') {
                leerCadena(c);
            } else if (c == '.') {
                agregar(Tipo.PUNTO, ".");
                pos++;
            } else if ((c == '>' || c == '<') && siguiente() == '=') {
                agregar(Tipo.SIMBOLO, c + "=");
                pos += 2;
            } else if ("+-*/=<>()".indexOf(c) >= 0) {
                agregar(Tipo.SIMBOLO, String.valueOf(c));
                pos++;
            } else {
                throw new CobolException(linea, "carácter inesperado '" + c + "'");
            }
        }
        agregar(Tipo.FIN, "fin del archivo");
        return tokens;
    }

    private void saltarEspaciosYComentarios() {
        while (pos < src.length()) {
            char c = src.charAt(pos);
            if (c == '\n') {
                linea++;
                pos++;
            } else if (Character.isWhitespace(c)) {
                pos++;
            } else if (c == '*' && siguiente() == '>') {
                while (pos < src.length() && src.charAt(pos) != '\n') pos++;
            } else {
                break;
            }
        }
    }

    /** Identificadores y palabras reservadas: letras, digitos y guiones internos (SALDO-ORIGEN). */
    private void leerPalabra() {
        int inicio = pos;
        while (pos < src.length()) {
            char c = src.charAt(pos);
            if (Character.isLetterOrDigit(c)) pos++;
            else if (c == '-' && pos + 1 < src.length() && Character.isLetterOrDigit(src.charAt(pos + 1))) pos++;
            else break;
        }
        agregar(Tipo.PALABRA, src.substring(inicio, pos).toUpperCase());
    }

    /** Enteros o decimales; el punto solo es decimal si le sigue un digito ("0." es 0 y fin de sentencia). */
    private void leerNumero() {
        int inicio = pos;
        while (pos < src.length() && Character.isDigit(src.charAt(pos))) pos++;
        if (pos + 1 < src.length() && src.charAt(pos) == '.' && Character.isDigit(src.charAt(pos + 1))) {
            pos++;
            while (pos < src.length() && Character.isDigit(src.charAt(pos))) pos++;
        }
        agregar(Tipo.NUMERO, src.substring(inicio, pos));
    }

    /** Cadena entre comillas; una comilla doble ('') dentro representa una comilla literal. */
    private void leerCadena(char comilla) {
        StringBuilder sb = new StringBuilder();
        pos++;
        while (true) {
            if (pos >= src.length() || src.charAt(pos) == '\n') {
                throw new CobolException(linea, "cadena sin cerrar");
            }
            char c = src.charAt(pos++);
            if (c == comilla) {
                if (pos < src.length() && src.charAt(pos) == comilla) pos++;
                else break;
            }
            sb.append(c);
        }
        agregar(Tipo.CADENA, sb.toString());
    }

    /** Despues de PIC/PICTURE viene una mascara como 9(12)V99 que se lee como un solo token. */
    private boolean esPic() {
        if (tokens.isEmpty()) return false;
        Token ultimo = tokens.get(tokens.size() - 1);
        return ultimo.es("PIC") || ultimo.es("PICTURE");
    }

    private void leerPic() {
        int inicio = pos;
        while (pos < src.length() && !Character.isWhitespace(src.charAt(pos))) pos++;
        String mascara = src.substring(inicio, pos).toUpperCase();
        boolean conPunto = mascara.endsWith(".");
        if (conPunto) mascara = mascara.substring(0, mascara.length() - 1);
        if (!mascara.matches("S?9+(\\(\\d+\\))?(V9+(\\(\\d+\\))?)?")) {
            throw new CobolException(linea, "cláusula PIC no soportada: " + mascara);
        }
        agregar(Tipo.PIC, mascara);
        if (conPunto) agregar(Tipo.PUNTO, ".");
    }

    private char siguiente() {
        return pos + 1 < src.length() ? src.charAt(pos + 1) : '\0';
    }

    private void agregar(Tipo tipo, String texto) {
        tokens.add(new Token(tipo, texto, linea));
    }
}
