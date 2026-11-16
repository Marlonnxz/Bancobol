package co.edu.uptc.banco.cobol;

import org.junit.jupiter.api.Test;

import java.io.File;
import java.math.BigDecimal;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

/** Llama las 5 operaciones en banco.dll real; se omite si la DLL no se ha compilado (compilar-dll.ps1). */
class CobolDllTest {

    private static BigDecimal bd(String valor) {
        return new BigDecimal(valor).setScale(2);
    }

    @Test
    void cincoOperacionesEnLaDll() {
        assumeTrue(new File("dll/banco.dll").isFile(), "falta dll/banco.dll");
        CobolDll dll = new CobolDll(new CobolEngine(), "dll/banco.dll", "C:/msys64/mingw64/bin");

        Map<String, BigDecimal> r = dll.ejecutar("APERTURA", Map.of("MONTO", bd("1000")));
        assertEquals(bd("1000"), r.get("SALDO"));
        assertEquals(bd("0"), r.get("CODIGO"));

        assertEquals(bd("0"), dll.ejecutar("CONSULTA", Map.of("SALDO", bd("1000"))).get("CODIGO"));
        assertEquals(bd("3"), dll.ejecutar("CONSULTA", Map.of("SALDO", bd("-1"))).get("CODIGO"));

        r = dll.ejecutar("DEPOSITO", Map.of("SALDO", bd("1000"), "MONTO", bd("250.75")));
        assertEquals(bd("1250.75"), r.get("SALDO"));

        r = dll.ejecutar("RETIRO", Map.of("SALDO", bd("100"), "MONTO", bd("100.01")));
        assertEquals(bd("100"), r.get("SALDO"));
        assertEquals(bd("2"), r.get("CODIGO"));

        r = dll.ejecutar("TRANSFERENCIA", Map.of("SALDO-ORIGEN", bd("300"), "SALDO-DESTINO", bd("20"), "MONTO", bd("120.50")));
        assertEquals(bd("179.50"), r.get("SALDO-ORIGEN"));
        assertEquals(bd("140.50"), r.get("SALDO-DESTINO"));
        assertEquals(bd("0"), r.get("CODIGO"));

        // saldo cercano al maximo PIC S9(12)V99: valida que viajen los 8 bytes completos
        r = dll.ejecutar("DEPOSITO", Map.of("SALDO", bd("999999999998.99"), "MONTO", bd("1")));
        assertEquals(bd("999999999999.99"), r.get("SALDO"));
    }
}
