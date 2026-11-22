# -*- coding: utf-8 -*-
"""
Generador del Documento PDF: Guion de Sustentacion y Defensa de BanCOBOL.
Autores: Julian Velandia & Marlon Delgado
Materia: Lenguajes Formales - UPTC
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1A2B4C"))
            self.drawString(54, 11 * inch - 36, "BANCOBOL — GUION DE SUSTENTACION Y DEFENSA TECNICA")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#666666"))
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "Lenguajes Formales | UPTC")
            
            self.setStrokeColor(colors.HexColor("#D0D5DD"))
            self.setLineWidth(0.6)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Footer
            self.line(54, 45, 8.5 * inch - 54, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#667085"))
            self.drawString(54, 32, "Julian Velandia (Frontend & Timeouts) | Marlon Delgado (Backend & Compiladores)")
            self.drawRightString(8.5 * inch - 54, 32, f"Pagina {self._pageNumber} de {total_pages}")
        self.restoreState()


def build_pdf(filename="Guion_Exposicion_BANCOBOL.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1A2B4C")     # Navy
    c_secondary = colors.HexColor("#3F3D56")   # Slate
    c_julian = colors.HexColor("#0D6EFD")      # Blue
    c_marlon = colors.HexColor("#198754")      # Green
    c_accent = colors.HexColor("#D97706")      # Amber
    c_dark = colors.HexColor("#1F2937")        # Dark Neutral
    c_light = colors.HexColor("#F8FAFC")       # Light Gray
    c_border = colors.HexColor("#E2E8F0")

    # Typography styles
    styles.add(ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=c_primary, alignment=1))
    styles.add(ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=16, textColor=c_secondary, alignment=1))
    styles.add(ParagraphStyle('MetaHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=c_primary, alignment=1))
    
    styles.add(ParagraphStyle('SecHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=c_primary, spaceBefore=14, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle('SubSecHeading', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=c_secondary, spaceBefore=10, spaceAfter=4, keepWithNext=True))
    
    styles.add(ParagraphStyle('BodyCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, textColor=c_dark, spaceAfter=6))
    styles.add(ParagraphStyle('BodyCustomBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13.5, textColor=c_dark, spaceAfter=4))
    styles.add(ParagraphStyle('SpeechSpeakerJulian', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_julian, spaceBefore=6, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('SpeechSpeakerMarlon', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_marlon, spaceBefore=6, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('SpeechText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9.5, leading=14, textColor=colors.HexColor("#111827"), spaceAfter=6))
    styles.add(ParagraphStyle('ActionNote', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=c_accent, spaceAfter=4))
    
    styles.add(ParagraphStyle('QTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_primary, spaceBefore=4, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('QResp', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, spaceAfter=6))
    styles.add(ParagraphStyle('CodeSnippet', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=11, textColor=colors.HexColor("#0F172A")))
    styles.add(ParagraphStyle('TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=c_dark))
    styles.add(ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white))

    story = []

    def speech_box(speaker, role_desc, text_p, action_text=None, color_bar=c_julian):
        header_p = Paragraph(f"<b>{speaker}</b> ({role_desc}):", styles['SpeechSpeakerJulian' if speaker.startswith("Juli") else 'SpeechSpeakerMarlon'])
        body_p = Paragraph(f'"{text_p}"', styles['SpeechText'])
        items = [header_p, body_p]
        if action_text:
            items.append(Paragraph(f"<b>[ACCION / EN PANTALLA]:</b> {action_text}", styles['ActionNote']))
            
        t = Table([[items]], colWidths=[7.2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('LINELEFT', (0,0), (0,-1), 3.5, color_bar),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        return t

    # ==================== PORTADA ====================
    story.append(Spacer(1, 15))
    story.append(Paragraph("UNIVERSIDAD PEDAGOGICA Y TECNOLOGICA DE COLOMBIA (UPTC)", styles['MetaHeader']))
    story.append(Paragraph("FACULTAD DE INGENIERIA — ESCUELA DE INGENIERIA DE SISTEMAS Y COMPUTACION", styles['MetaHeader']))
    story.append(Paragraph("CURSO: LENGUAJES FORMALES | SEMANA 15 — PROYECTO FINAL", styles['MetaHeader']))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=5, spaceAfter=15))
    
    story.append(Paragraph("BanCOBOL", styles['DocTitle']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Billetera Digital Transaccional basada en Compilador GnuCOBOL (DLL nativa) y Transpilador Formal a Java", styles['DocSubtitle']))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=5, spaceAfter=15))
    
    # Integrantes Table
    info_data = [
        [Paragraph("<b>INTEGRANTE</b>", styles['TableHeader']), Paragraph("<b>ROL ASIGNADO</b>", styles['TableHeader']), Paragraph("<b>RESPONSABILIDAD PRINCIPAL</b>", styles['TableHeader'])],
        [Paragraph("<b>Julian Velandia</b>", styles['TableText']), Paragraph("<b>FRONTEND & UI</b>", styles['TableText']), Paragraph("Interfaz web SPA, control y gestion de timeouts (red e inactividad), consumo API REST y experiencia de usuario.", styles['TableText'])],
        [Paragraph("<b>Marlon Delgado</b>", styles['TableText']), Paragraph("<b>BACKEND & COMPILADORES</b>", styles['TableText']), Paragraph("Spring Boot, puente nativo JNA con DLL GnuCOBOL, transpilador completo (Lexer, Parser, AST, Generador), persistencia H2 y Docker.", styles['TableText'])],
    ]
    t_info = Table(info_data, colWidths=[2.0 * inch, 2.0 * inch, 3.2 * inch])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    # Resumen Ejecutivo
    story.append(Paragraph("<b>Objetivo de la Sustentacion:</b>", styles['BodyCustomBold']))
    story.append(Paragraph(
        "Demostrar que el sistema cumple rigurosamente con los requerimientos del Taller de Semana 15: "
        "(1) Mini app bancaria tipo Nequi con persistencia de saldo; "
        "(2) Minimo 5 operaciones bancarias escritas en COBOL y compiladas en DLL nativa; "
        "(3) Transpilador propio que aplica la teoria de Lenguajes Formales (analisis lexico, sintactico, semantico y generacion de codigo Java); "
        "(4) Interfaz grafica con gestion explicita de timeouts (timeout de peticion HTTP y timeout de sesion por inactividad); "
        "(5) Separacion estricta y sustentable de roles entre los dos integrantes.",
        styles['BodyCustom']
    ))
    story.append(Spacer(1, 10))

    # ==================== GUION ACTO POR ACTO ====================
    story.append(PageBreak())
    story.append(Paragraph("PARTE 1: GUION SECUENCIAL DE SUSTENTACION (TURNO A TURNO)", styles['SecHeading']))
    story.append(Paragraph("Sigan este orden exacto durante la presentacion. Duracion estimada: 10 a 12 minutos.", styles['BodyCustom']))
    story.append(Spacer(1, 8))

    # Acto 1
    story.append(Paragraph("ACTO I: INTRODUCCION Y PLANTEAMIENTO DEL PROBLEMA (2 min)", styles['SubSecHeading']))
    
    story.append(speech_box(
        "Julian Velandia", "Frontend & Timeouts",
        "Buenos dias, profesor y companeros. Hoy, junto a mi companero Marlon Delgado, les presentamos BanCOBOL, una billetera digital transaccional inspirada en plataformas como Nequi. "
        "En este proyecto abordamos un reto de la ingenieria de software real y de los lenguajes formales: modernizar y conectar la logica clasica bancaria escrita en COBOL con arquitecturas contemporaneas en Java y la web. "
        "Para este taller, asumimos una division estricta de trabajo: yo estuve a cargo del diseno y desarrollo del Frontend, la experiencia de usuario y la gestion de timeouts en el cliente; mientras que Marlon desarrollo el Backend en Spring Boot, el puente nativo con la DLL de COBOL y el motor del transpilador formal.",
        action_text="Abrir el navegador en http://localhost:8080 mostrando la pantalla de bienvenida / login con el celular."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Marlon Delgado", "Backend & Compiladores",
        "Complementando la introduccion de Julian, el nucleo de BanCOBOL resuelve una premisa fundamental de la banca: 'Java decide como se transporta y guarda la informacion, pero COBOL decide estrictamente que pasa con el dinero'. "
        "Nuestra solucion implementa las cinco operaciones bancarias obligatorias: APERTURA de cuenta, CONSULTA de saldo, DEPOSITO (consignacion), RETIRO y TRANSFERENCIA interbancaria. "
        "Estas reglas no estan calculadas con if o sumas en Java; residen en archivos .cob compilados en una DLL nativa con GnuCOBOL y, en paralelo, son procesadas por un transpilador propio que construimos desde cero aplicando automatas, gramaticas libres de contexto y generacion de bytecode.",
        action_text="Senalar en las diapositivas o en el diagrama de arquitectura la separacion entre la DLL nativa y el transpilador."
    ))
    story.append(Spacer(1, 10))

    # Acto 2
    story.append(Paragraph("ACTO II: ARQUITECTURA Y LAS 5 OPERACIONES EN COBOL (3 min)", styles['SubSecHeading']))
    
    story.append(speech_box(
        "Marlon Delgado", "Backend & Compiladores",
        "Hablemos de las reglas en COBOL. En la carpeta src/main/resources/cobol/ tenemos los cinco programas fuente. Para que un programa COBOL pueda ser invocado dinamicamente desde Java sin detener el servidor, aplicamos tres decisiones tecnicas cruciales que vimos en clase:\n"
        "1. LINKAGE SECTION y PROCEDURE DIVISION USING: Los parametros viajan por referencia en memoria. Lo que COBOL modifica en esa direccion, Java lo lee inmediatamente.\n"
        "2. Formato binario nativo COMP-5: Usamos PIC S9(12)V99 COMP-5. Esto le dice a GnuCOBOL que represente el saldo no como texto, sino como un entero binario de 64 bits (8 bytes), equivalente al tipo 'long' en Java. El V99 representa dos decimales fijos, por lo que una transaccion de $5.000,50 viaja en memoria como el entero 500050 centavos, eliminando cualquier error de precision flotante.\n"
        "3. Sentencia GOBACK en lugar de STOP RUN: En un entorno de libreria dinamica, STOP RUN abortaria y apagaria la JVM entera. GOBACK simplemente devuelve el control y el estado de ejecucion a quien lo invoco.",
        action_text="Mostrar rapidamente el codigo de DEPOSITO.cob o TRANSFERENCIA.cob en pantalla."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Marlon Delgado", "Backend & Compiladores",
        "Las operaciones devuelven siempre una variable CODIGO: 0 para exito, 1 para monto invalido, 2 para fondos insuficientes y 3 para saldo inconsistente. Si el codigo es diferente de cero, COBOL garantiza atomicidad no alterando los saldos. "
        "Todas estas operaciones fueron compiladas en una sola libreria dinamica dll/banco.dll usando el script PowerShell con cobc -b -free. En Java, nuestra clase CobolDll utiliza JNA (Java Native Access) para reservar bloques de memoria 'Memory', pasar los punteros e invocar las funciones nativas con total sincronizacion de hilos.",
        action_text="Mostrar la clase CobolDll.java y destacar el metodo ejecutar() con JNA."
    ))
    story.append(Spacer(1, 10))

    # Acto 3
    story.append(Paragraph("ACTO III: FRONTEND Y GESTION CRITICA DE TIMEOUTS (2.5 min)", styles['SubSecHeading']))

    story.append(speech_box(
        "Julian Velandia", "Frontend & Timeouts",
        "Pasando a la interfaz de usuario, disenamos una Single Page Application (SPA) pura en HTML5, CSS moderno y JavaScript modular, sin librerias pesadas para garantizar maxima velocidad y compatibilidad en dispositivos moviles.\n"
        "Uno de los requerimientos mas exigentes del taller era la 'Gestion de Timeouts', y en BanCOBOL la implementamos en dos niveles esenciales del lado cliente:\n"
        "1. Timeout de Peticion HTTP (8 segundos): Cada vez que el frontend realiza una peticion con fetch, creamos un AbortController configurado a 8.000 ms. Si el servidor se congestiona o no responde antes de 8 segundos, la peticion se aborta y le informamos al usuario: 'El servidor no respondio en 8 segundos; revisa tus movimientos antes de reintentar para no duplicar consignaciones'.\n"
        "2. Timeout de Sesion por Inactividad (2 minutos): Como en Nequi, si el usuario no realiza ninguna accion durante 120 segundos, la sesion se destruye por seguridad. Pero para ofrecer una buena experiencia, a los 90 segundos disparamos un banner de advertencia visual con una cuenta regresiva segundo a segundo de 30 segundos. Si el usuario hace clic o presiona una tecla, el temporizador se reinicia inmediatamente; si no contesta, el sistema limpia el localStorage y lo expulsa al login.",
        action_text="Mostrar en app.js las constantes TIMEOUT_PETICION_MS = 8000 e INACTIVIDAD_MS = 120000, junto con el evento de reinicio de actividad."
    ))
    story.append(Spacer(1, 10))

    # Acto 4
    story.append(PageBreak())
    story.append(Paragraph("ACTO IV: EL TRANSPILADOR COBOL -> JAVA (TEORIA DE COMPILADORES) (3 min)", styles['SubSecHeading']))

    story.append(speech_box(
        "Marlon Delgado", "Backend & Compiladores",
        "Ademas de invocar la DLL nativa, el taller exigia implementar la transpilacion de COBOL a Java. En el paquete co.edu.uptc.banco.cobol implementamos un pipeline completo de cinco fases formales:\n"
        "1. Analizador Lexico (Lexer.java): Lee el texto COBOL caracter por caracter. Mediante automatas finitos y expresiones regulares extrae tokens (PALABRA, NUMERO, CADENA, SIMBOLO, PUNTO, y la mascara PIC mediante regex como S?9+(\\(\\d+\\))?(V9+(\\(\\d+\\))?)?). Registra el numero de linea exacto de cada token para reportar errores amigables.\n"
        "2. Analizador Sintactico (Parser.java): Es un parser descendente recursivo basado en la gramatica formal BNF de COBOL. Maneja precedencia de operadores (* y / sobre + y -) mediante niveles de funciones (expr -> termino -> factor) y condiciones booleanas (AND tiene mayor precedencia que OR). Valida las secciones IDENTIFICATION, DATA y PROCEDURE DIVISION, asegurando que las variables usadas hayan sido declaradas previamente.\n"
        "3. Arbol de Sintaxis Abstracta (Ast.java): Genera estructuras inmutables en memoria usando 'records' de Java (Move, Add, Subtract, Compute, If, Display, StopRun).\n"
        "4. Generador de Java (GeneradorJava.java): Realiza la traduccion dirigida por la sintaxis. Recorre el AST y genera clases Java que implementan Consumer<Map<String, BigDecimal>>. Transforma tipos COMP-5 en BigDecimal con escala 2 y redondeo bancario HALF_EVEN. Traduce STOP RUN como un bloque etiquetado 'break programa;' para asegurar que las variables resultantes siempre se guarden en el mapa de memoria antes de salir.\n"
        "5. Compilador en Memoria (CompiladorJava.java): Con ToolProvider.getSystemJavaCompiler(), compila el codigo Java generado al vuelo y lo carga con un ClassLoader custom en memoria, sin escribir archivos temporales en el disco duro.",
        action_text="Mostrar el flujo en la pantalla 'Compilador' de la app donde se ve el COBOL a la izquierda y el Java generado a la derecha."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Julian Velandia", "Frontend & Timeouts",
        "En el Frontend integramos una pantalla interactiva llamada 'Compilador COBOL'. Desde alli, cualquier usuario o docente puede seleccionar cualquiera de los 5 programas (como APERTURA, DEPOSITO o TRANSFERENCIA) y ver en tiempo real el codigo COBOL original frente al codigo Java que nuestro generador construyo. Esto permite verificar la equivalencia semantica de las operaciones de manera visual e inmediata.",
        action_text="En la interfaz web, hacer clic en el boton 'Compilador' y alternar entre los programas DEPOSITO y TRANSFERENCIA."
    ))
    story.append(Spacer(1, 10))

    # Acto 5
    story.append(Paragraph("ACTO V: DEMOSTRACION EN VIVO (LIVE DEMO) (3 min)", styles['SubSecHeading']))
    story.append(Paragraph("En esta fase, Julian maneja la interfaz web en el proyector y Marlon complementa explicando lo que ocurre internamente en la base de datos y la DLL.", styles['BodyCustomBold']))
    story.append(Spacer(1, 4))

    steps_demo = [
        ("Paso 1: Ingreso a cuenta de prueba", "Julian ingresa con el celular 3001234567 (Ana). Muestra el saldo disponible de $525.000 COP y el historial.", "Marlon explica: 'Al ingresar, se ejecuta el programa CONSULTA.cob en la DLL para verificar la consistencia del saldo antes de desplegarlo.'"),
        ("Paso 2: Consignacion (DEPOSITO)", "Julian consigna $50.000 COP. La pantalla se actualiza inmediatamente mostrando el saldo nuevo.", "Marlon senala la terminal Docker: 'Miren la consola: DEPOSITO.cob se ejecuto en C/COBOL y emitio el DISPLAY: DEPOSITO OK, NUEVO SALDO.'"),
        ("Paso 3: Retiro con validacion de fondos", "Julian intenta retirar $1.000.000 COP. La app muestra la alerta en rojo: 'Fondos insuficientes'. Luego retira $20.000 exitosamente.", "Marlon explica: 'COBOL evaluo IF MONTO > SALDO, retorno CODIGO=2, el servicio Java atrapo el codigo y lanzo un HttpStatus 422 sin tocar el dinero.'"),
        ("Paso 4: Transferencia entre cuentas", "Julian transfiere $30.000 al celular 3109876543 (Luis).", "Marlon explica: 'Aqui opera TRANSFERENCIA.cob con bloqueo pesimista ordenado de cuentas en la base H2, evitando condiciones de carrera (deadlocks).'"),
        ("Paso 5: Demostracion de Timeouts", "Julian se detiene y muestra el banner de inactividad que aparece a los 90s, o desconecta la red para mostrar el AbortController de 8s.", "Julian resalta: 'Aqui vemos como la interfaz cumple con la gestion estricta de timeouts exigida en las reglas del taller.'"),
        ("Paso 6: Demostracion de Persistencia", "Julian cierra sesion o se reinicia el contenedor Docker con docker compose restart.", "Marlon demuestra: 'Los datos estan guardados en ./data/banco.mv.db. Aunque se reinicie la app, el saldo y los movimientos persisten.'")
    ]

    t_demo_data = [[Paragraph("<b>PASO</b>", styles['TableHeader']), Paragraph("<b>ACCION EN VIVO (JULIAN)</b>", styles['TableHeader']), Paragraph("<b>EXPLICACION TECNICA (MARLON)</b>", styles['TableHeader'])]]
    for p, a, e in steps_demo:
        t_demo_data.append([Paragraph(f"<b>{p}</b>", styles['TableText']), Paragraph(a, styles['TableText']), Paragraph(e, styles['TableText'])])
    
    t_demo = Table(t_demo_data, colWidths=[1.7 * inch, 2.7 * inch, 2.8 * inch])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 10))

    # Acto 6
    story.append(Paragraph("ACTO VI: CIERRE Y CONCLUSIONES (1 min)", styles['SubSecHeading']))
    story.append(speech_box(
        "Julian Velandia", "Frontend & Timeouts",
        "En conclusion, demostramos que es perfectamente viable construir aplicaciones financieras amigables, robustas y seguras, gestionando de forma confiable eventos asincronos y tiempos de espera desde el navegador.",
        action_text=None
    ))
    story.append(Spacer(1, 4))
    story.append(speech_box(
        "Marlon Delgado", "Backend & Compiladores",
        "Y desde la perspectiva de los lenguajes formales, comprobamos la potencia de las fases clasicas de la compilacion: desde el analisis lexico y sintactico hasta la generacion de codigo y la interoperabilidad nativa entre lenguajes de diferentes epocas como COBOL y Java. Quedamos atentos a sus preguntas. Muchas gracias.",
        action_text="Proyectar la pantalla de preguntas o la arquitectura general."
    ))

    # ==================== BANCO DE PREGUNTAS ====================
    story.append(PageBreak())
    story.append(Paragraph("PARTE 2: BANCO DE PREGUNTAS DIFICILES DEL PROFESOR Y RESPUESTAS BLINDADAS", styles['SecHeading']))
    story.append(Paragraph("Preparense estudiando estas 10 preguntas. El docente casi con seguridad hara al menos 3 o 4 de ellas.", styles['BodyCustom']))
    story.append(Spacer(1, 6))

    preguntas = [
        (
            "1. ¿Por que usaron GOBACK en vez de STOP RUN en los programas COBOL?",
            "Marlon",
            "Porque nuestros programas COBOL estan compilados dentro de una DLL dinamica compartida (libreria nativa) invocada por el proceso de Java. "
            "En COBOL, la instruccion STOP RUN termina completamente el proceso en ejecucion del sistema operativo, lo que apagaria abruptamente todo el servidor Spring Boot. "
            "Por el contrario, GOBACK finaliza unicamente el subprograma actual y le devuelve limpiamente el control y los datos a la aplicacion Java que lo llamo."
        ),
        (
            "2. ¿Cual es la diferencia entre la DLL y el Transpilador? ¿Cual mueve el dinero real?",
            "Marlon",
            "El dinero real SIEMPRE lo mueve la DLL nativa (banco.dll compilada con GnuCOBOL) mediante JNA. El servicio BancoService llama a CobolDll.ejecutar(). "
            "El transpilador (Lexer -> Parser -> Ast -> GeneradorJava -> CompiladorJava) se construyo para aplicar formalmente la teoria de la materia: alimenta la pantalla didactica 'Compilador' de la app, permite correr pruebas unitarias sin depender de compiladores de C/COBOL instalados y extrae del AST el orden y los tipos de parametros USING."
        ),
        (
            "3. ¿Por que un Analizador Lexico (Regex) no es suficiente para compilar COBOL?",
            "Marlon",
            "Porque las expresiones regulares y los automatas finitos solo reconocen lenguajes regulares (Tipo 3 de Chomsky). No tienen memoria de pila y son incapaces de manejar estructuras anidadas o recursivas, como por ejemplo sentencias IF ... THEN ... IF ... ELSE ... END-IF o expresiones aritmeticas con parentesis balanceados (A + (B * (C - D))). "
            "Para reconocer esa anidacion se requiere obligatoriamente una Gramatica Libre de Contexto (Tipo 2) procesada por un Parser descendente recursivo."
        ),
        (
            "4. ¿Como garantizan la precedencia de operadores (*, / sobre +, -) en el Parser?",
            "Marlon",
            "La precedencia no esta resuelta con condicionales 'if' sueltos, sino codificada directamente en la jerarquia de la gramatica BNF:\n"
            "• expr() maneja las sumas y restas (+, -), llamando primero a termino().\n"
            "• termino() maneja multiplicaciones y divisiones (*, /), llamando primero a factor().\n"
            "• factor() resuelve los elementos atomicos (numeros, variables o expresiones entre parentesis).\n"
            "De este modo, cuando el parser encuentra 'A + B * C', el arbol sintactico agrupa naturalmente 'B * C' en un nodo inferior antes de sumarlo con 'A'."
        ),
        (
            "5. ¿Por que usaron COMP-5 en COBOL y como viajan los decimales a Java?",
            "Marlon",
            "COMP-5 representa datos computacionales en formato binario nativo del procesador (little-endian en x86_64). "
            "PIC S9(12)V99 COMP-5 ocupa 8 bytes, exactamente igual que un 'long' de Java. "
            "Como los computadores no representan decimales en punto flotante sin perder precision, la clausula V99 define 2 decimales implicitos fijos: $100.50 viaja en memoria como el entero 10050 centavos. Java multiplica por 100 al enviar y divide entre 100 al recibir en un BigDecimal con escala 2."
        ),
        (
            "6. ¿Como resolvieron la gestion de timeouts en el frontend?",
            "Julian",
            "Implementamos dos mecanismos independientes en app.js:\n"
            "1. En peticiones de red: Usamos la API estandar AbortController con setTimeout a 8.000 ms. Si la peticion tarda mas, se dispara el metodo abort() y se captura en un bloque catch que muestra un mensaje preventivo al usuario para evitar dobles transacciones.\n"
            "2. En sesiones de usuario: Tenemos un temporizador de inactividad a 120.000 ms (2 min). A los 90 segundos mostramos un banner visual con cuenta regresiva de 30 segundos. Escuchamos eventos globales en el DOM ('click', 'keydown', 'touchstart') para reiniciar el contador si el usuario interactua. Si el contador llega a 0, se destruye la sesion de localStorage y se devuelve al login."
        ),
        (
            "7. ¿Que pasa si dos usuarios se transfieren dinero mutuamente al mismo tiempo? (Deadlocks)",
            "Marlon / Julian",
            "Marlon: 'Lo prevenimos en BancoService aplicando bloqueo pesimista en base de datos (SELECT ... FOR UPDATE con @Lock(PESSIMISTIC_WRITE)). Para evitar un interbloqueo o deadlock entre dos transferencias simultaneas (A->B y B->A), el codigo siempre bloquea las dos cuentas en orden lexicografico estricto de su numero celular (primero el menor y luego el mayor). Ademas, H2 tiene configurado un LOCK_TIMEOUT=5000 ms para abortar si alguna transaccion supera los 5 segundos.'\n"
            "Julian: 'Y si eso llegara a fallar, el frontend captura el error HTTP 400/409/500 y le avisa limpiamente al usuario en la pantalla.'"
        ),
        (
            "8. ¿Por que el saldo persiste si se apaga el servidor o se cae la app?",
            "Julian / Marlon",
            "Julian: 'En el frontend el usuario no pierde su sesion porque se guarda en localStorage.'\n"
            "Marlon: 'Y en el backend, la base de datos H2 no esta configurada en memoria (:mem:), sino en archivo local: jdbc:h2:file:./data/banco. Todas las transacciones tienen @Transactional: o se guardan juntos el nuevo saldo y el movimiento en disco (data/banco.mv.db), o ante cualquier excepcion se aplica rollback completo.'"
        ),
        (
            "9. ¿Por que en el transpilador tradujeron STOP RUN como 'break programa;' y no como 'return;'?",
            "Marlon",
            "Porque la clase Java generada recibe un mapa de memoria (Map<String, BigDecimal> memoria). Si usaramos 'return;', el metodo terminaria de inmediato sin ejecutar las lineas finales memoria.put('SALDO', SALDO) que devuelven los valores actualizados al llamador. "
            "Al envolver el PROCEDURE DIVISION en un bloque etiquetado 'programa: { ... }' y usar 'break programa;', el flujo salta ordenadamente al bloque final de asignacion al mapa."
        ),
        (
            "10. ¿Por que necesitaron un JDK completo y no solo un JRE para correr el proyecto?",
            "Marlon",
            "Porque nuestra fase 4 (CompiladorJava.java) invoca dinamicamente la interfaz JavaCompiler provista por ToolProvider.getSystemJavaCompiler(). Esta API es el propio 'javac' integrado en Java, el cual solo viene incluido en el Java Development Kit (JDK). Un JRE comun carece de compilador y lanzaria un IllegalStateException al intentar transpilar en caliente."
        )
    ]

    for q, quien, r in preguntas:
        story.append(Paragraph(f"<b>{q}</b>", styles['QTitle']))
        story.append(Paragraph(f"<b>Quien responde preferiblemente:</b> <font color='{c_marlon if quien.startswith('Marlon') else c_julian}'>{quien}</font>", styles['BodyCustomBold']))
        story.append(Paragraph(f"<b>Respuesta modelo:</b> {r}", styles['QResp']))
        story.append(Spacer(1, 3))

    # ==================== GLOSARIO ====================
    story.append(PageBreak())
    story.append(Paragraph("PARTE 3: GLOSARIO TECNICO PARA DEFENDERSE COMO UN SENIOR", styles['SecHeading']))
    story.append(Paragraph("Dominen estos terminos; si el profesor los usa en una pregunta, ustedes sabran exactamente a que se refiere.", styles['BodyCustom']))
    story.append(Spacer(1, 6))

    glosario_items = [
        ("Transpilador (Source-to-Source)", "Compilador que toma codigo fuente de un lenguaje de alto nivel (COBOL) y lo traduce a otro lenguaje del mismo nivel de abstraccion (Java), preservando la semantica."),
        ("Lexer / Scanner", "Fase inicial de un compilador que realiza analisis lexico. Agrupa una secuencia de caracteres en unidades minimas con significado llamadas 'tokens'."),
        ("Parser / Analizador Sintactico", "Fase que comprueba que la secuencia de tokens cumpla las reglas gramaticales formales (Gramatica Libre de Contexto) y construye el arbol sintactico."),
        ("Descendente Recursivo", "Tecnica de parsing LL(1) donde cada regla no terminal de la gramatica BNF se implementa directamente como una funcion o metodo recursivo en el codigo."),
        ("AST (Abstract Syntax Tree)", "Arbol de Sintaxis Abstracta: representacion jerarquica e intermedia de la estructura sintactica del programa, libre de elementos decorativos como puntos o parentesis redundantes."),
        ("COMP-5 (COBOL)", "Formato computacional binario nativo que almacena numeros respetando la representacion del hardware anfitrion (2, 4 u 8 bytes enteros), ideal para interoperar con tipos primitivos de C y Java."),
        ("JNA (Java Native Access)", "Libreria de Java que permite invocar funciones exportadas en librerias nativas (DLL en Windows o SO en Linux) directamente sin tener que escribir codigo de puente JNI en C/C++."),
        ("AbortController", "API estandar de JavaScript que permite senalizar y cancelar peticiones asincronas de red (fetch) si sobrepasan un tiempo limite estipulado (Timeout)."),
        ("Bloqueo Pesimista (PESSIMISTIC_WRITE)", "Estrategia de concurrencia a nivel de base de datos que bloquea los registros involucrados (SELECT ... FOR UPDATE) hasta que la transaccion termina, impidiendo lecturas sucias y carreras entre hilos."),
        ("GnuCOBOL (cobc)", "Compilador libre y estandar de COBOL que traduce codigo COBOL a C y luego genera binarios nativos ejecutables o librerias dinamicas (DLL/.so).")
    ]

    t_glo_data = [[Paragraph("<b>TERMINO</b>", styles['TableHeader']), Paragraph("<b>DEFINICION Y RELEVANCIA EN EL PROYECTO</b>", styles['TableHeader'])]]
    for term, defn in glosario_items:
        t_glo_data.append([Paragraph(f"<b>{term}</b>", styles['TableText']), Paragraph(defn, styles['TableText'])])
    
    t_glo = Table(t_glo_data, colWidths=[2.2 * inch, 5.0 * inch])
    t_glo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
    ]))
    story.append(t_glo)
    story.append(Spacer(1, 15))

    # Mensaje de exito final
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("<b>¡Muchos exitos a Julian y Marlon en la sustentacion! Tienen un proyecto impecable y una base teorica blindada.</b>", styles['DocSubtitle']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {os.path.abspath(filename)}")

if __name__ == '__main__':
    build_pdf()
