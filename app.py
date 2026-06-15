import streamlit as st
import pandas as pd
import anthropic
from datetime import date
import re

st.set_page_config(page_title="Reporte Financiero IA", page_icon="📊")
st.title("📊 Reporte Financiero con IA")
st.write("Sube tu Excel y recibe un análisis ejecutivo en segundos.")

API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# ── PLANTILLAS CSS ──────────────────────────────────────────────────────────────

CSS_PLANTILLAS = {

    "Dashboard": """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#f0f4f8;color:#1a202c;padding:24px}
.header{background:linear-gradient(135deg,#1e40af,#3b82f6);color:white;padding:24px 32px;border-radius:16px;margin-bottom:24px;box-shadow:0 4px 20px rgba(59,130,246,0.3)}
.header h1{font-size:24px;font-weight:700}
.header .meta{font-size:13px;opacity:0.85;margin-top:6px}
.seccion{background:white;border-radius:16px;padding:24px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}
.seccion h2{font-size:14px;font-weight:700;color:#1e40af;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #eff6ff;text-transform:uppercase;letter-spacing:0.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}
.kpi{background:linear-gradient(135deg,#f8faff,#eff6ff);border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,0.05)}
.kpi .label{font-size:11px;text-transform:uppercase;color:#64748b;margin-bottom:10px;letter-spacing:0.5px;font-weight:600}
.kpi .valor{font-size:28px;font-weight:800}
.kpi .detalle{font-size:12px;color:#94a3b8;margin-top:6px}
.positivo .valor{color:#16a34a}
.alerta .valor{color:#d97706}
.critico .valor{color:#dc2626}
.neutro .valor{color:#1e40af}
.lista{list-style:none}
.lista li{padding:12px 0;border-bottom:1px solid #f1f5f9;font-size:14px}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700}
.badge-rojo{background:#fef2f2;color:#dc2626}
.badge-amarillo{background:#fffbeb;color:#d97706}
.badge-verde{background:#f0fdf4;color:#16a34a}
.grafico-container{background:white;border-radius:16px;padding:24px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}
.grafico-container h3{font-size:13px;font-weight:700;color:#1e40af;margin-bottom:20px;text-transform:uppercase;letter-spacing:0.5px}
.grafico-wrapper{position:relative;height:280px}
</style>""",

    "Profesional": """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b;padding:24px}
.header{background:#1e3a5f;color:white;padding:24px 32px;border-radius:12px;margin-bottom:24px}
.header h1{font-size:22px;font-weight:600}
.header .meta{font-size:13px;opacity:0.8;margin-top:6px}
.seccion{background:white;border-radius:12px;padding:24px;margin-bottom:16px;border:1px solid #e2e8f0}
.seccion h2{font-size:16px;font-weight:600;color:#1e3a5f;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #e2e8f0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.kpi{background:#f8fafc;border-radius:8px;padding:16px;border-left:4px solid #e2e8f0}
.kpi .label{font-size:11px;text-transform:uppercase;color:#64748b;margin-bottom:8px}
.kpi .valor{font-size:24px;font-weight:700}
.kpi .detalle{font-size:12px;color:#64748b;margin-top:4px}
.positivo{border-left-color:#16a34a}.positivo .valor{color:#16a34a}
.alerta{border-left-color:#ca8a04}.alerta .valor{color:#ca8a04}
.critico{border-left-color:#dc2626}.critico .valor{color:#dc2626}
.neutro .valor{color:#1e3a5f}
.lista{list-style:none}
.lista li{padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:14px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge-rojo{background:#fef2f2;color:#dc2626}
.badge-amarillo{background:#fefce8;color:#ca8a04}
.badge-verde{background:#f0fdf4;color:#16a34a}
.grafico-container{background:#f8fafc;border-radius:8px;padding:20px;margin-bottom:16px;border:1px solid #e2e8f0}
.grafico-container h3{font-size:14px;font-weight:600;color:#1e3a5f;margin-bottom:16px}
.grafico-wrapper{position:relative;height:280px}
</style>""",

    "Ejecutivo oscuro": """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;padding:24px}
.header{background:linear-gradient(135deg,#1e293b,#0f172a);color:white;padding:24px 32px;border-radius:12px;margin-bottom:24px;border:1px solid #334155}
.header h1{font-size:22px;font-weight:600;color:#f1f5f9}
.header .meta{font-size:13px;color:#94a3b8;margin-top:6px}
.seccion{background:#1e293b;border-radius:12px;padding:24px;margin-bottom:16px;border:1px solid #334155}
.seccion h2{font-size:16px;font-weight:600;color:#93c5fd;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #334155}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.kpi{background:#0f172a;border-radius:8px;padding:16px;border-left:4px solid #334155}
.kpi .label{font-size:11px;text-transform:uppercase;color:#64748b;margin-bottom:8px}
.kpi .valor{font-size:24px;font-weight:700;color:#f1f5f9}
.kpi .detalle{font-size:12px;color:#64748b;margin-top:4px}
.positivo{border-left-color:#22c55e}.positivo .valor{color:#22c55e}
.alerta{border-left-color:#f59e0b}.alerta .valor{color:#f59e0b}
.critico{border-left-color:#ef4444}.critico .valor{color:#ef4444}
.neutro .valor{color:#93c5fd}
.lista{list-style:none}
.lista li{padding:10px 0;border-bottom:1px solid #1e293b;font-size:14px;color:#cbd5e1}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge-rojo{background:#450a0a;color:#ef4444}
.badge-amarillo{background:#451a03;color:#f59e0b}
.badge-verde{background:#052e16;color:#22c55e}
.grafico-container{background:#0f172a;border-radius:12px;padding:20px;margin-bottom:16px;border:1px solid #334155}
.grafico-container h3{font-size:14px;font-weight:600;color:#93c5fd;margin-bottom:16px}
.grafico-wrapper{position:relative;height:280px}
</style>""",

    "Minimalista": """<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Georgia',serif;background:#ffffff;color:#111827;padding:32px}
.header{background:#ffffff;color:#111827;padding:24px 0;margin-bottom:32px;border-bottom:2px solid #111827}
.header h1{font-size:24px;font-weight:400;letter-spacing:-0.5px}
.header .meta{font-size:12px;color:#6b7280;margin-top:8px;letter-spacing:1px;text-transform:uppercase}
.seccion{background:#ffffff;padding:24px 0;margin-bottom:24px;border-bottom:1px solid #e5e7eb}
.seccion h2{font-size:13px;font-weight:600;color:#6b7280;margin-bottom:16px;text-transform:uppercase;letter-spacing:1.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.kpi{background:#f9fafb;padding:16px;border-left:3px solid #e5e7eb}
.kpi .label{font-size:11px;text-transform:uppercase;color:#9ca3af;margin-bottom:8px;letter-spacing:1px}
.kpi .valor{font-size:26px;font-weight:300;color:#111827}
.kpi .detalle{font-size:12px;color:#9ca3af;margin-top:4px}
.positivo{border-left-color:#111827}.positivo .valor{color:#111827}
.alerta{border-left-color:#d97706}.alerta .valor{color:#d97706}
.critico{border-left-color:#dc2626}.critico .valor{color:#dc2626}
.neutro .valor{color:#111827}
.lista{list-style:none}
.lista li{padding:10px 0;border-bottom:1px solid #f3f4f6;font-size:14px;color:#374151}
.badge{display:inline-block;padding:2px 10px;border-radius:2px;font-size:11px;font-weight:400}
.badge-rojo{background:#fef2f2;color:#dc2626}
.badge-amarillo{background:#fffbeb;color:#d97706}
.badge-verde{background:#f0fdf4;color:#16a34a}
.grafico-container{background:#f9fafb;padding:20px;margin-bottom:24px}
.grafico-container h3{font-size:12px;font-weight:600;color:#6b7280;margin-bottom:16px;text-transform:uppercase;letter-spacing:1px}
.grafico-wrapper{position:relative;height:260px}
</style>"""
}

# ── SCRIPTS Y BOTÓN PDF ─────────────────────────────────────────────────────────

SCRIPTS_PDF = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
"""

BOTON_PDF = """
<div id="zona-pdf" style="text-align:center;margin:32px 0 8px 0">
  <button id="btn-pdf" onclick="descargarPDF()"
    style="background:#1e40af;color:white;border:none;padding:12px 36px;
           border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;
           font-family:'Segoe UI',sans-serif;box-shadow:0 2px 8px rgba(30,64,175,0.3)">
    ⬇ Descargar PDF
  </button>
</div>
<script>
async function descargarPDF() {
  const btn = document.getElementById('btn-pdf');
  const zona = document.getElementById('zona-pdf');
  btn.textContent = 'Generando PDF...';
  btn.disabled = true;
  zona.style.display = 'none';
  try {
    const { jsPDF } = window.jspdf;
    const canvas = await html2canvas(document.body, {scale: 2, useCORS: true, logging: false});
    const imgData = canvas.toDataURL('image/png');
    const pdfWidth = 210;
    const imgHeight = (canvas.height * pdfWidth) / canvas.width;
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: [pdfWidth, imgHeight]
    });
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, imgHeight);
    pdf.save('reporte_financiero.pdf');
  } finally {
    zona.style.display = '';
    btn.textContent = '⬇ Descargar PDF';
    btn.disabled = false;
  }
}
</script>
"""

# ── UI ──────────────────────────────────────────────────────────────────────────

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if archivo is not None:
    st.markdown("---")
    st.subheader("Configura tu reporte")

    nombre_empresa = st.text_input(
        "Nombre de la empresa (opcional)",
        placeholder="Ej: Distribuciones Martínez S.L."
    )

    tipo_reporte = st.selectbox(
        "¿Qué tipo de análisis necesitas?",
        ["Reporte completo", "Solo liquidez", "Comparativa de períodos", "Otro"]
    )

    audiencia = st.selectbox(
        "¿Para quién es el reporte?",
        ["Para dirección", "Para un cliente", "Para el banco", "Uso propio"]
    )

    plantilla = st.selectbox(
        "Estilo visual",
        ["Dashboard", "Profesional", "Ejecutivo oscuro", "Minimalista"]
    )

    incluir_graficos = st.checkbox("Incluir gráficos", value=True)

    contexto = st.text_area(
        "Contexto adicional (opcional)",
        placeholder="Ej: Marzo fue atípico por vacaciones, incluye una partida extraordinaria..."
    )

    if st.button("Generar reporte"):
        df = pd.read_excel(archivo)
        contenido = df.to_string()

        instruccion_tipo = {
            "Reporte completo": "Genera un análisis completo con los 4 bloques adaptados al tipo de datos.",
            "Solo liquidez": "Centra el análisis exclusivamente en la salud de liquidez y flujo de caja.",
            "Comparativa de períodos": "Identifica y compara los períodos disponibles en los datos.",
            "Otro": "Adapta el análisis al tipo de datos disponibles."
        }

        instruccion_audiencia = {
            "Para dirección": "Usa lenguaje ejecutivo, conciso y orientado a decisiones.",
            "Para un cliente": "Usa un tono profesional y explicativo.",
            "Para el banco": "Resalta la solidez financiera y los indicadores clave.",
            "Uso propio": "Puedes ser más técnico y detallado."
        }

        empresa_header = nombre_empresa if nombre_empresa else "Análisis Financiero"
        fecha_hoy = date.today().strftime("%d/%m/%Y")

        bloque_graficos = ""
        if incluir_graficos:
            bloque_graficos = """
GRÁFICOS CON CHART.JS:
- Añade <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> en el <head>
- Incluye entre 1 y 3 gráficos según los datos disponibles:
  * Datos temporales (meses, trimestres) → líneas o barras
  * Categorías comparables → barras verticales u horizontales
  * Distribución porcentual → dona
- Cada gráfico en un div.grafico-container con h3 descriptivo y div.grafico-wrapper con canvas dentro
- IDs únicos para cada canvas: grafico1, grafico2, grafico3
- JavaScript al final del <body>
- Colores: ['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316']
- SOLO datos reales del Excel. Sin inventar valores.
- Configuración: responsive:true, maintainAspectRatio:false
"""

        progreso = st.empty()
        progreso.info("⏳ Generando tu reporte... por favor espera.")

        prompt = f"""Eres un analista experto en datos financieros y operativos. Genera un reporte ejecutivo en HTML.

CLASES HTML OBLIGATORIAS — sin estilos inline ni bloques <style>:
- .header con h1 (nombre empresa) y .meta (fecha · tipo)
- .seccion con h2 como título de cada bloque
- .grid → contenedor de KPIs
- .kpi con .label, .valor, .detalle + clase de estado: .positivo / .alerta / .critico / .neutro
- .lista + li → listas de puntos
- .badge .badge-verde / .badge-amarillo / .badge-rojo → etiquetas

NO incluyas ningún bloque <style>. El diseño se aplica externamente.
{bloque_graficos}
CONFIGURACIÓN:
- Empresa: {empresa_header}
- Fecha: {fecha_hoy}
- Tipo: {instruccion_tipo[tipo_reporte]}
- Audiencia: {instruccion_audiencia[audiencia]}

REGLAS ABSOLUTAS:
1. NUNCA inventes cifras ni conceptos que no estén en los datos.
2. Si un dato no está disponible, omítelo.
3. El header debe mostrar "{empresa_header}" en h1 y "{fecha_hoy} · {tipo_reporte}" en .meta.

ANÁLISIS ADAPTATIVO:
- Estados financieros / flujos de caja → Bloque 1: Salud de liquidez | Bloque 2: Variaciones clave | Bloque 3: Alertas y red flags | Bloque 4: Recomendaciones
- Gastos / costes → Bloque 1: Resumen y KPIs | Bloque 2: Distribución por categoría | Bloque 3: Alertas y desviaciones | Bloque 4: Recomendaciones de optimización
- Ventas / ingresos → Bloque 1: Rendimiento general | Bloque 2: Análisis por producto o período | Bloque 3: Alertas y tendencias | Bloque 4: Recomendaciones
- Otro tipo → adapta los 4 bloques al contexto real

Contexto adicional: {contexto if contexto else 'Ninguno'}

Datos:
{contenido}

Devuelve SOLO el HTML completo empezando por <!DOCTYPE html>. Sin explicaciones."""

        cliente = anthropic.Anthropic(api_key=API_KEY)
        html_chunks = []

        with cliente.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for i, text in enumerate(stream.text_stream):
                html_chunks.append(text)
                if i % 50 == 0:
                    progreso.info(f"⏳ Generando tu reporte... {len(''.join(html_chunks))} caracteres procesados")

        progreso.empty()
        html = "".join(html_chunks)
        html = html.replace("```html", "").replace("```", "").strip()

        # Quitar cualquier <style> que la IA haya incluido
        html = re.sub(r'<style>.*?</style>', '', html, flags=re.DOTALL)

        # Inyectar CSS de la plantilla + scripts PDF en el <head>
        css = CSS_PLANTILLAS[plantilla]
        if "<head>" in html:
            html = html.replace("<head>", f"<head>\n{css}\n{SCRIPTS_PDF}", 1)
        else:
            html = html.replace("<!DOCTYPE html>", f"<!DOCTYPE html>\n<head>{css}{SCRIPTS_PDF}</head>", 1)

        # Inyectar botón PDF antes del cierre del body
        if "</body>" in html:
            html = html.replace("</body>", f"{BOTON_PDF}\n</body>", 1)
        else:
            html += BOTON_PDF

        st.success("✅ Reporte generado correctamente.")
        alto = 3500 if incluir_graficos else 2200
        st.components.v1.html(html, height=alto, scrolling=True)
        st.download_button(
            label="⬇️ Descargar HTML",
            data=html,
            file_name="reporte_financiero.html",
            mime="text/html"
        )

# ── FEEDBACK ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("💬 **¿Tienes un minuto?** Tu opinión nos ayuda a mejorar la herramienta.")
st.link_button(
    "Dejar feedback",
    "https://docs.google.com/forms/d/e/1FAIpQLScrFclbrMlLUoDwFlAKxXEQhFpEXHxrVMIbXFOqDsIDree8tw/viewform?usp=header"
)
