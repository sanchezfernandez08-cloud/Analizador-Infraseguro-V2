# EXPORTADOR PDF v2 — Motor Genérico Infraseguro Chile
import sys
sys.path.insert(0, '/home/claude')
from motor_generico import CasoSeguro, calcular, FUNDAMENTOS_CI, explicar_vub, DESGLOSE_VUB
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image as RLImage
import io
from PIL import Image as PILImage

# ── Paleta A PLUS Ajustadores ─────────────────────────────────────────────────
AZ  = rl_colors.HexColor("#183363")   # Azul oscuro principal
AZM = rl_colors.HexColor("#335FB3")   # Azul medio subtítulos
AZC = rl_colors.HexColor("#B4CDE0")   # Celeste fondos de fila
NR  = rl_colors.HexColor("#FF7640")   # Naranja acento/alerta
NRB = rl_colors.HexColor("#FFE8DC")   # Naranja claro fondo
GR  = rl_colors.HexColor("#AFADA8")   # Gris texto secundario
GL  = rl_colors.HexColor("#D5D4D1")   # Gris borde líneas
GF  = rl_colors.HexColor("#F5F7FA")   # Gris muy claro fondo filas
RJ  = rl_colors.HexColor("#C0392B")   # Rojo alerta (infraseguro)
RJB = rl_colors.HexColor("#FADBD8")   # Rojo claro fondo alerta
VD  = rl_colors.HexColor("#1E8449")   # Verde OK
VDB = rl_colors.HexColor("#D5F5E3")   # Verde claro fondo OK
W   = 17.0 * cm

def fmt(n):        return f"{round(n):,}".replace(",",".")
def fmtd(n, d=1):  return f"{n:.{d}f}".replace(".",",")
def pct_s(v):      return f"{fmtd(v*100,1)}%"

def S(name, **kw): return ParagraphStyle(name, **kw)

sT    = S("T",  fontSize=16, textColor=AZ,  fontName="Helvetica-Bold",  spaceAfter=3,  alignment=1)
sST   = S("ST", fontSize=9,  textColor=AZM, fontName="Helvetica",       spaceAfter=2,  alignment=1)
sH    = S("H",  fontSize=11, textColor=AZ,  fontName="Helvetica-Bold",  spaceBefore=12, spaceAfter=4)
sH2   = S("H2", fontSize=10, textColor=NR,  fontName="Helvetica-Bold",  spaceBefore=8,  spaceAfter=3)
sN    = S("N",  fontSize=8.5, fontName="Helvetica", spaceAfter=2, leading=13)
sNI   = S("NI", fontSize=8,  fontName="Helvetica-Oblique", spaceAfter=2,
          textColor=GR, leading=12)
sJust = S("J",  fontSize=8.5, fontName="Helvetica", spaceAfter=4, leading=13, alignment=4)
sFte  = S("FT", fontSize=7.5, fontName="Helvetica-Oblique", spaceAfter=3, leading=11,
          textColor=GR, alignment=4)
sF    = S("F",  fontSize=7,  fontName="Helvetica", alignment=1, textColor=GR)


def mktab(filas, col_widths, extra=None):
    t = Table(filas, colWidths=col_widths)
    base = [
        ("BACKGROUND",(0,0),(-1,0),AZ), ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GF,rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.4,GL),
        ("ALIGN",(1,0),(-1,-1),"RIGHT"), ("ALIGN",(0,0),(0,-1),"LEFT"),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),4),  ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]
    if extra: base += extra
    t.setStyle(TableStyle(base)); return t


def box_ci(key, res):
    """Genera los elementos visuales del bloque de un costo indirecto."""
    fd    = FUNDAMENTOS_CI[key]
    pct   = res["pcts"][key]
    monto = res["ci_detalle"][key]
    just  = res["justificaciones"][key]
    rango = f"{fmtd(fd['rango_min']*100,0)}%–{fmtd(fd['rango_max']*100,0)}%"
    es_default = (pct == fd["pct_default"])

    # Cabecera azul
    hdr = Table([
        [Paragraph(f"<b>{fd['label'].upper()}</b>",
                   S("bh", fontSize=8.5, fontName="Helvetica-Bold", textColor=rl_colors.white)),
         Paragraph(f"<b>Aplicado: {pct_s(pct)}  |  UF {fmt(monto)}</b>",
                   S("bv", fontSize=8.5, fontName="Helvetica-Bold",
                     textColor=rl_colors.white, alignment=2))],
        [Paragraph(f"Rango de mercado: {rango}",
                   S("rg", fontSize=8, fontName="Helvetica-Oblique", textColor=rl_colors.white)),
         Paragraph("Valor default" if es_default else "⚠ Valor personalizado",
                   S("rv", fontSize=8, fontName="Helvetica-Bold",
                     textColor=rl_colors.HexColor("#fbbf24") if not es_default else rl_colors.white,
                     alignment=2))],
    ], colWidths=[10*cm, 7*cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),AZM),
        ("GRID",(0,0),(-1,-1),0.3,rl_colors.HexColor("#1e3a5f")),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),5),  ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))

    # Fuente
    fuente_table = Table([[
        Paragraph("<b>Fuente y justificación:</b> " + just, sFte)
    ]], colWidths=[W])
    fuente_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NRB),
        ("BOX",(0,0),(-1,-1),0.4,NR),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),5),  ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))

    # Componentes
    comp_rows = [[Paragraph("<b>Qué incluye este componente:</b>",
                            S("ch", fontSize=8, fontName="Helvetica-Bold", textColor=AZ))]]
    for comp in fd["componentes"]:
        comp_rows.append([Paragraph(f"• {comp}", sN)])
    comp_t = Table(comp_rows, colWidths=[W])
    comp_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),AZC),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[GF,rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.3,GL),
        ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),3),  ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    return [hdr, fuente_table, comp_t, Spacer(1, 0.35*cm)]


def build_pdf(caso: CasoSeguro, path: str):
    res = calcular(caso); c = caso
    vub_exp = explicar_vub(caso, res)
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # ── Encabezado con logo corporativo ────────────────────────────────────
    LOGO_PATH = "/home/claude/logo_aplus.png"
    import os

    # Estilos de título con más espacio interno
    sTitulo = S("TIT", fontSize=17, textColor=AZ, fontName="Helvetica-Bold",
                spaceBefore=6, spaceAfter=6, alignment=0, leading=22)
    sSubtit = S("SUB", fontSize=10, textColor=AZM, fontName="Helvetica",
                spaceBefore=4, spaceAfter=4, alignment=0, leading=14)
    sLegal  = S("LEG", fontSize=8,  textColor=GR,  fontName="Helvetica-Oblique",
                spaceBefore=2, spaceAfter=0, alignment=0, leading=11)

    if os.path.exists(LOGO_PATH):
        # Logo a la izquierda — bloque de títulos a la derecha con más aire
        logo_img = RLImage(LOGO_PATH, width=5.8*cm, height=3.58*cm)
        title_block = [
            Spacer(1, 0.4*cm),
            Paragraph("Análisis de Montos Asegurados", sTitulo),
            Spacer(1, 0.15*cm),
            Paragraph("Informe de Valor de Reconstrucción e Infraseguro", sSubtit),
            Spacer(1, 0.1*cm),
            Paragraph("DFL 251  ·  DS 1055  ·  CCom Art. 553  ·  Ley 19.537", sLegal),
            Spacer(1, 0.4*cm),
        ]
        hdr_table = Table(
            [[logo_img, title_block]],
            colWidths=[6.0*cm, 11.0*cm]
        )
        hdr_table.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (0,0),   12),   # espacio entre logo y texto
            ("RIGHTPADDING", (1,0), (1,0),   0),
            ("TOPPADDING",   (0,0), (-1,-1), 0),
            ("BOTTOMPADDING",(0,0), (-1,-1), 0),
        ]))
        story += [
            Spacer(1, 0.5*cm),
            hdr_table,
            Spacer(1, 0.3*cm),
            HRFlowable(width="100%", thickness=3, color=NR),
            Spacer(1, 0.08*cm),
            HRFlowable(width="100%", thickness=0.5, color=AZ),
            Spacer(1, 0.4*cm),
        ]
    else:
        story += [
            Spacer(1, 0.5*cm),
            Paragraph("Análisis de Montos Asegurados", sT),
            Spacer(1, 0.15*cm),
            Paragraph("Informe de Valor de Reconstrucción e Infraseguro", sST),
            Spacer(1, 0.1*cm),
            Paragraph("DFL 251  ·  DS 1055  ·  CCom Art. 553  ·  Ley 19.537", sST),
            Spacer(1, 0.4*cm),
            HRFlowable(width="100%", thickness=3, color=NR),
            Spacer(1, 0.08*cm),
            HRFlowable(width="100%", thickness=0.5, color=AZ),
            Spacer(1, 0.4*cm),
        ]

    # ── 1. Identificación ──────────────────────────────────────────────────
    story.append(Paragraph("1. IDENTIFICACIÓN DEL ASEGURADO Y LA PÓLIZA", sH))
    story.append(mktab([
        ["Campo","Dato"],
        ["Asegurado",c.nombre], ["RUT",c.rut_asegurado or "—"],
        ["Dirección",c.direccion], ["Póliza",c.poliza or "—"],
        ["Corredor",c.corredor or "—"], ["Fecha de análisis",c.fecha_analisis],
    ], [8*cm,9*cm]))
    story.append(Spacer(1,0.3*cm))

    # ── 2. Descripción inmueble ────────────────────────────────────────────
    story.append(Paragraph("2. DESCRIPCIÓN DEL INMUEBLE", sH))
    story.append(mktab([
        ["Parámetro","Valor"],
        ["Tipo de inmueble",c.tipo_inmueble], ["Sistema constructivo",c.sistema],
        ["Nivel de terminaciones",c.nivel], ["N° de pisos",str(c.numero_pisos)],
        ["Año de construcción",str(c.anio_construccion)], ["Zona geográfica",c.zona],
        ["Superficie asegurable",f"{fmt(c.superficie_m2)} m²"],
        ["IVA aplicable","Sí (19%)" if c.aplica_iva else "No aplica"],
    ], [8*cm,9*cm]))
    if c.nota_superficie:
        story += [Spacer(1,0.2*cm), Paragraph(f"⚠ {c.nota_superficie}", sNI)]
    story.append(Spacer(1,0.3*cm))

    # ── 3. Factores ────────────────────────────────────────────────────────
    story.append(Paragraph("3. FACTORES DE AJUSTE APLICADOS", sH))
    story.append(mktab([
        ["Factor","Valor","Fundamento"],
        ["VUB — Valor Unitario Base", f"{res['vub']} UF/m²",
         f"Tabla: {c.tipo_inmueble} / {c.sistema} / Nivel {c.nivel}"],
        ["Factor geográfico (Fg)", fmtd(res['fg'],2), f"Zona {c.zona}"],
        ["Factor normativo (Fn)", fmtd(res['fn'],2), f"Año construcción {c.anio_construccion}"],
        ["Factor de altura (Fa)", fmtd(res['fa'],2), f"{c.numero_pisos} pisos"],
    ], [6*cm,3.5*cm,7.5*cm]))
    story.append(Spacer(1,0.3*cm))

    # ── 4. DESGLOSE EXPLICATIVO DEL VUB ──────────────────────────────────────
    story.append(Paragraph("4. VUB — VALOR UNITARIO BASE: ORIGEN Y COMPOSICIÓN", sH))

    # Bloque explicativo general
    intro_vub = Table([[Paragraph(vub_exp["nota_general"], sFte)]], colWidths=[W])
    intro_vub.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), rl_colors.HexColor("#EBF3FB")),
        ("BOX",(0,0),(-1,-1), 0.8, AZM),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),7),   ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    story.append(intro_vub)
    story.append(Spacer(1, 0.3*cm))

    # Bloque sistema constructivo + nivel de terminaciones
    story.append(Paragraph("¿Cómo se eligió el VUB aplicado?", sH2))

    desc_rows = [
        ["Tipo inmueble",       c.tipo_inmueble,                       ""],
        ["Sistema constructivo",c.sistema,                             vub_exp["desc_sistema"]],
        ["Nivel de terminaciones", c.nivel,                           vub_exp["desc_nivel"]],
        ["VUB resultante",      f"{res['vub']} UF/m²",
         "Valor paramétrico según tabla de la industria aseguradora chilena"],
    ]
    sWDesc = S("WD", fontSize=8, fontName="Helvetica", leading=11, textColor=GR)
    sWVal  = S("WV", fontSize=8.5, fontName="Helvetica-Bold", leading=11, textColor=AZ)
    sWLbl  = S("WL", fontSize=8.5, fontName="Helvetica-Bold", leading=11)

    desc_table_rows = [[
        Paragraph("Parámetro", S("DH", fontSize=8.5, fontName="Helvetica-Bold",
                  textColor=rl_colors.white, leading=11)),
        Paragraph("Valor", S("VH", fontSize=8.5, fontName="Helvetica-Bold",
                  textColor=rl_colors.white, leading=11)),
        Paragraph("Qué significa", S("QH", fontSize=8.5, fontName="Helvetica-Bold",
                  textColor=rl_colors.white, leading=11)),
    ]]
    for lbl, val, desc in desc_rows:
        is_vub = "resultante" in lbl
        desc_table_rows.append([
            Paragraph(lbl, S(f"DL{lbl[:3]}", fontSize=8.5, fontName="Helvetica-Bold", leading=11,
                      textColor=NR if is_vub else AZ)),
            Paragraph(val, S(f"VL{val[:3]}", fontSize=8.5,
                      fontName="Helvetica-Bold" if is_vub else "Helvetica",
                      leading=11, textColor=NR if is_vub else rl_colors.black)),
            Paragraph(desc, sWDesc),
        ])
    t_desc = Table(desc_table_rows, colWidths=[4*cm, 3*cm, 10*cm])
    t_desc.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),  AZ),
        ("ROWBACKGROUNDS",(0,1),  (-1,-2), [GF, rl_colors.white]),
        ("BACKGROUND",    (0,-1), (-1,-1), rl_colors.HexColor("#FFF3EC")),
        ("GRID",          (0,0),  (-1,-1), 0.4, GL),
        ("LEFTPADDING",   (0,0),  (-1,-1), 6),
        ("RIGHTPADDING",  (0,0),  (-1,-1), 6),
        ("TOPPADDING",    (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 5),
        ("VALIGN",        (0,0),  (-1,-1), "TOP"),
    ]))
    story.append(t_desc)
    story.append(Spacer(1, 0.3*cm))

    # Desglose por componentes del VUB
    story.append(Paragraph("¿En qué se descompone el VUB por cada metro cuadrado?", sH2))
    story.append(Paragraph(
        "El VUB representa el costo directo de construir 1 m² de la edificación. "
        "Se distribuye internamente entre cuatro grandes grupos de partidas, "
        "según proporciones típicas de la industria de la construcción chilena "
        "(CChC, CDT, MINVU). A continuación se muestra la estimación de cuántas "
        "UF representa cada grupo por cada metro cuadrado asegurable:", sJust))
    story.append(Spacer(1, 0.2*cm))

    for i, comp in enumerate(vub_exp["componentes"]):
        uf_m2  = comp["uf_m2"]
        pct_v  = int(comp["pct"]*100)
        bg_hdr = AZ if i % 2 == 0 else AZM

        # Cabecera del componente
        comp_hdr = Table([[
            Paragraph(f"{comp['label'].upper()}",
                      S(f"CH{i}", fontSize=8.5, fontName="Helvetica-Bold",
                        textColor=rl_colors.white, leading=11)),
            Paragraph(f"≈ {pct_v}% del VUB  |  aprox. {uf_m2} UF/m²",
                      S(f"CV{i}", fontSize=8.5, fontName="Helvetica-Bold",
                        textColor=rl_colors.white, leading=11, alignment=2)),
        ]], colWidths=[10*cm, 7*cm])
        comp_hdr.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), bg_hdr),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ]))

        # Descripción + fuente
        comp_body = Table([[
            Paragraph(comp["descripcion"], sJust),
        ]], colWidths=[W])
        comp_body.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), GF if i%2==0 else rl_colors.white),
            ("BOX",(0,0),(-1,-1),0.4,GL),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        comp_fuente = Table([[
            Paragraph(f"Fuente: {comp['fuente']}", sFte),
        ]], colWidths=[W])
        comp_fuente.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), rl_colors.HexColor("#F0F4F8")),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))

        story += [comp_hdr, comp_body, comp_fuente, Spacer(1, 0.2*cm)]

    # Tabla resumen del desglose VUB
    story.append(Paragraph("Resumen: distribución del VUB por componente", sH2))
    vub_resumen = [[
        Paragraph("Componente",   S("RH0",fontSize=8.5,fontName="Helvetica-Bold",textColor=rl_colors.white,leading=11)),
        Paragraph("% del VUB",    S("RH1",fontSize=8.5,fontName="Helvetica-Bold",textColor=rl_colors.white,leading=11,alignment=2)),
        Paragraph("UF/m²",        S("RH2",fontSize=8.5,fontName="Helvetica-Bold",textColor=rl_colors.white,leading=11,alignment=2)),
        Paragraph("UF total caso",S("RH3",fontSize=8.5,fontName="Helvetica-Bold",textColor=rl_colors.white,leading=11,alignment=2)),
    ]]
    total_uf = 0
    for comp in vub_exp["componentes"]:
        uf_total_comp = round(comp["uf_m2"] * c.superficie_m2)
        total_uf += uf_total_comp
        vub_resumen.append([
            Paragraph(comp["label"], S(f"RL{comp['key'][:3]}",fontSize=8.5,fontName="Helvetica",leading=11)),
            Paragraph(f"{int(comp['pct']*100)}%", S(f"RP{comp['key'][:3]}",fontSize=8.5,fontName="Helvetica",leading=11,alignment=2)),
            Paragraph(f"UF {comp['uf_m2']:.2f}", S(f"RU{comp['key'][:3]}",fontSize=8.5,fontName="Helvetica",leading=11,alignment=2)),
            Paragraph(f"UF {fmt(uf_total_comp)}", S(f"RT{comp['key'][:3]}",fontSize=8.5,fontName="Helvetica",leading=11,alignment=2)),
        ])
    vub_resumen.append([
        Paragraph("COSTO DIRECTO TOTAL (VUB × Superficie)",
                  S("RTL",fontSize=8.5,fontName="Helvetica-Bold",leading=11,textColor=AZ)),
        Paragraph(f"100%",
                  S("RTp",fontSize=8.5,fontName="Helvetica-Bold",leading=11,alignment=2,textColor=AZM)),
        Paragraph(f"UF {res['vub']}",
                  S("RTu",fontSize=8.5,fontName="Helvetica-Bold",leading=11,alignment=2,textColor=AZM)),
        Paragraph(f"UF {fmt(res['costo_directo'])}",
                  S("RTt",fontSize=8.5,fontName="Helvetica-Bold",leading=11,alignment=2,textColor=AZM)),
    ])
    t_vub_res = Table(vub_resumen, colWidths=[7.5*cm, 2*cm, 2.8*cm, 4.7*cm])
    t_vub_res.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),  AZ),
        ("ROWBACKGROUNDS",(0,1),  (-1,-2), [GF, rl_colors.white]),
        ("BACKGROUND",    (0,-1), (-1,-1), AZC),
        ("GRID",          (0,0),  (-1,-1), 0.4, GL),
        ("LEFTPADDING",   (0,0),  (-1,-1), 6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",    (0,0),  (-1,-1), 5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
    ]))
    story.append(t_vub_res)
    story.append(Spacer(1, 0.3*cm))
    story.append(PageBreak())

    # ── 5. Costos indirectos — núcleo del informe ──────────────────────────
    story.append(Paragraph("5. COSTOS INDIRECTOS — FUNDAMENTOS Y JUSTIFICACIÓN POR COMPONENTE", sH))
    story.append(Paragraph(
        "ADVERTENCIA METODOLÓGICA: No existe en Chile una norma única que fije los porcentajes "
        "de costos indirectos para efectos de seguros. Los valores aplicados provienen de "
        "práctica de mercado, doctrina del contrato de construcción y referencias gremiales "
        "(CChC, Colegio de Arquitectos). Cada componente se documenta y justifica "
        "individualmente. El liquidador puede ajustar cualquier porcentaje cuando cuente con "
        "presupuesto real de contratista o antecedentes específicos del caso concreto.", sJust))
    story.append(Spacer(1,0.3*cm))

    for key in FUNDAMENTOS_CI:
        for elem in box_ci(key, res):
            story.append(elem)

    # Resumen CI
    story.append(Paragraph("Cuadro resumen — costos indirectos aplicados", sH2))
    # 4 columnas con wrap | anchos: 7.5 + 2.2 + 3.3 + 4.0 = 17.0 cm exactos
    sWp  = S("Wp",  fontSize=8.5, fontName="Helvetica",      leading=11)
    sWpB = S("WpB", fontSize=8.5, fontName="Helvetica-Bold", leading=11)

    def _p(txt, bold=False, align=0, color=rl_colors.black):
        fn = "Helvetica-Bold" if bold else "Helvetica"
        return Paragraph(txt, S(f"_p{id(txt)}", fontSize=8.5, fontName=fn,
                         leading=11, alignment=align, textColor=color))

    ci_header = [
        _p("Componente",    bold=True, color=rl_colors.white),
        _p("% Aplicado",    bold=True, align=2, color=rl_colors.white),
        _p("Monto (UF)",    bold=True, align=2, color=rl_colors.white),
        _p("Rango mercado", bold=True, align=1, color=rl_colors.white),
    ]
    ci_filas2 = [ci_header]
    for key, fd in FUNDAMENTOS_CI.items():
        ci_filas2.append([
            _p(fd["label"]),
            _p(pct_s(res["pcts"][key]), align=2),
            _p(f"UF {fmt(res['ci_detalle'][key])}", align=2),
            _p(f"{fmtd(fd['rango_min']*100,0)}%\u2013{fmtd(fd['rango_max']*100,0)}%", align=1,
               color=rl_colors.HexColor("#475569")),
        ])
    ci_filas2.append([
        _p("TOTAL COSTOS INDIRECTOS", bold=True),
        _p(pct_s(res["pct_total_ci"]), bold=True, align=2, color=AZM),
        _p(f"UF {fmt(res['costos_indirectos'])}", bold=True, align=2, color=AZM),
        _p("—", align=1),
    ])
    t_ci = Table(ci_filas2, colWidths=[7.5*cm, 2.2*cm, 3.3*cm, 4.0*cm], repeatRows=1)
    t_ci.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),  (-1,0),  AZ),
        ("ROWBACKGROUNDS",(0,1),  (-1,-2), [GF, rl_colors.white]),
        ("BACKGROUND",    (0,-1), (-1,-1), AZC),
        ("GRID",          (0,0),  (-1,-1), 0.4, GL),
        ("LEFTPADDING",   (0,0),  (-1,-1), 6),
        ("RIGHTPADDING",  (0,0),  (-1,-1), 6),
        ("TOPPADDING",    (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING", (0,0),  (-1,-1), 5),
        ("VALIGN",        (0,0),  (-1,-1), "MIDDLE"),
    ]))
    story.append(t_ci)
    story.append(Spacer(1,0.3*cm))
    story.append(PageBreak())

    # ── 5. Desglose económico ──────────────────────────────────────────────
    story.append(Paragraph("6. DESGLOSE DEL CÁLCULO", sH))
    story.append(Paragraph(
        f"Fórmula: VR = Superficie × VUB × Fg × Fn × Fa × (1 + CI total) × (1 + IVA)", sNI))
    story.append(Paragraph(
        f"VR = {fmt(c.superficie_m2)} m² × {res['vub']} × {fmtd(res['fg'],2)} × "
        f"{fmtd(res['fn'],2)} × {fmtd(res['fa'],2)} × "
        f"{fmtd(1+res['pct_total_ci'],4)} × "
        f"{'1,19' if c.aplica_iva else '1,00'} = UF {fmt(res['vr'])}", sNI))
    story.append(Spacer(1,0.2*cm))
    sub = res["subtotal"]
    des = [["Concepto","Monto (UF)"]]
    des.append([f"Costo directo ({fmt(c.superficie_m2)} m² × {res['vub']} × "
                f"{fmtd(res['fg'],2)} × {fmtd(res['fn'],2)} × {fmtd(res['fa'],2)})",
                f"UF {fmt(res['costo_directo'])}"])
    for key, fd in FUNDAMENTOS_CI.items():
        des.append([f"  {fd['label']} ({pct_s(res['pcts'][key])})",
                    f"UF {fmt(res['ci_detalle'][key])}"])
    des += [
        [f"Subtotal costos indirectos ({pct_s(res['pct_total_ci'])})", f"UF {fmt(res['costos_indirectos'])}"],
        ["Subtotal antes de IVA", f"UF {fmt(sub)}"],
        ["IVA 19%" if c.aplica_iva else "IVA",
         f"UF {fmt(res['iva_monto'])}" if c.aplica_iva else "No aplica"],
        ["VALOR DE RECONSTRUCCIÓN", f"UF {fmt(res['vr'])}"],
    ]
    story.append(mktab(des, [11*cm,6*cm], extra=[
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("BACKGROUND",(0,-1),(-1,-1),AZC), ("TEXTCOLOR",(1,-1),(1,-1),AZM),
        ("FONTNAME",(0,-4),(-1,-4),"Helvetica-Bold"),
        ("FONTNAME",(0,-3),(-1,-3),"Helvetica-Bold"),
    ]))
    story.append(Spacer(1,0.3*cm))

    # ── 6. Póliza ──────────────────────────────────────────────────────────
    story.append(Paragraph("7. ANÁLISIS DE PÓLIZA E INFRASEGURO", sH))
    story.append(mktab([
        ["Concepto","Monto (UF)"],
        ["Monto asegurado actual", f"UF {fmt(c.monto_asegurado)}"],
        ["Valor de reconstrucción", f"UF {fmt(res['vr'])}"],
        ["Cobertura real", f"{fmtd(res['ratio']*100,1)}%"],
        ["Protección infraseguro (±10%)", "Activa" if res["proteccion_activa"] else "No activa ✗"],
        ["INFRASEGURO", "SÍ ⚠" if res["infraseguro"] else "NO ✓"],
        ["Brecha sin cubrir", f"UF {fmt(res['brecha'])}" if res["infraseguro"] else "—"],
        ["Monto asegurado recomendado", f"UF {fmt(res['vr'])}"],
    ], [11*cm,6*cm], extra=[
        ("TEXTCOLOR",(1,3),(1,3),NR), ("FONTNAME",(1,3),(1,3),"Helvetica-Bold"),
        *([("TEXTCOLOR",(0,4),(-1,5),RJ),("FONTNAME",(0,4),(-1,5),"Helvetica-Bold"),
           ("BACKGROUND",(0,4),(-1,5),RJB)]
          if res["infraseguro"] else
          [("TEXTCOLOR",(0,4),(-1,4),VD),("FONTNAME",(0,4),(-1,4),"Helvetica-Bold"),
           ("BACKGROUND",(0,4),(-1,4),VDB)]),
        ("TEXTCOLOR",(0,-1),(-1,-1),VD), ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("BACKGROUND",(0,-1),(-1,-1),VDB),
    ]))
    story.append(Spacer(1,0.3*cm))

    # ── 7. Regla proporcional ──────────────────────────────────────────────
    story.append(Paragraph(
        f"8. REGLA PROPORCIONAL — Art. 553 CCom  (ejemplo daño {int(c.danio_ejemplo_pct*100)}%)", sH))
    story.append(mktab([
        ["Concepto","Monto (UF)"],
        [f"Daño ejemplo ({int(c.danio_ejemplo_pct*100)}%)", f"UF {fmt(res['danio'])}"],
        ["Ratio de cobertura", f"{fmtd(res['ratio']*100,1)}%"],
        ["Indemnización real (Art. 553)", f"UF {fmt(res['indemn'])}"],
        ["Pérdida que absorbe el asegurado",
         f"UF {fmt(res['perdida'])}" if res["infraseguro"] else "—"],
    ], [11*cm,6*cm], extra=[
        *([("TEXTCOLOR",(1,3),(1,3),RJ),("FONTNAME",(1,3),(1,3),"Helvetica-Bold"),
           ("TEXTCOLOR",(1,4),(1,4),RJ),("FONTNAME",(1,4),(1,4),"Helvetica-Bold")]
          if res["infraseguro"] else [])
    ]))
    story.append(Spacer(1,0.4*cm))

    if res["infraseguro"]:
        al = Table([[Paragraph(
            f"⚠  INFRASEGURO: UF {fmt(c.monto_asegurado)} = {fmtd(res['ratio']*100,1)}% "
            f"del VR UF {fmt(res['vr'])}. Brecha: UF {fmt(res['brecha'])}. "
            "Actualizar póliza urgentemente.",
            S("AX",fontSize=8.5,fontName="Helvetica-Bold",textColor=RJ,leading=13))
        ]], colWidths=[W])
        al.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),RJB), ("BOX",(0,0),(-1,-1),1.2,RJ),
            ("LEFTPADDING",(0,0),(-1,-1),10),  ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),8),    ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(al)

    # Línea naranja + azul de cierre marca A PLUS
    story += [
        Spacer(1,0.4*cm),
        HRFlowable(width="100%", thickness=2, color=NR),
        HRFlowable(width="100%", thickness=0.5, color=AZ),
        Spacer(1,0.2*cm),
        Paragraph(
            f"A PLUS Ajustadores · aplusajustadores.cl · "
            f"Generado {c.fecha_analisis} · Valores en UF · "
            "Costos indirectos: parámetros de industria — revisar con presupuesto real."
            + (f" · Analista: {c.analista}" if c.analista else ""), sF),
    ]
    doc.build(story)
    print(f"  PDF generado: {path}")
