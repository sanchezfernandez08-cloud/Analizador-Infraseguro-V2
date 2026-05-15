# =========================================
# MOTOR GENÉRICO DE VALOR DE RECONSTRUCCIÓN
# SEGUROS – CHILE v2
# Conforme DFL 251, DS 1055 y CCom art. 553
# Ley 19.537 Copropiedad Inmobiliaria
# =========================================

from dataclasses import dataclass, field
from typing import Optional
from datetime import date

VUB = {
    ("Casa",      "Albañilería","Básico"): 18,
    ("Casa",      "Albañilería","Medio"):  22,
    ("Casa",      "Albañilería","Alto"):   28,
    ("Casa",      "Metalcon",  "Básico"): 17,
    ("Casa",      "Metalcon",  "Medio"):  21,
    ("Depto",     "Hormigón",  "Medio"):  26,
    ("Depto",     "Hormigón",  "Alto"):   32,
    ("Edificio",  "Hormigón",  "Medio"):  28,
    ("Edificio",  "Hormigón",  "Alto"):   35,
    ("Comunidad", "Hormigón",  "Medio"):  27,
    ("Comunidad", "Hormigón",  "Alto"):   34,
}

FACTOR_GEOGRAFICO = {
    "Metropolitana": 1.05,
    "Intermedia":    1.00,
    "Aislada":       1.15,
}

IVA = 0.19

# ─── FUNDAMENTOS DOCUMENTADOS ────────────────────────────────────────────────
FUNDAMENTOS_CI = {
    "gastos_generales": {
        "pct_default": 0.03,
        "rango_min":   0.02,
        "rango_max":   0.08,
        "label":       "Gastos generales del contratista",
        "fuente":      "Práctica de mercado chilena (CChC) y doctrina del contrato de construcción (Revista de Derecho UCV, Scielo Chile 2020). En obras privadas oscilan entre 2% y 8% del costo directo según magnitud. El 3% representa la fracción de administración central atribuible a una obra específica de reconstrucción. No existe decreto chileno que fije este porcentaje para seguros; es un parámetro de industria.",
        "componentes": [
            "Personal técnico y administrativo no asignado directamente a obra",
            "Gastos de oficina central (arriendo, equipos, comunicaciones)",
            "Seguros corporativos y fianzas de cumplimiento",
            "Gastos de licitación y contratación del contratista",
            "Aportes gremiales y gastos legales generales de la empresa",
        ],
    },
    "utilidad": {
        "pct_default": 0.06,
        "rango_min":   0.04,
        "rango_max":   0.10,
        "label":       "Utilidad del contratista",
        "fuente":      "Estándar de industria chilena e internacional: 5%-8% sobre costo directo (Scielo Chile, 'La variabilidad del precio en el contrato de construcción', 2020). El 6% es el Beneficio Industrial (BI) de referencia más utilizado, coincidente con el estándar del RD 1098/2001 art.131 (España) adoptado como referencia técnica en valoraciones de seguros. No existe norma chilena que lo fije; es práctica de mercado.",
        "componentes": [
            "Remuneración por riesgo empresarial asumido por el contratista",
            "Retorno sobre capital invertido en materiales y mano de obra",
            "Margen por gestión, coordinación y dirección del proceso constructivo",
        ],
    },
    "imprevistos": {
        "pct_default": 0.12,
        "rango_min":   0.05,
        "rango_max":   0.15,
        "label":       "Imprevistos y contingencias",
        "fuente":      "La Cámara Chilena de la Construcción (CChC) y expertos recomiendan entre 5% y 10% para obras nuevas (conprojecto.cl, 2024). En RECONSTRUCCIÓN POST-SINIESTRO se justifica un rango superior (10%-15%) por: demolición previa, daños ocultos, urgencia de contratación, escasez de mano de obra especializada y volatilidad de precios. El 12% es un valor intermedio-alto documentado para contexto de seguros.",
        "componentes": [
            "Demolición y retiro de escombros y elementos dañados",
            "Daños estructurales ocultos revelados durante la ejecución",
            "Sobrecosto por urgencia y plazo acotado de reconstrucción",
            "Fluctuaciones de precios de materiales (acero, hormigón, madera)",
            "Instalación de faenas temporales en sitio dañado o inhabitable",
            "Contingencias climáticas y de acceso durante la obra",
        ],
    },
    "diseno_proyecto": {
        "pct_default": 0.10,
        "rango_min":   0.07,
        "rango_max":   0.15,
        "label":       "Diseño, ingeniería y proyecto",
        "fuente":      "Colegio de Arquitectos de Chile A.G. — Valores Referenciales de Honorarios: etapa de proyecto entre 5,5% y 8% del valor de obra. Sumando todas las especialidades requeridas (arquitectura 5%-8%, ingeniería estructural/sísmica 2%-3%, instalaciones eléctrica-sanitaria-gas 1%-2%, ITO 1%-2%, permisos DOM 0,5%-1%), el total razonable es 8%-15%. El 10% es un valor intermedio conservador.",
        "componentes": [
            "Honorarios arquitecto: anteproyecto, proyecto y permiso DOM",
            "Ingeniería estructural y cálculo sísmico (NCh433, DS61, DS60)",
            "Proyecto instalaciones: eléctrica (SEC), sanitaria, gas (SEC)",
            "Inspección Técnica de Obra (ITO) durante ejecución",
            "Tramitación permisos municipales y recepción definitiva (DOM)",
            "Memoria de cálculo, especificaciones técnicas y planos As-Built",
        ],
    },
}


@dataclass
class CasoSeguro:
    nombre:          str
    direccion:       str
    rut_asegurado:   str  = ""
    poliza:          str  = ""
    corredor:        str  = ""
    fecha_analisis:  str  = field(default_factory=lambda: date.today().strftime("%d-%m-%Y"))

    tipo_inmueble:     str   = "Comunidad"
    sistema:           str   = "Hormigón"
    nivel:             str   = "Medio"
    superficie_m2:     float = 0
    zona:              str   = "Metropolitana"
    numero_pisos:      int   = 1
    anio_construccion: int   = 2000
    aplica_iva:        bool  = True

    monto_asegurado:   float = 0
    danio_ejemplo_pct: float = 0.50

    # Costos indirectos configurables (None = usar default documentado)
    pct_gastos_generales: Optional[float] = None
    pct_utilidad:         Optional[float] = None
    pct_imprevistos:      Optional[float] = None
    pct_diseno_proyecto:  Optional[float] = None

    # Justificaciones personalizadas (vacío = usar fuente estándar)
    justificacion_gastos_generales: str = ""
    justificacion_utilidad:         str = ""
    justificacion_imprevistos:      str = ""
    justificacion_diseno_proyecto:  str = ""

    nota_superficie: str = ""
    analista:        str = ""


def factor_normativo(anio: int) -> float:
    if anio < 1985:  return 1.15
    if anio <= 2000: return 1.10
    if anio <= 2010: return 1.05
    return 1.00

def factor_altura(pisos: int) -> float:
    if pisos <= 2:  return 1.00
    if pisos <= 5:  return 1.05
    if pisos <= 10: return 1.10
    return 1.15

def _pct(c: CasoSeguro, key: str) -> float:
    val = getattr(c, f"pct_{key}", None)
    return val if val is not None else FUNDAMENTOS_CI[key]["pct_default"]


def calcular(c: CasoSeguro) -> dict:
    key = (c.tipo_inmueble, c.sistema, c.nivel)
    if key not in VUB:
        raise ValueError(f"Combinación no disponible: {key}")

    vub = VUB[key]
    fg  = FACTOR_GEOGRAFICO[c.zona]
    fn  = factor_normativo(c.anio_construccion)
    fa  = factor_altura(c.numero_pisos)

    costo_directo = c.superficie_m2 * vub * fg * fn * fa

    pcts = {k: _pct(c, k) for k in FUNDAMENTOS_CI}
    ci_detalle = {k: costo_directo * v for k, v in pcts.items()}
    costos_indirectos = sum(ci_detalle.values())
    pct_total_ci = sum(pcts.values())

    subtotal  = costo_directo + costos_indirectos
    iva_monto = subtotal * IVA if c.aplica_iva else 0
    vr        = subtotal + iva_monto

    ratio       = c.monto_asegurado / vr if vr > 0 else 0
    infraseguro = ratio < 1.0
    brecha      = max(0, vr - c.monto_asegurado)
    danio       = vr * c.danio_ejemplo_pct
    indemn      = danio * ratio if infraseguro else danio
    perdida     = max(0, danio - indemn)
    proteccion_activa = c.monto_asegurado * 1.10 >= vr

    just = {}
    for k in FUNDAMENTOS_CI:
        custom = getattr(c, f"justificacion_{k}", "")
        just[k] = custom if custom else FUNDAMENTOS_CI[k]["fuente"]

    return {
        "caso": c, "vub": vub, "fg": fg, "fn": fn, "fa": fa,
        "costo_directo": costo_directo,
        "pcts": pcts, "pct_total_ci": pct_total_ci,
        "ci_detalle": ci_detalle,
        "costos_indirectos": costos_indirectos,
        "subtotal": subtotal, "iva_monto": iva_monto, "vr": vr,
        "ratio": ratio, "infraseguro": infraseguro,
        "brecha": brecha, "danio": danio, "indemn": indemn,
        "perdida": perdida, "proteccion_activa": proteccion_activa,
        "justificaciones": just, "fundamentos": FUNDAMENTOS_CI,
    }


# ─── DESGLOSE EXPLICATIVO DEL VUB ────────────────────────────────────────────
# El VUB (Valor Unitario Base) es un valor paramétrico que representa el costo
# de reconstruir 1 m² de una edificación en condiciones normales de mercado,
# SIN considerar aún los factores de ajuste (Fg, Fn, Fa) ni costos indirectos.
#
# ORIGEN: No existe en Chile un decreto único que fije el VUB para seguros.
# Se construye a partir de tres referencias convergentes:
#   1. Tablas de costos unitarios MINVU (Res. Ex. anual, arts. 126°-127° LGUC)
#   2. Tablas referenciales SERVIU (DS 49, DS 27) que incluyen GG y utilidades
#   3. Práctica de la industria aseguradora chilena y peritos de seguros
#
# COMPOSICIÓN INTERNA del VUB (distribución típica del costo directo por m²):

DESGLOSE_VUB = {
    # Cada entrada: descripción, % aproximado del VUB, qué incluye, fuente
    "obra_gruesa": {
        "label":      "Obra gruesa y estructura",
        "pct":        0.40,
        "descripcion": (
            "Es la parte más costosa de cualquier construcción. Incluye todo lo que "
            "da soporte y firmeza al edificio: excavaciones y fundaciones (cimientos "
            "de hormigón armado que transfieren el peso al suelo), pilares y vigas "
            "estructurales, losas de entrepiso y techumbre, muros de hormigón o "
            "albañilería confinada, y escaleras. En edificios de hormigón armado, "
            "esta partida concentra el mayor gasto en materiales (cemento, fierro, "
            "áridos) y mano de obra especializada (enfierradores, moldajistas)."
        ),
        "fuente": "Referencia: proporción estándar APU industria chilena (CChC/CDT). "
                  "Obra gruesa representa 40%-50% del costo directo en edificación media.",
    },
    "terminaciones": {
        "label":      "Terminaciones interiores y exteriores",
        "pct":        0.25,
        "descripcion": (
            "Todo lo que se ve y se usa dentro del inmueble: revestimientos de pisos "
            "(cerámica, porcelanato, madera), muros (pintura, estuco, papel mural), "
            "cielos (planchas de yeso, pintados), puertas y ventanas (marcos, hojas, "
            "herrajes, vidrios), muebles fijos de cocina y baños, y fachadas exteriores "
            "(revestimientos, pinturas impermeabilizantes). El nivel 'Básico', 'Medio' "
            "o 'Alto' del VUB refleja principalmente la calidad de esta partida: "
            "porcelanato importado vs. cerámica estándar, por ejemplo, puede duplicar "
            "el costo de las terminaciones."
        ),
        "fuente": "Referencia: terminaciones representan 20%-30% del costo directo "
                  "según nivel (Constructora Márquez Arranz, 2025; winteri.com, 2024).",
    },
    "instalaciones": {
        "label":      "Instalaciones y especialidades",
        "pct":        0.25,
        "descripcion": (
            "Todo el sistema 'invisible' que hace habitable el edificio. Se divide en: "
            "instalación eléctrica (tablero, circuitos, enchufes, luminarias, SEC), "
            "instalación sanitaria (agua potable, alcantarillado, cámaras), instalación "
            "de gas (cañerías, medidores, SEC), sistema de calefacción y climatización, "
            "ascensores y montacargas (en edificios de varios pisos), sistema contra "
            "incendio (rociadores, detectores, red húmeda según DS 594/NCh 1929), "
            "y telecomunicaciones básicas. En condominios, las instalaciones comunes "
            "(bombas, tableros generales, sistema de extracción) tienen un peso "
            "significativo en esta partida."
        ),
        "fuente": "Referencia: instalaciones representan 20%-30% del costo directo "
                  "(SmartHomes/CChC, 2025; CYPE Generador de Precios Chile, 2024).",
    },
    "equipos_medios": {
        "label":      "Equipos, maquinaria y medios auxiliares",
        "pct":        0.10,
        "descripcion": (
            "Arriendo y operación de maquinaria necesaria para ejecutar la obra: "
            "grúa torre o pluma (imprescindible en edificios de más de 4 pisos), "
            "betonera o bomba de hormigón, andamiaje y apuntalamientos, retroexcavadora "
            "para fundaciones, montacargas de obra, herramientas menores y su desgaste. "
            "También incluye la instalación de faenas: oficinas de obra, bodegas, "
            "baños provisorios y el cuidado nocturno del sitio. En edificios en altura "
            "(factor Fa > 1.00) esta partida aumenta proporcionalmente al número de "
            "pisos, lo que justifica el factor de altura aplicado al VUB."
        ),
        "fuente": "Referencia: equipos y medios auxiliares representan 8%-12% del "
                  "costo directo (chilecubica.com APU; MINVU tablas referenciales DS27).",
    },
}

# Mapa completo de VUB con descripción del nivel de terminaciones
DESCRIPCION_NIVEL = {
    "Básico": (
        "Terminaciones de estándar mínimo normativo: pisos de cerámica económica o "
        "radier afinado, pintura látex, ventanas de aluminio simple, puertas MDF "
        "económicas, baños con artefactos básicos. Corresponde al estándar de "
        "vivienda social o construcción funcional sin acabados premium."
    ),
    "Medio": (
        "Terminaciones de estándar habitacional corriente: pisos de porcelanato o "
        "madera laminada, pintura lavable, ventanas termopanel, puertas de madera "
        "sólida, baños con artefactos de primera marca económica, cocina con muebles "
        "melamínicos. Es el estándar más frecuente en el mercado residencial chileno."
    ),
    "Alto": (
        "Terminaciones de estándar superior: pisos de porcelanato importado, piedra "
        "natural o madera noble, pintura de alta cubrición, ventanas termopanel de "
        "aluminio anodizado o PVC, puertas de madera maciza, baños con artefactos "
        "de diseño, cocina equipada con muebles de melamina de alto espesor o "
        "madera. Corresponde a proyectos de rango medio-alto y alto."
    ),
}

DESCRIPCION_SISTEMA = {
    "Albañilería": (
        "Muros de ladrillo o bloque confinados entre pilares y vigas de hormigón "
        "armado. Es el sistema más usado en casas y edificios de baja altura en Chile. "
        "Buen comportamiento sísmico si está correctamente confinado (NCh433). "
        "Costo más accesible que el hormigón, pero limita las plantas libres."
    ),
    "Metalcon": (
        "Estructura liviana de perfiles de acero galvanizado (Steel Framing). "
        "Rápida de ejecutar, con buen desempeño sísmico y térmico si tiene aislación "
        "adecuada. Muy usada en casas DS49 y proyectos de construcción modular. "
        "Costo intermedio; requiere revestimientos exteriores adicionales."
    ),
    "Hormigón": (
        "Estructura de hormigón armado con pilares, vigas y losas de H° A°. "
        "Es el sistema obligatorio en edificios sobre 4-5 pisos en Chile. "
        "Mayor resistencia sísmica, mayor flexibilidad de diseño en planta, "
        "pero también el más costoso en materiales y mano de obra especializada "
        "(enfierradores, moldajistas, bombeo de hormigón)."
    ),
}


def explicar_vub(caso: "CasoSeguro", res: dict) -> dict:
    """
    Genera el desglose explicativo completo del VUB para el informe.
    Retorna un dict con todos los textos, valores y porcentajes necesarios.
    """
    vub   = res["vub"]
    nivel = caso.nivel
    sist  = caso.sistema
    tipo  = caso.tipo_inmueble

    # Costo estimado por componente (sobre el VUB total)
    componentes = []
    for key, d in DESGLOSE_VUB.items():
        uf_comp = round(vub * d["pct"], 2)
        componentes.append({
            "key":         key,
            "label":       d["label"],
            "pct":         d["pct"],
            "uf_m2":       uf_comp,
            "descripcion": d["descripcion"],
            "fuente":      d["fuente"],
        })

    return {
        "vub":           vub,
        "tipo":          tipo,
        "sistema":       sist,
        "nivel":         nivel,
        "desc_nivel":    DESCRIPCION_NIVEL.get(nivel, ""),
        "desc_sistema":  DESCRIPCION_SISTEMA.get(sist, ""),
        "componentes":   componentes,
        "nota_general": (
            f"El VUB de {vub} UF/m² es un valor paramétrico de referencia para la "
            f"industria aseguradora chilena. No proviene de un presupuesto real de "
            f"obra, sino de la convergencia entre las tablas de costos unitarios MINVU "
            f"(arts. 126°-127° LGUC), las tablas referenciales SERVIU (DS 49/DS 27) "
            f"y la práctica de peritos y liquidadores de seguros. "
            f"Para mayor precisión, puede reemplazarse por un presupuesto de "
            f"contratista o una tasación de perito calificado."
        ),
    }
