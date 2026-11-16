package co.edu.uptc.banco.cobol;

import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class CobolEngineTest {

    private final CobolEngine motor = new CobolEngine();

    private static BigDecimal bd(String valor) {
        return new BigDecimal(valor).setScale(2);
    }

    @Test
    void depositoOk() {
        Map<String, BigDecimal> r = motor.ejecutar("DEPOSITO", Map.of("SALDO", bd("100"), "MONTO", bd("50.25")));
        assertEquals(bd("150.25"), r.get("SALDO"));
        assertEquals(bd("0"), r.get("CODIGO"));
    }

    @Test
    void depositoMontoInvalido() {
        Map<String, BigDecimal> r = motor.ejecutar("DEPOSITO", Map.of("SALDO", bd("100"), "MONTO", bd("0")));
        assertEquals(bd("100"), r.get("SALDO"));
        assertEquals(bd("1"), r.get("CODIGO"));
    }

    @Test
    void retiroOk() {
        Map<String, BigDecimal> r = motor.ejecutar("RETIRO", Map.of("SALDO", bd("100"), "MONTO", bd("100")));
        assertEquals(bd("0"), r.get("SALDO"));
        assertEquals(bd("0"), r.get("CODIGO"));
    }

    @Test
    void retiroMontoInvalido() {
        Map<String, BigDecimal> r = motor.ejecutar("RETIRO", Map.of("SALDO", bd("100"), "MONTO", bd("-5")));
        assertEquals(bd("100"), r.get("SALDO"));
        assertEquals(bd("1"), r.get("CODIGO"));
    }

    @Test
    void retiroFondosInsuficientes() {
        Map<String, BigDecimal> r = motor.ejecutar("RETIRO", Map.of("SALDO", bd("100"), "MONTO", bd("100.01")));
        assertEquals(bd("100"), r.get("SALDO"));
        assertEquals(bd("2"), r.get("CODIGO"));
    }

    @Test
    void transferenciaOk() {
        Map<String, BigDecimal> r = motor.ejecutar("TRANSFERENCIA",
                Map.of("SALDO-ORIGEN", bd("300"), "SALDO-DESTINO", bd("20"), "MONTO", bd("120.50")));
        assertEquals(bd("179.50"), r.get("SALDO-ORIGEN"));
        assertEquals(bd("140.50"), r.get("SALDO-DESTINO"));
        assertEquals(bd("0"), r.get("CODIGO"));
    }

    @Test
    void transferenciaMontoInvalido() {
        Map<String, BigDecimal> r = motor.ejecutar("TRANSFERENCIA",
                Map.of("SALDO-ORIGEN", bd("300"), "SALDO-DESTINO", bd("20"), "MONTO", bd("0")));
        assertEquals(bd("300"), r.get("SALDO-ORIGEN"));
        assertEquals(bd("20"), r.get("SALDO-DESTINO"));
        assertEquals(bd("1"), r.get("CODIGO"));
    }

    @Test
    void transferenciaFondosInsuficientes() {
        Map<String, BigDecimal> r = motor.ejecutar("TRANSFERENCIA",
                Map.of("SALDO-ORIGEN", bd("10"), "SALDO-DESTINO", bd("20"), "MONTO", bd("50")));
        assertEquals(bd("10"), r.get("SALDO-ORIGEN"));
        assertEquals(bd("20"), r.get("SALDO-DESTINO"));
        assertEquals(bd("2"), r.get("CODIGO"));
    }

    @Test
    void transpilaConGuionBajoYClaveCobol() {
        String java = motor.transpilar("TRANSFERENCIA");
        assertTrue(java.contains("public class Cobol_TRANSFERENCIA implements Consumer<Map<String, BigDecimal>>"));
        assertTrue(java.contains("BigDecimal SALDO_ORIGEN = leer(memoria, \"SALDO-ORIGEN\""));
    }

    @Test
    void computeConDivisionYParentesis() {
        String fuente = """
                IDENTIFICATION DIVISION.
                PROGRAM-ID. CALCULO.
                DATA DIVISION.
                WORKING-STORAGE SECTION.
                01 A PIC 9(5)V99 VALUE 10.
                01 B PIC 9(5)V99.
                PROCEDURE DIVISION.
                    COMPUTE B = (A + 0.5) / 3 * 2
                    IF B >= 7 AND A NOT = 0 OR B < 0 DISPLAY 'OK ' B END-IF
                    STOP RUN.
                """;
        String java = CobolEngine.transpilarFuente(fuente);
        assertTrue(java.contains("B = A.add(new BigDecimal(\"0.5\")).divide(new BigDecimal(\"3\"), 2, RoundingMode.HALF_EVEN)"
                + ".multiply(new BigDecimal(\"2\")).setScale(2, RoundingMode.HALF_EVEN);"), java);
    }

    @Test
    void errorDeSintaxisIndicaLinea() {
        String fuente = """
                IDENTIFICATION DIVISION.
                PROGRAM-ID. MALO.
                DATA DIVISION.
                WORKING-STORAGE SECTION.
                01 SALDO PIC 9(12)V99.
                PROCEDURE DIVISION.
                    MOVE 5 SALDO.
                """;
        CobolException e = assertThrows(CobolException.class, () -> CobolEngine.transpilarFuente(fuente));
        assertTrue(e.getMessage().contains("línea 7"), e.getMessage());
    }

    @Test
    void errorLexicoIndicaLinea() {
        CobolException e = assertThrows(CobolException.class,
                () -> CobolEngine.transpilarFuente("IDENTIFICATION DIVISION.\n  PROGRAM-ID. X #"));
        assertTrue(e.getMessage().contains("línea 2"), e.getMessage());
    }

    @Test
    void programaDesconocido() {
        IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
                () -> motor.ejecutar("PRESTAMO", Map.of()));
        assertEquals("Programa COBOL no encontrado: PRESTAMO", e.getMessage());
    }
}
