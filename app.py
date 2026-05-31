import streamlit as st
import pandas as pd
import anthropic

st.set_page_config(page_title="Reporte Financiero IA", page_icon="📊")
st.title("📊 Reporte Financiero con IA")
st.write("Sube tu Excel y recibe un análisis ejecutivo en segundos.")

API_KEY = st.secrets["ANTHROPIC_API_KEY"]

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])
contexto = st.text_area("Contexto adicional (opcional)", placeholder="Ej: Marzo fue atípico por vacaciones...")

if archivo is not None:
    if st.button("Generar reporte"):
        with st.spinner("Analizando tu archivo..."):
            df = pd.read_excel(archivo)
            contenido = df.to_string()

            prompt = f"""Eres un analista financiero experto. Genera un reporte ejecutivo en HTML usando EXACTAMENTE este CSS y estructura. No cambies nada del estilo.

CSS FIJO OBLIGATORIO:
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b;padding:24px}}
.header{{background:#1e3a5f;color:white;padding:24px 32px;border-radius:12px;margin-bottom:24px}}
.header h1{{font-size:22px;font-weight:600}}
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

ESTRUCTURA DE LOS 4 BLOQUES:
1. Salud de Liquidez — KPIs principales con clases positivo/alerta/critico
2. Variaciones Clave — comparativas con periodos anteriores
3. Alertas y Red Flags — lista con badges de color
4. Recomendaciones de Acción — lista numerada con acciones concretas

Contexto adicional: {contexto if contexto else 'Ninguno'}

Datos:
{contenido}

Devuelve SOLO el HTML completo empezando por <!DOCTYPE html>. Sin explicaciones."""

            cliente = anthropic.Anthropic(api_key=API_KEY)
            respuesta = cliente.messages.create(
                model="claude-opus-4-5",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            html = respuesta.content[0].text
            html = html.replace("```html", "").replace("```", "").strip()
            st.success("✅ Reporte generado correctamente.")
            st.components.v1.html(html, height=2000, scrolling=True)
            st.download_button(
                label="⬇️ Descargar reporte",
                data=html,
                file_name="reporte_financiero.html",
                mime="text/html"
            )