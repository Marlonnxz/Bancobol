# BanCOBOL

Mini billetera digital (Spring Boot + Java 21) cuya lógica de saldo está escrita en COBOL.
Un transpilador propio (lexer -> parser -> AST -> Java) traduce `src/main/resources/cobol/*.cob`
y el Java generado se compila en memoria con `javax.tools.JavaCompiler`.

## Ejecutar

Requiere un JDK 21+ (no basta un JRE: se usa el compilador en tiempo de ejecución) y Maven.

    mvn spring-boot:run

Abrir http://localhost:8080. Cuentas de prueba: 3001234567 (Ana) y 3109876543 (Luis).
El saldo persiste en `./data/banco.mv.db` (H2 en archivo).

## Pruebas

    mvn test

## Documentación

Ver [doc/](doc/README.md): arquitectura, subconjunto COBOL, fases del transpilador y API.
