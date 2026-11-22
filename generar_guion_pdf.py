# -*- coding: utf-8 -*-
"""
Generador del Documento PDF: Guion de Sustentacion y Defensa de BanCOBOL.
Autores: Marlon Delgado (Frontend & Timeouts) & Julian Velandia (Backend & Compiladores)
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
            self.drawString(54, 32, "Marlon Delgado (Frontend & Timeouts) | Julian Velandia (Backend & Compiladores)")
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
    c_marlon = colors.HexColor("#0D6EFD")      # Blue (Frontend & Timeouts)
    c_julian = colors.HexColor("#198754")      # Green (Backend & Compiladores)
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
    styles.add(ParagraphStyle('SpeechSpeakerMarlon', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_marlon, spaceBefore=6, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('SpeechSpeakerJulian', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_julian, spaceBefore=6, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('SpeechText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9.5, leading=14, textColor=colors.HexColor("#111827"), spaceAfter=6))
    styles.add(ParagraphStyle('ActionNote', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=c_accent, spaceAfter=4))
    
    styles.add(ParagraphStyle('QTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_primary, spaceBefore=4, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle('QResp', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=c_dark, spaceAfter=6))
    styles.add(ParagraphStyle('TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=c_dark))
    styles.add(ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white))

    story = []

    def speech_box(speaker, role_desc, text_p, action_text=None, color_bar=c_marlon):
        header_p = Paragraph(f"<b>{speaker}</b> ({role_desc}):", styles['SpeechSpeakerMarlon' if speaker.startswith("Marlon") else 'SpeechSpeakerJulian'])
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
        [Paragraph("<b>Marlon Delgado</b>", styles['TableText']), Paragraph("<b>FRONTEND & UI</b>", styles['TableText']), Paragraph("Interfaz web SPA tipo Nequi, control y gestion estricta de timeouts (AbortController 8s e inactividad 2 min), consumo API REST y pantalla del Compilador.", styles['TableText'])],
        [Paragraph("<b>Julian Velandia</b>", styles['TableText']), Paragraph("<b>BACKEND & COMPILADORES</b>", styles['TableText']), Paragraph("Arquitectura Spring Boot, puente nativo JNA con DLL GnuCOBOL, transpilador completo (Lexer, Parser, AST, Generador), persistencia H2 y Docker.", styles['TableText'])],
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
        "Marlon Delgado", "Frontend & Timeouts",
        "Buenos dias, profesor y companeros. Hoy, junto a mi companero Julian Velandia, les presentamos BanCOBOL, una billetera digital transaccional inspirada en plataformas como Nequi. "
        "En este proyecto abordamos un reto clave de la ingenieria de software y de los lenguajes formales: modernizar y conectar la logica clasica bancaria escrita en COBOL con arquitecturas contemporaneas en Java y la web. "
        "Para este taller dividimos estrictamente los roles de desarrollo: yo estuve a cargo del diseno y construccion de todo el Frontend, la experiencia de usuario SPA y la gestion integral de timeouts en el navegador; mientras que Julian desarrollo el Backend en Spring Boot, el enlace nativo con la DLL de COBOL, la base de datos persistente y el motor del transpilador formal.",
        action_text="Abrir el navegador en http://localhost:8080 mostrando la pantalla principal de BanCOBOL."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Julian Velandia", "Backend & Compiladores",
        "Complementando la introduccion de Marlon, el nucleo de BanCOBOL resuelve un principio fundamental de la arquitectura financiera: 'Java transporta, orquesta y persiste los datos, pero COBOL decide estrictamente que pasa con el dinero'. "
        "Implementamos las cinco operaciones bancarias fundamentales: APERTURA de cuenta, CONSULTA de saldo, DEPOSITO (consignacion), RETIRO y TRANSFERENCIA interbancaria. "
        "Estas transacciones no estan resueltas con calculos arbitrarios en Java; residen en modulos COBOL compilados en una DLL nativa con GnuCOBOL y, de forma paralela, son procesadas por un transpilador propio que construimos aplicando la teoria formal de automatas, gramaticas libres de contexto y generacion de bytecode.",
        action_text="Senalar en las diapositivas o en el diagrama de arquitectura la coexistencia de la DLL nativa y el transpilador."
    ))
    story.append(Spacer(1, 10))

    # Acto 2
    story.append(Paragraph("ACTO II: FRONTEND Y GESTION INTEGRAL DE TIMEOUTS (2.5 min)", styles['SubSecHeading']))

    story.append(speech_box(
        "Marlon Delgado", "Frontend & Timeouts",
        "En el Frontend desarrollamos una Single Page Application (SPA) modular y ligera, construida sobre HTML5 semantico, CSS3 personalizado con modo visual responsivo y JavaScript moderno, sin sobrecargas de librerias de terceros para garantizar maxima reactividad.\n"
        "Uno de los requerimientos explicitos del taller fue la 'Interfaz grafica con gestion de timeouts'. En sistemas bancarios, la tolerancia a demoras de red y el abandono de terminales son riesgos criticos. Por ello, implementamos dos capas de timeouts en app.js:\n"
        "1. Timeout de Transporte HTTP (8 segundos): Cada invocacion asincrona 'fetch' se envuelve en un AbortController programado a 8.000 ms. Si la red se cae o el servidor demora mas de 8 segundos, la promesa se aborta limpiamente, desbloquea los formularios y le notifica al usuario: 'Tiempo de espera agotado (8s). Por favor revisa tus movimientos antes de reintentar para evitar duplicidades'.\n"
        "2. Timeout de Sesion por Inactividad (2 minutos con Banner de Advertencia): Escuchamos continuamente los eventos globales del usuario en el DOM ('mousemove', 'keydown', 'click', 'scroll'). Si pasan 90 segundos sin actividad, se activa un banner emergente con un contador regresivo visible de 30 segundos. Si el usuario interactua, el tiempo se renueva al instante; si transcurren los 30 segundos sin respuesta, la sesion se destruye en localStorage, los formularios se bloquean y el usuario es redirigido al login.",
        action_text="Mostrar en el codigo de app.js las funciones fetchConTimeout, temporizadorInactividad y la constante TIMEOUT_PETICION_MS = 8000."
    ))
    story.append(Spacer(1, 10))

    # Acto 3
    story.append(Paragraph("ACTO III: ARQUITECTURA BACKEND, DLL NATIVA Y MEMORIA BINARIA JNA (3 min)", styles['SubSecHeading']))
    
    story.append(speech_box(
        "Julian Velandia", "Backend & Compiladores",
        "En el Backend utilizamos Spring Boot 3.5.7 sobre Java 21, organizado en una arquitectura de capas limpias. Para las 5 operaciones obligatorias del taller (APERTURA, CONSULTA, DEPOSITO, RETIRO y TRANSFERENCIA), escribimos el codigo fuente en COBOL ANSI-85 estandar.\n"
        "Para ejecutar COBOL desde Java en tiempo real sin reiniciar el proceso, compilamos los cinco programas en una libreria dinamica nativa: banco.dll en Windows o libbanco.so en Linux mediante el compilador GnuCOBOL 3.2. Aplicamos tres principios tecnicos esenciales:\n"
        "1. LINKAGE SECTION y pasaje por referencia: Las variables compartidas viajan directamente en punteros de memoria.\n"
        "2. Formato binario nativo COMP-5: Definimos los montos monetarios como PIC S9(12)V99 COMP-5. COMP-5 le indica al compilador almacenar el numero como entero binario nativo de 64 bits (8 bytes), correspondiente al tipo 'long' en Java. El punto decimal implisito V99 significa que un saldo de $10.000,50 se transfiere en memoria como 1.000.050 centavos, eliminando cualquier error de punto flotante.\n"
        "3. GOBACK en vez de STOP RUN: En una libreria compartida, STOP RUN abortaria el proceso entero del sistema operativo apagando la JVM. GOBACK simplemente retorna el control y el estado de memoria al hilo de Java que lo invoco.",
        action_text="Mostrar el codigo de DEPOSITO.cob y senalar la LINKAGE SECTION y la sentencia GOBACK."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Julian Velandia", "Backend & Compiladores",
        "Para conectar Java con la DLL nativa utilizamos JNA (Java Native Access) en la clase CobolDll.java, prescindiendo del clasico y peligroso JNI en C. JNA asigna bloques contiguos de memoria con la clase 'Memory', pasa los apuntadores nativos e invoca la funcion correspondiente con proteccion contra condiciones de carrera.\n"
        "Ademas, en la persistencia con H2 y JPA, protegemos las cuentas durante transacciones concurrentes aplicando bloqueos pesimistas de escritura (@Lock(PESSIMISTIC_WRITE)), y en las transferencias ordenamos lexicograficamente los celulares de las cuentas para evitar de raiz cualquier posibilidad de interbloqueo o Deadlock.",
        action_text="Abrir CobolDll.java en IntelliJ o VSCode y mostrar el metodo ejecutar() con JNA."
    ))
    story.append(Spacer(1, 10))

    # Acto 4
    story.append(PageBreak())
    story.append(Paragraph("ACTO IV: EL TRANSPILADOR COBOL A JAVA (TEORIA DE COMPILADORES) (3 min)", styles['SubSecHeading']))

    story.append(speech_box(
        "Julian Velandia", "Backend & Compiladores",
        "El componente teorico central de nuestra materia es el Transpilador Source-to-Source de COBOL a Java. Implementamos un pipeline formal completo de cinco fases dentro del paquete co.edu.uptc.banco.transpiler:\n"
        "1. Analizador Lexico (Lexer.java): Transforma el flujo de caracteres en tokens semanticos mediante automatas y expresiones regulares, capturando palabras reservadas, identificadores, mascaras PIC y constantes numericas con su linea correspondiente.\n"
        "2. Analizador Sintactico (Parser.java): Es un parser descendente recursivo basado en la gramatica formal Libre de Contexto de COBOL. Valida las cuatro divisiones estructurales y maneja precedencia estricta de operadores aritmeticos (* y / sobre + y -) y logicos (AND sobre OR).\n"
        "3. Arbol de Sintaxis Abstracta (Ast.java): Construye una representacion jerarquica e inmutable del programa en memoria utilizando Java Records (Move, Add, Subtract, If, Perform, Display).\n"
        "4. Generador de Codigo Java (GeneradorJava.java): Traduce la semantica de COBOL a Java puro. Convierte las operaciones a metodos de BigDecimal con escala 2 y redondeo bancario HALF_EVEN. Emite la estructura ejecutable dentro de un bloque etiquetado 'break programa;' para asegurar que el mapa de memoria se actualice correctamente antes de retornar.\n"
        "5. Compilador en Memoria (CompiladorJava.java): A traves de ToolProvider.getSystemJavaCompiler(), el codigo Java generado se compila dinamicamente en memoria RAM sin escribir archivos en disco, cargandose en caliente con un ClassLoader personalizado.",
        action_text="Mostrar el paquete co.edu.uptc.banco.transpiler y resaltar el AST y el GeneradorJava."
    ))
    story.append(Spacer(1, 6))

    story.append(speech_box(
        "Marlon Delgado", "Frontend & Timeouts",
        "Para que cualquier usuario pueda interactuar con el transpilador sin abrir terminales, en el Frontend construi la pestana interactiva 'Compilador'. "
        "En esta pantalla se puede elegir cualquiera de los cinco programas o escribir codigo COBOL nuevo, enviarlo al backend y visualizar en dos paneles paralelos el codigo COBOL original y el codigo Java transpilado resultante. "
        "Ademas, cuenta con el boton 'Compilar y Ejecutar' que lanza la prueba del codigo generado y muestra el saldo y el estado retornado por el bytecode en tiempo real.",
        action_text="Hacer clic en la pestana 'Compilador' de la app web y cargar el programa RETIRO.cob mostrando los dos paneles."
    ))
    story.append(Spacer(1, 10))

    # Acto 5
    story.append(Paragraph("ACTO V: DEMOSTRACION EN VIVO (LIVE DEMO) (3 min)", styles['SubSecHeading']))
    story.append(Paragraph("Marlon opera la interfaz grafica en el proyector y Julian complementa explicando la ejecucion interna en la DLL y la base de datos.", styles['BodyCustomBold']))
    story.append(Spacer(1, 4))

    steps_demo = [
        ("Paso 1: Apertura y Consulta", "Marlon abre la cuenta 3001234567 con $50.000 COP y consulta el saldo.", "Julian explica: 'Se ejecuta APERTURA.cob en la DLL nativa y la cuenta se persiste en la base de datos H2 en disco.'"),
        ("Paso 2: Consignacion (DEPOSITO)", "Marlon consigna $30.000 COP. El saldo sube a $80.000 de forma reactiva.", "Julian senala: 'DEPOSITO.cob recibe el apuntador JNA, suma en COMP-5 binario y retorna CODIGO=00.'"),
        ("Paso 3: Retiro con validacion", "Marlon intenta retirar $100.000 COP. La app muestra la alerta roja: 'Fondos insuficientes'. Luego retira $20.000 exitosamente.", "Julian explica: 'COBOL valida IF LK-MONTO > LK-SALDO, retorna CODIGO=02 y el servicio Java cancela la operacion sin modificar el balance.'"),
        ("Paso 4: Transferencia entre cuentas", "Marlon transfiere $25.000 a la cuenta 3109876543.", "Julian explica: 'Opera TRANSFERENCIA.cob con bloqueos pesimistas ordenados en base de datos para garantizar consistencia total.'"),
        ("Paso 5: Demostracion de Timeouts", "Marlon demuestra el banner de inactividad de 2 minutos (con cuenta regresiva de 30s) y explica la cancelacion por AbortController a los 8s.", "Marlon enfatiza: 'La gestion de timeouts en el cliente previene transacciones zombi y sesiones abandonadas desprotegidas.'"),
        ("Paso 6: Demostracion de Transpilador y Persistencia", "Marlon compila y ejecuta RETIRO en la pestana del Compilador. Luego muestra la persistencia tras reiniciar.", "Julian demuestra: 'El codigo Java compilado en RAM produce exactamente el mismo resultado contable, y los datos persisten en ./data/bancodb.'")
    ]

    t_demo_data = [[Paragraph("<b>PASO</b>", styles['TableHeader']), Paragraph("<b>ACCION EN VIVO (MARLON)</b>", styles['TableHeader']), Paragraph("<b>EXPLICACION TECNICA (JULIAN)</b>", styles['TableHeader'])]]
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
        "Marlon Delgado", "Frontend & Timeouts",
        "En conclusion, demostramos que la interfaz de usuario de una entidad financiera puede ser moderna, rapida y segura, gestionando de forma estricta los tiempos de espera y la inactividad para proteger al usuario.",
        action_text=None
    ))
    story.append(Spacer(1, 4))
    story.append(speech_box(
        "Julian Velandia", "Backend & Compiladores",
        "Y desde la perspectiva de los lenguajes formales y la ingenieria de compiladores, demostramos la viabilidad de interoperar con software bancario legado mediante bibliotecas nativas C/COBOL y, al mismo tiempo, modernizarlo de raiz a traves de transpilacion formal a Java puro. Quedamos a su entera disposicion para las preguntas del jurado. Muchas gracias.",
        action_text="Proyectar la pantalla de preguntas o el repositorio en GitHub."
    ))

    # ==================== BANCO DE PREGUNTAS ====================
    story.append(PageBreak())
    story.append(Paragraph("PARTE 2: BANCO DE PREGUNTAS DIFICILES DEL PROFESOR Y RESPUESTAS BLINDADAS", styles['SecHeading']))
    story.append(Paragraph("Preparense estudiando estas 10 preguntas. Cada uno responde segun su area de especialidad en el proyecto.", styles['BodyCustom']))
    story.append(Spacer(1, 6))

    preguntas = [
        (
            "1. ¿Como funciona la gestion de Timeouts en el frontend y que previene?",
            "Marlon Delgado",
            "Implementamos dos capas independientes en app.js:\n"
            "1. Timeout de Red (8 segundos): Con la API estandar AbortController creamos una senal vinculada a cada peticion fetch con un setTimeout a 8.000 ms. Si el servidor o la red se demoran mas, la peticion se cancela y se captura en un catch amigable, evitando que la pantalla quede congelada o que el usuario reintente a ciegas provocando consignaciones duplicadas.\n"
            "2. Timeout de Sesion (2 minutos): Escuchamos continuamente los eventos del mouse y teclado. Si no hay interaccion durante 90 segundos, mostramos un banner visual con contador de 30 segundos. Si expira, se destruye la sesion en localStorage y se redirige al login para prevenir secuestros de sesion desatendida."
        ),
        (
            "2. ¿Por que el Transpilador es un compilador real y no un script de reemplazo con Regex?",
            "Julian Velandia",
            "Porque las expresiones regulares solo describen lenguajes regulares (Tipo 3 en la Jerarquia de Chomsky) y carecen de memoria para manejar estructuras anidadas o recursivas, como sentencias IF ... ELSE ... END-IF anidadas o expresiones aritmeticas complejas. "
            "Nuestro transpilador implementa un Analizador Lexico formal, un Parser Descendente Recursivo basado en una Gramatica Libre de Contexto (Tipo 2), genera un Arbol de Sintaxis Abstracta (AST) inmutable y luego aplica traduccion dirigida por la sintaxis hacia Java."
        ),
        (
            "3. ¿Por que usaron GOBACK en vez de STOP RUN en los programas COBOL?",
            "Julian Velandia",
            "Porque los programas COBOL estan compilados como una biblioteca dinamica compartida (DLL/.so) cargada dentro del mismo proceso de la JVM de Java. "
            "La instruccion STOP RUN en COBOL emite una llamada al sistema para terminar el proceso completo del sistema operativo, lo que apagaria de golpe todo el servidor Spring Boot. "
            "GOBACK unicamente finaliza el subprograma actual y devuelve de forma limpia el control y la memoria al hilo de Java que lo invoco."
        ),
        (
            "4. ¿Como garantizan que dos transferencias simultaneas no generen un Deadlock?",
            "Julian / Marlon",
            "Julian: 'En el backend aplicamos bloqueos pesimistas en la base de datos (SELECT ... FOR UPDATE con @Lock(PESSIMISTIC_WRITE)). Para erradicar deadlocks cuando dos personas se transfieren al mismo tiempo (A a B y B a A), ordenamos lexicograficamente las cuentas por su numero de celular antes de pedir el bloqueo, garantizando que todos los hilos adquieran los cerrojos en el mismo orden.'\n"
            "Marlon: 'Y en el frontend, si ocurriera un timeout o rechazo por concurrencia, el cliente recibe el error HTTP y desbloquea la interfaz sin perdida de datos ni bloqueos visuales.'"
        ),
        (
            "5. ¿Por que usaron COMP-5 en COBOL y como viajan los decimales a Java?",
            "Julian Velandia",
            "COMP-5 representa datos computacionales en formato binario nativo del procesador (little-endian en x86_64). "
            "PIC S9(12)V99 COMP-5 ocupa 8 bytes, exactamente igual que un 'long' de 64 bits en Java. "
            "Como los computadores no representan decimales en punto flotante IEEE 754 sin perder precision, la clausula V99 define dos decimales implicitos: $100.50 viaja en memoria como el entero 10050 centavos. En Java multiplicamos por 100 al llamar a COBOL y dividimos entre 100 al recibir usando BigDecimal con escala 2."
        ),
        (
            "6. ¿Que rol juega la pestana del 'Compilador' en el Frontend?",
            "Marlon Delgado",
            "La pestana Compilador permite que el usuario o el docente pruebe directamente el motor de transpilacion de forma visual e interactiva. "
            "Carga el archivo .cob original, realiza la llamada a la API REST /api/compilador/transpilar, recibe el codigo Java generado y lo formatea en dos paneles sincronizados. "
            "Ademas, permite presionar 'Compilar y Ejecutar' para probar el bytecode generado en caliente y ver el resultado exacto de la transaccion en pantalla."
        ),
        (
            "7. ¿Por que eligieron JNA en lugar del JNI tradicional para enlazar la DLL?",
            "Julian Velandia",
            "JNI exige escribir un pegamento intermedio en C, generar cabeceras .h con javah, compilar otra libreria C puente y administrar memoria manual propensa a fallos de segmentacion. "
            "JNA (Java Native Access) utiliza internamente libffi para invocar funciones nativas directamente desde Java mediante interfaces e instancias Memory, reduciendo codigo repetitivo y facilitando la portabilidad entre Windows (banco.dll) y Linux (libbanco.so)."
        ),
        (
            "8. ¿Como se resolvio la persistencia si se reinicia el contenedor Docker?",
            "Marlon / Julian",
            "Marlon: 'En el frontend el usuario no pierde su sesion porque se mantiene en localStorage.'\n"
            "Julian: 'Y en el backend, la base de datos H2 esta configurada en modo archivo sobre un volumen persistente de Docker (/app/data/bancodb). Todas las operaciones estan protegidas con @Transactional: o se guardan juntos el nuevo saldo y el movimiento en disco, o se aplica un rollback total ante cualquier error.'"
        ),
        (
            "9. ¿Como compila y ejecuta Java el codigo transpilado sin reiniciar la aplicacion?",
            "Julian Velandia",
            "Hacemos uso de la herramienta ToolProvider.getSystemJavaCompiler() incluida en el JDK. "
            "Creamos un JavaFileManager virtual en memoria RAM que toma el texto de la clase Java generada, la compila a bytecode binario sin crear archivos temporales en disco y, mediante un ClassLoader dinámico, carga la clase e invoca el metodo de transaccion mediante reflexion."
        ),
        (
            "10. ¿Que problema hubo con la señal SIGSEGV entre COBOL y Java en Docker y como se soluciono?",
            "Julian Velandia",
            "La JVM de Java HotSpot utiliza señales POSIX como SIGSEGV para coordinar puntos de recolección de basura (safepoints). Por su parte, la funcion cob_init() de GnuCOBOL registra su propio manejador global de señales, lo que causaba un fallo de memoria fatal. "
            "Lo solucionamos configurando en el Dockerfile la variable ENV LD_PRELOAD=/opt/java/openjdk/lib/libjsig.so, la cual encadena limpiamente los manejadores de señales entre la JVM y la biblioteca nativa de COBOL."
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
    story.append(Paragraph("Dominen estos terminos; les permitiran responder con propiedad formal ante cualquier observacion del docente.", styles['BodyCustom']))
    story.append(Spacer(1, 6))

    glosario_items = [
        ("Transpilador (Source-to-Source)", "Compilador que toma codigo fuente de un lenguaje de alto nivel (COBOL) y lo traduce a otro lenguaje del mismo nivel de abstraccion (Java), preservando la semantica."),
        ("Lexer / Scanner", "Fase inicial de un compilador que realiza analisis lexico. Agrupa una secuencia continua de caracteres en unidades minimas con significado llamadas 'tokens'."),
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
    story.append(Paragraph("<b>¡Muchos exitos a Marlon y Julian en la sustentacion! Tienen un proyecto impecable y una base teorica blindada.</b>", styles['DocSubtitle']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {os.path.abspath(filename)}")

if __name__ == '__main__':
    build_pdf()
