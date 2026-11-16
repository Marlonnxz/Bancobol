package co.edu.uptc.banco.cobol;

import co.edu.uptc.banco.cobol.Ast.*;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Fase 3: generacion de codigo. Recorre el AST y escribe una clase Java que implementa
 * Consumer&lt;Map&lt;String, BigDecimal&gt;&gt; (solo tipos del JDK). Cada variable COBOL es un
 * BigDecimal local con escala 2; el mapa sirve de entrada y salida.
 */
public class GeneradorJava {

    private static final String REDONDEO = "RoundingMode.HALF_EVEN";

    private final StringBuilder sb = new StringBuilder();
    private int sangria = 0;

    public static String nombreClase(String programa) {
        return "Cobol_" + identificador(programa);
    }

    /** SALDO-ORIGEN -> SALDO_ORIGEN */
    static String identificador(String nombreCobol) {
        return nombreCobol.replace('-', '_');
    }

    public String generar(Programa p) {
        linea("import java.math.BigDecimal;");
        linea("import java.math.RoundingMode;");
        linea("import java.util.Map;");
        linea("import java.util.function.Consumer;");
        linea("");
        linea("/** Generado automáticamente a partir de " + p.nombre() + ".cob */");
        abrir("public class " + nombreClase(p.nombre()) + " implements Consumer<Map<String, BigDecimal>> {");
        linea("");
        linea("@Override");
        abrir("public void accept(Map<String, BigDecimal> memoria) {");
        linea("// WORKING-STORAGE SECTION");
        for (Variable v : p.variables()) {
            linea("BigDecimal " + identificador(v.nombre()) + " = leer(memoria, \"" + v.nombre() + "\", \""
                    + v.valor() + "\"); // PIC " + v.pic());
        }
        linea("");
        linea("// PROCEDURE DIVISION (STOP RUN = break programa)");
        abrir("programa: {");
        sentencias(p.sentencias());
        cerrar("}");
        linea("");
        linea("// Devuelve las variables al mapa");
        for (Variable v : p.variables()) {
            linea("memoria.put(\"" + v.nombre() + "\", " + identificador(v.nombre()) + ");");
        }
        cerrar("}");
        linea("");
        abrir("private static BigDecimal leer(Map<String, BigDecimal> memoria, String nombre, String valorInicial) {");
        linea("BigDecimal valor = memoria.get(nombre);");
        linea("return (valor != null ? valor : new BigDecimal(valorInicial)).setScale(2, " + REDONDEO + ");");
        cerrar("}");
        cerrar("}");
        return sb.toString();
    }

    // ---------------- Sentencias ----------------

    /**
     * Genera una lista de sentencias y devuelve true si todos sus caminos terminan en STOP RUN.
     * Lo que sigue a un STOP RUN es inalcanzable y javac lo rechazaria, por eso se omite.
     */
    private boolean sentencias(List<Sentencia> lista) {
        for (Sentencia s : lista) {
            if (sentencia(s)) return true;
        }
        return false;
    }

    private boolean sentencia(Sentencia s) {
        switch (s) {
            case Move m -> asignar(m.destino(), expr(m.origen()));
            case Add a -> asignar(a.destino(), identificador(a.destino()) + ".add(" + expr(a.valor()) + ")");
            case Subtract r -> asignar(r.destino(), identificador(r.destino()) + ".subtract(" + expr(r.valor()) + ")");
            case Compute c -> asignar(c.destino(), expr(c.expr()));
            case If i -> {
                abrir("if (" + condicion(i.condicion()) + ") {");
                boolean terminaEntonces = sentencias(i.entonces());
                boolean terminaSino = false;
                if (!i.sino().isEmpty()) {
                    sangria--;
                    abrir("} else {");
                    terminaSino = sentencias(i.sino());
                }
                cerrar("}");
                return terminaEntonces && terminaSino;
            }
            case Display d -> linea("System.out.println("
                    + d.partes().stream().map(this::textoDisplay).collect(Collectors.joining(" + ")) + ");");
            case StopRun stop -> {
                linea("break programa;");
                return true;
            }
        }
        return false;
    }

    private void asignar(String destino, String valor) {
        linea(identificador(destino) + " = " + valor + ".setScale(2, " + REDONDEO + ");");
    }

    private String textoDisplay(Expr e) {
        return switch (e) {
            case Texto t -> cadenaJava(t.valor());
            case Numero n -> cadenaJava(n.valor());
            default -> expr(e) + ".toPlainString()";
        };
    }

    // ---------------- Condiciones y expresiones ----------------

    private String condicion(Condicion c) {
        return switch (c) {
            case Comparacion cmp -> {
                String op = switch (cmp.op()) {
                    case "=" -> "==";
                    case "<>" -> "!=";
                    default -> cmp.op();
                };
                yield expr(cmp.izq()) + ".compareTo(" + expr(cmp.der()) + ") " + op + " 0";
            }
            case Logica l -> "(" + condicion(l.izq()) + (l.op().equals("AND") ? " && " : " || ") + condicion(l.der()) + ")";
        };
    }

    /** a + b -> a.add(b); como el lado izquierdo siempre es una llamada o primario, no hacen falta parentesis. */
    private String expr(Expr e) {
        return switch (e) {
            case Numero n -> "new BigDecimal(\"" + n.valor() + "\")";
            case Var v -> identificador(v.nombre());
            case Negativo n -> expr(n.expr()) + ".negate()";
            case Binaria b -> {
                String izq = expr(b.izq());
                String der = expr(b.der());
                yield switch (b.op()) {
                    case '+' -> izq + ".add(" + der + ")";
                    case '-' -> izq + ".subtract(" + der + ")";
                    case '*' -> izq + ".multiply(" + der + ")";
                    default -> izq + ".divide(" + der + ", 2, " + REDONDEO + ")";
                };
            }
            case Texto t -> throw new IllegalStateException("texto fuera de DISPLAY: " + t.valor());
        };
    }

    private static String cadenaJava(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    // ---------------- Formato ----------------

    private void linea(String texto) {
        if (!texto.isEmpty()) sb.append("    ".repeat(sangria)).append(texto);
        sb.append('\n');
    }

    private void abrir(String texto) {
        linea(texto);
        sangria++;
    }

    private void cerrar(String texto) {
        sangria--;
        linea(texto);
    }
}
