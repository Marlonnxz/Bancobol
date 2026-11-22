# Etapa 1: Build con Maven y JDK 21 oficial + GnuCOBOL
FROM maven:3.9-eclipse-temurin-21 AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnucobol \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Descargar dependencias Maven primero (cache de capas)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copiar código fuente y recursos COBOL
COPY src ./src

# Compilar los 5 programas COBOL en dll/banco.dll
RUN mkdir -p dll && \
    cobc -b -free -o dll/banco.dll src/main/resources/cobol/*.cob

# Compilar y empaquetar el JAR de la aplicación
RUN mvn clean package -DskipTests

# Etapa 2: Imagen final de ejecución (JDK 21 para soportar compilación en memoria del transpilador)
FROM eclipse-temurin:21-jdk

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnucobol \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar la DLL compilada y el JAR generado
COPY --from=build /app/dll ./dll
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

# Volumen para persistir los saldos y transacciones en disco
VOLUME ["/app/data"]

ENV BANCO_COBOL_DLL=./dll/banco.dll
ENV BANCO_COBOL_RUNTIME=/usr/lib/x86_64-linux-gnu
# libjsig encadena las señales entre GnuCOBOL y el recolector/JIT de Java
ENV LD_PRELOAD=/opt/java/openjdk/lib/libjsig.so

ENTRYPOINT ["java", "--enable-native-access=ALL-UNNAMED", "-jar", "app.jar"]
