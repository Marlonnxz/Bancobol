package co.edu.uptc.banco.cobol;

import javax.tools.DiagnosticCollector;
import javax.tools.FileObject;
import javax.tools.ForwardingJavaFileManager;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileManager;
import javax.tools.JavaFileObject;
import javax.tools.SimpleJavaFileObject;
import javax.tools.ToolProvider;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.URI;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Fase 4: compila el codigo Java generado en memoria (sin tocar el disco) y carga la clase
 * con un ClassLoader propio que la define a partir de los bytes del .class.
 */
public class CompiladorJava {

    public Class<?> compilar(String nombreClase, String codigo) {
        JavaCompiler compilador = ToolProvider.getSystemJavaCompiler();
        if (compilador == null) {
            throw new IllegalStateException("No hay compilador de Java disponible: se requiere ejecutar con un JDK, no un JRE");
        }

        // Fuente en memoria
        JavaFileObject fuente = new SimpleJavaFileObject(
                URI.create("string:///" + nombreClase + JavaFileObject.Kind.SOURCE.extension), JavaFileObject.Kind.SOURCE) {
            @Override
            public CharSequence getCharContent(boolean ignorarErrores) {
                return codigo;
            }
        };

        // Los .class resultantes se guardan en este mapa en lugar de escribirse en disco
        Map<String, ByteArrayOutputStream> clases = new HashMap<>();
        JavaFileManager estandar = compilador.getStandardFileManager(null, null, null);
        JavaFileManager enMemoria = new ForwardingJavaFileManager<>(estandar) {
            @Override
            public JavaFileObject getJavaFileForOutput(Location ubicacion, String nombre, JavaFileObject.Kind tipo, FileObject hermano) {
                return new SimpleJavaFileObject(URI.create("mem:///" + nombre + tipo.extension), tipo) {
                    @Override
                    public OutputStream openOutputStream() {
                        return clases.computeIfAbsent(nombre, n -> new ByteArrayOutputStream());
                    }
                };
            }
        };

        DiagnosticCollector<JavaFileObject> diagnosticos = new DiagnosticCollector<>();
        // -proc:none: sin procesadores de anotaciones; el codigo generado solo usa tipos del JDK
        boolean ok = compilador.getTask(null, enMemoria, diagnosticos, List.of("-proc:none"), null, List.of(fuente)).call();
        if (!ok) {
            StringBuilder errores = new StringBuilder("Error compilando el Java generado:");
            diagnosticos.getDiagnostics().forEach(d ->
                    errores.append("\n  línea ").append(d.getLineNumber()).append(": ").append(d.getMessage(null)));
            throw new IllegalStateException(errores.toString());
        }

        ClassLoader cargador = new ClassLoader(CompiladorJava.class.getClassLoader()) {
            @Override
            protected Class<?> findClass(String nombre) throws ClassNotFoundException {
                ByteArrayOutputStream bytes = clases.get(nombre);
                if (bytes == null) throw new ClassNotFoundException(nombre);
                byte[] b = bytes.toByteArray();
                return defineClass(nombre, b, 0, b.length);
            }
        };
        try {
            return cargador.loadClass(nombreClase);
        } catch (ClassNotFoundException e) {
            throw new IllegalStateException(e);
        }
    }
}
