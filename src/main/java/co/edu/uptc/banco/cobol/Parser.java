package co.edu.uptc.banco.cobol;

import co.edu.uptc.banco.cobol.Ast.*;
import co.edu.uptc.banco.cobol.Lexer.Tipo;
import co.edu.uptc.banco.cobol.Lexer.Token;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Fase 2: analisis sintactico descendente recursivo. Gramatica (simplificada):
 *
 * <pre>
 * programa    ::= IDENTIFICATION DIVISION . PROGRAM-ID . nombre .
 *                 DATA DIVISION . WORKING-STORAGE SECTION . variable*
 *                 PROCEDURE DIVISION . sentencia*
 * variable    ::= nivel nombre PIC mascara [VALUE ['-'] numero] .
 * sentencia   ::= (move | add | subtract | compute | if | display | STOP RUN) ['.']
 * move        ::= MOVE factor TO variable
 * add         ::= ADD factor TO variable
 * subtract    ::= SUBTRACT factor FROM variable
 * compute     ::= COMPUTE variable = expr
 * if          ::= IF condicion [THEN] sentencia* [ELSE sentencia*] END-IF
 * display     ::= DISPLAY (cadena | numero | variable)+
 * condicion   ::= condY (OR condY)*
 * condY       ::= comparacion (AND comparacion)*
 * comparacion ::= expr [NOT] ('>' | '<' | '=' | '>=' | '<=') expr
 * expr        ::= termino (('+' | '-') termino)*
 * termino     ::= factor (('*' | '/') factor)*
 * factor      ::= numero | variable | '-' factor | '(' expr ')'
 * </pre>
 */
public class Parser {

    private final List<Token> tokens;
    private int pos = 0;
    private final Map<String, Variable> variables = new LinkedHashMap<>();

    public Parser(List<Token> tokens) {
        this.tokens = tokens;
    }

    public Programa programa() {
        esperar("IDENTIFICATION"); esperar("DIVISION"); punto();
        esperar("PROGRAM-ID"); punto();
        String nombre = esperarTipo(Tipo.PALABRA, "el nombre del programa").texto(); punto();

        esperar("DATA"); esperar("DIVISION"); punto();
        esperar("WORKING-STORAGE"); esperar("SECTION"); punto();
        while (actual().tipo() == Tipo.NUMERO) variable();

        esperar("PROCEDURE"); esperar("DIVISION"); punto();
        List<Sentencia> sentencias = sentencias();
        if (actual().tipo() != Tipo.FIN) throw error("'" + actual().texto() + "' sin IF correspondiente");
        return new Programa(nombre, List.copyOf(variables.values()), sentencias);
    }

    // ---------------- DATA DIVISION ----------------

    private void variable() {
        Token nivel = avanzar();
        if (!nivel.texto().equals("01") && !nivel.texto().equals("77")) {
            throw new CobolException(nivel.linea(), "solo se soportan variables de nivel 01 o 77");
        }
        Token nombre = esperarTipo(Tipo.PALABRA, "el nombre de la variable");
        if (variables.containsKey(nombre.texto())) {
            throw new CobolException(nombre.linea(), "variable duplicada '" + nombre.texto() + "'");
        }
        if (!aceptar("PIC")) esperar("PICTURE");
        String pic = esperarTipo(Tipo.PIC, "la máscara PIC").texto();
        String valor = "0";
        if (aceptar("VALUE")) {
            if (!(aceptar("ZERO") || aceptar("ZEROS") || aceptar("ZEROES"))) {
                String signo = aceptar("-") ? "-" : "";
                valor = signo + esperarTipo(Tipo.NUMERO, "un número después de VALUE").texto();
            }
        }
        punto();
        variables.put(nombre.texto(), new Variable(nombre.texto(), pic, valor));
    }

    // ---------------- PROCEDURE DIVISION ----------------

    /** Lee sentencias hasta encontrar ELSE, END-IF o el fin del archivo. */
    private List<Sentencia> sentencias() {
        List<Sentencia> lista = new ArrayList<>();
        while (true) {
            while (actual().tipo() == Tipo.PUNTO) avanzar(); // los puntos son opcionales
            Token t = actual();
            if (t.tipo() == Tipo.FIN || t.es("ELSE") || t.es("END-IF")) return lista;
            lista.add(sentencia());
        }
    }

    private Sentencia sentencia() {
        Token t = avanzar();
        if (t.tipo() != Tipo.PALABRA) {
            throw new CobolException(t.linea(), "se esperaba una sentencia pero se encontró '" + t.texto() + "'");
        }
        switch (t.texto()) {
            case "MOVE": {
                Expr origen = factor();
                esperar("TO");
                return new Move(origen, variableDeclarada());
            }
            case "ADD": {
                Expr valor = factor();
                esperar("TO");
                return new Add(valor, variableDeclarada());
            }
            case "SUBTRACT": {
                Expr valor = factor();
                esperar("FROM");
                return new Subtract(valor, variableDeclarada());
            }
            case "COMPUTE": {
                String destino = variableDeclarada();
                esperar("=");
                return new Compute(destino, expr());
            }
            case "IF": {
                Condicion cond = condicion();
                aceptar("THEN");
                List<Sentencia> entonces = sentencias();
                List<Sentencia> sino = aceptar("ELSE") ? sentencias() : List.of();
                esperar("END-IF");
                return new If(cond, entonces, sino);
            }
            case "DISPLAY": {
                List<Expr> partes = new ArrayList<>();
                do {
                    Token p = actual();
                    if (p.tipo() == Tipo.CADENA) partes.add(new Texto(avanzar().texto()));
                    else if (p.tipo() == Tipo.NUMERO) partes.add(new Numero(avanzar().texto()));
                    else partes.add(new Var(variableDeclarada()));
                } while (actual().tipo() == Tipo.CADENA || actual().tipo() == Tipo.NUMERO || esVariable(actual()));
                return new Display(partes);
            }
            case "STOP": {
                esperar("RUN");
                return new StopRun();
            }
            default:
                throw new CobolException(t.linea(), "sentencia desconocida '" + t.texto() + "'");
        }
    }

    // ---------------- Condiciones ----------------

    private Condicion condicion() {
        Condicion c = condicionY();
        while (aceptar("OR")) c = new Logica("OR", c, condicionY());
        return c;
    }

    private Condicion condicionY() {
        Condicion c = comparacion();
        while (aceptar("AND")) c = new Logica("AND", c, comparacion());
        return c;
    }

    private Condicion comparacion() {
        Expr izq = expr();
        boolean negado = aceptar("NOT");
        Token op = avanzar();
        String simbolo = switch (op.tipo() == Tipo.SIMBOLO ? op.texto() : "") {
            case ">" -> negado ? "<=" : ">";
            case "<" -> negado ? ">=" : "<";
            case "=" -> negado ? "<>" : "=";
            case ">=", "<=" -> {
                if (negado) throw new CobolException(op.linea(), "NOT no se puede combinar con " + op.texto());
                yield op.texto();
            }
            default -> throw new CobolException(op.linea(),
                    "se esperaba un operador de comparación pero se encontró '" + op.texto() + "'");
        };
        return new Comparacion(izq, simbolo, expr());
    }

    // ---------------- Expresiones ----------------

    private Expr expr() {
        Expr e = termino();
        while (actual().es("+") || actual().es("-")) {
            char op = avanzar().texto().charAt(0);
            e = new Binaria(op, e, termino());
        }
        return e;
    }

    private Expr termino() {
        Expr e = factor();
        while (actual().es("*") || actual().es("/")) {
            char op = avanzar().texto().charAt(0);
            e = new Binaria(op, e, factor());
        }
        return e;
    }

    private Expr factor() {
        if (actual().tipo() == Tipo.NUMERO) return new Numero(avanzar().texto());
        if (aceptar("-")) return new Negativo(factor());
        if (aceptar("(")) {
            Expr e = expr();
            esperar(")");
            return e;
        }
        return new Var(variableDeclarada());
    }

    private String variableDeclarada() {
        Token t = esperarTipo(Tipo.PALABRA, "una variable");
        if (!variables.containsKey(t.texto())) {
            throw new CobolException(t.linea(), "variable no declarada '" + t.texto() + "'");
        }
        return t.texto();
    }

    private boolean esVariable(Token t) {
        return t.tipo() == Tipo.PALABRA && variables.containsKey(t.texto());
    }

    // ---------------- Utilidades ----------------

    private Token actual() {
        return tokens.get(pos);
    }

    private Token avanzar() {
        Token t = tokens.get(pos);
        if (t.tipo() != Tipo.FIN) pos++;
        return t;
    }

    private boolean aceptar(String texto) {
        if (actual().es(texto)) {
            pos++;
            return true;
        }
        return false;
    }

    private void esperar(String texto) {
        if (!aceptar(texto)) throw error("se esperaba '" + texto + "' pero se encontró '" + actual().texto() + "'");
    }

    private Token esperarTipo(Tipo tipo, String descripcion) {
        if (actual().tipo() != tipo) {
            throw error("se esperaba " + descripcion + " pero se encontró '" + actual().texto() + "'");
        }
        return avanzar();
    }

    private void punto() {
        if (actual().tipo() != Tipo.PUNTO) throw error("se esperaba '.' pero se encontró '" + actual().texto() + "'");
        avanzar();
    }

    private CobolException error(String mensaje) {
        return new CobolException(actual().linea(), mensaje);
    }
}
