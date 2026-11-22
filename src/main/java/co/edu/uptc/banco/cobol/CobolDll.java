package co.edu.uptc.banco.cobol;

import com.sun.jna.Memory;
import com.sun.jna.NativeLibrary;
import com.sun.jna.Platform;
import com.sun.jna.Pointer;
import java.io.File;
import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Ejecuta las operaciones bancarias compiladas por GnuCOBOL en banco.dll (cobc -b), llamandolas con JNA.
 * Cada programa recibe sus parametros por referencia (PROCEDURE DIVISION USING); el orden y el tamano
 * de cada uno salen del AST del mismo .cob con el que se compilo la DLL.
 */
@Component
public class CobolDll {
    private static final Pattern NUEVES = Pattern.compile("9(?:\\((\\d+)\\))?");

    private final CobolEngine cobol;
    private final NativeLibrary dll;

    CobolDll(CobolEngine cobol,
             @Value("${banco.cobol.dll}") String rutaDll,
             @Value("${banco.cobol.runtime}") String runtime) {
        this.cobol = cobol;
        File archivo = new File(rutaDll).getAbsoluteFile();
        if (!archivo.isFile())
            throw new IllegalStateException("No existe " + archivo + ": compile la DLL con compilar-dll.ps1");
        NativeLibrary libcob;
        if (Platform.isWindows()) {
            libcob = NativeLibrary.getInstance(new File(runtime, "libcob-4.dll").getAbsolutePath());
            libcob.getFunction("cob_init").invokeVoid(new Object[]{0, Pointer.NULL});
            this.dll = NativeLibrary.getInstance(archivo.getPath());
        } else {
            this.dll = NativeLibrary.getInstance(archivo.getPath());
            libcob = NativeLibrary.getInstance("cob");
            Memory argv = new Memory(8);
            argv.setPointer(0, Pointer.NULL);
            libcob.getFunction("cob_init").invokeVoid(new Object[]{0, argv});
        }
    }

    /**
     * Llama al programa de la DLL con los valores de entrada y devuelve todos sus parametros USING.
     * ponytail: synchronized porque libcob no es seguro entre hilos; una llamada nativa a la vez.
     */
    public synchronized Map<String, BigDecimal> ejecutar(String programa, Map<String, BigDecimal> entrada) {
        Ast.Programa ast = cobol.ast(programa);
        Map<String, Ast.Variable> vars = new LinkedHashMap<>();
        ast.variables().forEach(v -> vars.put(v.nombre(), v));

        Object[] args = new Object[ast.usando().size()];
        for (int i = 0; i < args.length; i++) {
            Ast.Variable v = vars.get(ast.usando().get(i));
            if (!v.binario()) throw new IllegalStateException(programa + ": el parámetro " + v.nombre() + " debe ser COMP-5");
            int bytes = digitos(v.pic(), true) + digitos(v.pic(), false) <= 9 ? 4 : 8;
            long crudo = entrada.getOrDefault(v.nombre(), BigDecimal.ZERO).movePointRight(digitos(v.pic(), false)).longValueExact();
            Memory m = new Memory(bytes);
            if (bytes == 4) m.setInt(0, Math.toIntExact(crudo)); else m.setLong(0, crudo);
            args[i] = m;
        }

        dll.getFunction(programa).invokeInt(args);

        Map<String, BigDecimal> salida = new LinkedHashMap<>();
        for (int i = 0; i < args.length; i++) {
            Ast.Variable v = vars.get(ast.usando().get(i));
            Memory m = (Memory) args[i];
            long crudo = m.size() == 4 ? m.getInt(0) : m.getLong(0);
            salida.put(v.nombre(), BigDecimal.valueOf(crudo, digitos(v.pic(), false)).setScale(2));
        }
        return salida;
    }

    /** Cuenta los 9 de la parte entera (antes de V) o decimal de una mascara: S9(12)V99 -> 12 y 2. */
    static int digitos(String pic, boolean enteros) {
        String[] partes = pic.replace("S", "").split("V");
        String parte = enteros ? partes[0] : (partes.length > 1 ? partes[1] : "");
        int n = 0;
        Matcher m = NUEVES.matcher(parte);
        while (m.find()) n += m.group(1) == null ? 1 : Integer.parseInt(m.group(1));
        return n;
    }
}
