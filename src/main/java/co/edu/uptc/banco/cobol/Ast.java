package co.edu.uptc.banco.cobol;

import java.util.List;

/** Arbol de sintaxis abstracta (AST) que produce el Parser y consume el GeneradorJava. */
public final class Ast {
    private Ast() {}

    public record Programa(String nombre, List<Variable> variables, List<Sentencia> sentencias) {}

    /** Entrada de WORKING-STORAGE: 01 NOMBRE PIC mascara [VALUE valor]. */
    public record Variable(String nombre, String pic, String valor) {}

    // ---- Sentencias de la PROCEDURE DIVISION ----
    public sealed interface Sentencia permits Move, Add, Subtract, Compute, If, Display, StopRun {}
    public record Move(Expr origen, String destino) implements Sentencia {}
    public record Add(Expr valor, String destino) implements Sentencia {}
    public record Subtract(Expr valor, String destino) implements Sentencia {}
    public record Compute(String destino, Expr expr) implements Sentencia {}
    public record If(Condicion condicion, List<Sentencia> entonces, List<Sentencia> sino) implements Sentencia {}
    public record Display(List<Expr> partes) implements Sentencia {}
    public record StopRun() implements Sentencia {}

    // ---- Expresiones aritmeticas ----
    public sealed interface Expr permits Numero, Var, Texto, Binaria, Negativo {}
    public record Numero(String valor) implements Expr {}
    public record Var(String nombre) implements Expr {}
    /** Literal de texto; solo se permite en DISPLAY. */
    public record Texto(String valor) implements Expr {}
    public record Binaria(char op, Expr izq, Expr der) implements Expr {}
    public record Negativo(Expr expr) implements Expr {}

    // ---- Condiciones ----
    public sealed interface Condicion permits Comparacion, Logica {}
    /** op es uno de: > < = >= <= <> */
    public record Comparacion(Expr izq, String op, Expr der) implements Condicion {}
    /** op es AND u OR */
    public record Logica(String op, Condicion izq, Condicion der) implements Condicion {}
}
