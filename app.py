import streamlit as st
import pandas as pd
import anthropic
from datetime import date

st.set_page_config(page_title="Reporte Financiero IA", page_icon="📊")
st.title("📊 Reporte Financiero con IA")
st.write("Sube tu Excel y recibe un análisis ejecutivo en segundos.")

API_KEY = st.secrets["ANTHROPIC_API_KEY"]

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

    contexto = st.text_area(
        "Contexto adicional (opcional)",
        placeholder="Ej: Marzo fue atípico por vacaciones, incluye una partida extraordinaria..."
    )

    if st.button("Generar reporte"):
        df = pd.read_excel(archivo)
        contenido = df.to_string()

        instruccion_tipo = {
            "Reporte completo": "Genera un análisis completo con los 4 bloques adaptados al tipo de datos.",
            "Solo liquidez": "Centra el análisis exclusivamente en la salud de liquidez y flujo de caja. Ignora otros aspectos.",
            "Comparativa de períodos": "El usuario necesita comparar períodos. Identifica y compara los períodos disponibles en los datos.",
            "Otro": "Adapta el análisis al tipo de datos disponibles."
        }

        instruccion_audiencia = {
            "Para dirección": "El informe es para la dirección de la empresa. Usa lenguaje ejecutivo, conciso y orientado a decisiones.",
            "Para un cliente": "El informe es para presentar a un cliente externo. Usa un tono profesional y explicativo.",
            "Para el banco": "El informe es para presentar a una entidad bancaria. Resalta la solidez financiera y los indicadores clave.",
            "Uso propio": "El informe es para uso interno. Puedes ser más técnico y detallado."
        }

        empresa_header = nombre_empresa if nombre_empresa else "Análisis Financiero"
        fecha_hoy = date.today().strftime("%d/%m/%Y")

        progreso = st.empty()
        progreso.info("⏳ Generando tu reporte... por favor espera.")

        prompt = f"""Eres un analista experto en datos financieros y operativos. Genera un reporte ejecutivo en HTML usando EXACTAMENTE este CSS. No cambies nada del estilo.

CSS FIJO OBLIGATORIO:
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b;padding:24px}}
.header{{background:#1e3a5f;color:white;padding:24px 32px;border-radius:12px;margin-bottom:24px}}
.header h1{{font-size:22px;font-weight:600}}
.header .meta{{font-size:13px;opacity:0.8;margin-top:6px}}
.seccion{{background:white;border-radius:12px;padding:24px;margin-bottom:16px;border:1px solid #e2e8f0}}
.seccion h2{{font-size:16px;font-weight:600;color:#1e3a5f;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #e2e8f0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}
.kpi{{background:#f8fafc;border-radius:8px;padding:16px;border-left:4px solid #e2e8f0}}
.kpi .label{{font-size:11px;text-transform:uppercase;color:#64748b;margin-bottom:8px}}
.kpi .valor{{font-size:24px;font-weight:700}}
.kpi .detalle{{font-size:12px;color:#64748b;margin-top:4px}}
.positivo{{border-left-color:#16a34a}}.positivo .valor{{color:#16a34a}}
.alerta{{border-left-color:#ca8a04}}.alerta .valor{{color:#ca8a04}}
.critico{{border-left-color:#dc2626}}.critico .valor{{color:#dc2626}}
.neutro .valor{{color:#1e3a5f}}
.lista{{list-style:none}}
.lista li{{padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:14px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}}
.badge-rojo{{background:#fef2f2;color:#dc2626}}
.badge-amarillo{{background:#fefce8;color:#ca8a04}}
.badge-verde{{background:#f0fdf4;color:#16a34a}}
</style>

CONFIGURACIÓN DEL REPORTE:
- Empresa: {empresa_header}
- Fecha: {fecha_hoy}
- Tipo de análisis: {instruccion_tipo[tipo_reporte]}
- Audiencia: {instruccion_audiencia[audiencia]}

REGLAS ABSOLUTAS — OBLIGATORIAS:
1. NUNCA inventes, supongas ni incluyas conceptos, cifras o términos que no aparezcan en los datos. Solo analiza lo que existe en el archivo.
2. Si un dato no está disponible, omite ese punto. No lo rellenes.
3. El header del HTML debe mostrar: nombre "{empresa_header}" en h1, y debajo en clase "meta" la fecha {fecha_hoy} y el tipo de reporte "{tipo_reporte}".

ANÁLISIS ADAPTATIVO — identifica el tipo de datos y adapta los 4 bloques:

- Si son estados financieros o flujos de caja:
  Bloque 1: Salud de liquidez | Bloque 2: Variaciones clave | Bloque 3: Alertas y red flags | Bloque 4: Recomendaciones

- Si son gastos, costes o mantenimiento:
  Bloque 1: Resumen de gasto total y KPIs principales | Bloque 2: Distribución por categoría y conceptos con mayor peso | Bloque 3: Alertas y desviaciones detectadas | Bloque 4: Recomendaciones de optimización

- Si son ventas o ingresos:
  Bloque 1: Rendimiento general | Bloque 2: Análisis por producto, cliente o periodo | Bloque 3: Alertas y tendencias | Bloque 4: Recomendaciones

- Si son otro tipo de datos:
  Adapta los 4 bloques al contexto real. Usa títulos descriptivos que reflejen lo que son los datos.

Contexto adicional: {contexto if contexto else 'Ninguno'}

Datos:
{contenido}

Devuelve SOLO el HTML completo empezando por <!DOCTYPE html>. Sin explicaciones."""

        cliente = anthropic.Anthropic(api_key=API_KEY)
        html_chunks = []

        with cliente.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for i, text in enumerate(stream.text_stream):
                html_chunks.append(text)
                if i % 50 == 0:
                    progreso.info(f"⏳ Generando tu reporte... {len(''.join(html_chunks))} caracteres procesados")

        progreso.empty()
        html = "".join(html_chunks)
        html = html.replace("```html", "").replace("```", "").strip()
        st.success("✅ Reporte generado correctamente.")
        st.components.v1.html(html, height=2000, scrolling=True)
        st.download_button(
            label="⬇️ Descargar reporte",
            data=html,
            file_name="reporte_financiero.html",
            mime="text/html"
        )
