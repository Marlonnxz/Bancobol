package co.edu.uptc.banco.cobol;

import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * Punto de entrada: COBOL (.cob) -> Lexer -> Parser -> GeneradorJava -> CompiladorJava -> ejecucion.
 */
@Component
public class CobolEngine {

    private static final List<String> PROGRAMAS = List.of("DEPOSITO", "RETIRO", "TRANSFERENCIA");

    private final Map<String, Consumer<Map<String, BigDecimal>>> compilados = new ConcurrentHashMap<>();

    public List<String> programas() {
        return PROGRAMAS;
    }

    public String fuente(String programa) {
        if (!PROGRAMAS.contains(programa)) throw noEncontrado(programa);
        try (InputStream in = CobolEngine.class.getResourceAsStream("/cobol/" + programa + ".cob")) {
            if (in == null) throw noEncontrado(programa);
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public String transpilar(String programa) {
        return transpilarFuente(fuente(programa));
    }

    /** Ejecuta el programa sobre una copia de la entrada y devuelve todas sus variables WORKING-STORAGE. */
    public Map<String, BigDecimal> ejecutar(String programa, Map<String, BigDecimal> entrada) {
        Consumer<Map<String, BigDecimal>> ejecutable = compilados.computeIfAbsent(programa, this::compilar);
        Map<String, BigDecimal> memoria = new LinkedHashMap<>(entrada);
        ejecutable.accept(memoria);
        return memoria;
    }

    static String transpilarFuente(String fuente) {
        Ast.Programa ast = new Parser(new Lexer(fuente).tokens()).programa();
        return new GeneradorJava().generar(ast);
    }

    @SuppressWarnings("unchecked")
    private Consumer<Map<String, BigDecimal>> compilar(String programa) {
        Ast.Programa ast = new Parser(new Lexer(fuente(programa)).tokens()).programa();
        String codigo = new GeneradorJava().generar(ast);
        String nombreClase = GeneradorJava.nombreClase(ast.nombre());
        try {
            Class<?> clase = new CompiladorJava().compilar(nombreClase, codigo);
            return (Consumer<Map<String, BigDecimal>>) clase.getDeclaredConstructor().newInstance();
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("No se pudo instanciar " + nombreClase, e);
        }
    }

    private static IllegalArgumentException noEncontrado(String programa) {
        return new IllegalArgumentException("Programa COBOL no encontrado: " + programa);
    }
}
