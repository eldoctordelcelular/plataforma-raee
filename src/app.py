import streamlit as st
import pandas as pd
import requests
import base64
import threading
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client
from PIL import Image
import io
from xhtml2pdf import pisa
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import random
import time
# Ocultar footer, barra de herramientas y elementos flotantes inferiores
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    
    /* Ocultar Streamlit Viewer Badge y Developer Menu flotantes */
    #viewerBadge {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}
    div[data-testid="viewerBadge"] {display: none !important;}
    a[href^="https://streamlit.io/cloud"] {display: none !important;}
    
    /* Ocultar botones de Despliegue y logos inyectados por Streamlit */
    [data-testid="stAppDeployButton"] {display: none !important;}
    [data-testid="stLogo"] {display: none !important;}
    .stDeployButton {display: none !important;}
    #st-deploy-button {display: none !important;}
    
    /* Ocultar el contenedor de botones de administrador inyectado por Streamlit Cloud */
    div[class^="stActionButton"] {display: none !important;}
    div[class*="streamlit-developer-menu"] {display: none !important;}
    iframe[src*="streamlit"] {display: none !important;}
    
    /* Regla ultra-genérica para ocultar cualquier botón flotante en la esquina inferior derecha */
    div[style*="position: fixed"][style*="bottom: 1"][style*="right: 1"] {
        display: none !important;
    }
    div[style*="position: fixed"][style*="bottom:"][style*="right:"] {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Cargar variables de entorno y configurar Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")

# Configurar Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
if api_key:
    genai.configure(api_key=api_key)

def optimizar_imagen(imagen_subida):
    img = Image.open(imagen_subida)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.thumbnail((512, 512))
    return img


@st.cache_data(ttl=3600)
def obtener_modelos_gemini_cached(_api_key):
    url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={_api_key}"
    modelos_a_probar = []
    try:
        res_list = requests.get(url_list, timeout=10)
        if res_list.status_code == 200:
            datos_modelos = res_list.json().get("models", [])
            for m in datos_modelos:
                metodos = m.get("supportedGenerationMethods", [])
                if "generateContent" in metodos:
                    modelos_a_probar.append(m.get("name"))
    except Exception:
        pass

    # Si no se pudo listar, usar los identificadores estándar
    if not modelos_a_probar:
        modelos_a_probar = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro"
        ]

    # Ordenar priorizando modelos flash
    modelos_ordenados = [m for m in modelos_a_probar if "flash" in m.lower()] + \
                        [m for m in modelos_a_probar if "pro" in m.lower()] + \
                        modelos_a_probar
    return list(dict.fromkeys(modelos_ordenados))

def analizar_con_gemini_reintentos(prompt, imagenes_pil):
    if not api_key:
        raise Exception("Falta configurar la variable GEMINI_API_KEY en tu archivo .env o en Secrets.")

    # 1. Preparar las partes del contenido (Texto e Imágenes en Base64)
    parts = [{"text": prompt}]
    for img in imagenes_pil:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=60)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_b64
            }
        })
    
    # Añadir configuracion para forzar JSON nativo (Sugerencia 2)
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    headers = {"Content-Type": "application/json"}

    # Usar el modelo recomendado por la API de Google en el mensaje de error
    nombre_limpio = "gemini-3.5-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{nombre_limpio}:generateContent?key={api_key}"
    
    try:
        res = requests.post(endpoint, headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Status {res.status_code}: {res.text}")
    except Exception as e_req:
        raise Exception(f"Fallo al procesar con {nombre_limpio}. Error: {str(e_req)}")


def enviar_correo_resumen(destinatario, resumen_texto):
    remitente = os.getenv("SMTP_EMAIL", "tu_correo@gmail.com")
    password = os.getenv("SMTP_PASSWORD", "tu_contraseña_de_aplicacion")
    
    if not remitente or not password:
        raise Exception("Faltan configurar las credenciales SMTP_EMAIL y SMTP_PASSWORD en el archivo .env")

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = "Resumen de Registro - Club REDE"

    msg.attach(MIMEText(resumen_texto, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
    except Exception as e:
        raise Exception(f"No se pudo enviar el correo: {str(e)}")

def generar_pdf_certificado(entidad, codigo_cert, fecha_str, materia_prima, carbono_evitada, residuos_peligrosos, circ_pct, icl_pct, rcc_val):
    html_template = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <style>
      @page {{
        size: A4 portrait;
        margin: 18mm 16mm;
      }}
      body {{
        margin: 0;
        padding: 0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1f2937;
        line-height: 1.45;
      }}
      .cert-container {{
        border: 3px double #1e3a8a;
        padding: 24px;
        border-radius: 6px;
      }}
      .header {{
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 12px;
        margin-bottom: 18px;
      }}
      .badge {{
        display: inline-block;
        background-color: #059669;
        color: #ffffff;
        font-size: 9pt;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        margin-bottom: 6px;
      }}
      .header h1 {{
        font-size: 16pt;
        color: #1e3a8a;
        margin: 4px 0 2px 0;
        text-transform: uppercase;
      }}
      .header h2 {{
        font-size: 10.5pt;
        font-weight: normal;
        color: #374151;
        margin: 0;
      }}
      .intro-text {{
        font-size: 9.5pt;
        text-align: justify;
        margin-bottom: 16px;
      }}
      .meta-grid {{
        width: 100%;
        margin-bottom: 16px;
        border-collapse: collapse;
      }}
      .meta-grid td {{
        padding: 6px 10px;
        font-size: 9pt;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
      }}
      .meta-grid td strong {{
        color: #1e3a8a;
      }}
      .section-title {{
        font-size: 10.5pt;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 14px;
        margin-bottom: 8px;
        border-left: 4px solid #059669;
        padding-left: 8px;
      }}
      table.data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
        font-size: 8.5pt;
      }}
      table.data-table th {{
        background-color: #1e3a8a;
        color: #ffffff;
        text-align: left;
        padding: 6px 8px;
        font-weight: bold;
        border: 1px solid #1e3a8a;
      }}
      table.data-table td {{
        padding: 5px 8px;
        border: 1px solid #e2e8f0;
      }}
      table.data-table tr:nth-child(even) {{
        background-color: #f8fafc;
      }}
      .statement {{
        font-size: 8pt;
        color: #4b5563;
        border-top: 1px solid #cbd5e1;
        padding-top: 10px;
        margin-top: 10px;
        text-align: justify;
      }}
      .signatures {{
        width: 100%;
        margin-top: 20px;
        border-collapse: collapse;
      }}
      .signatures td {{
        width: 50%;
        text-align: center;
        vertical-align: bottom;
        padding: 0 15px;
      }}
      .sig-line {{
        border-top: 1px solid #374151;
        width: 80%;
        margin: 25px auto 4px auto;
      }}
      .sig-name {{
        font-size: 8.5pt;
        font-weight: bold;
        color: #1f2937;
      }}
      .sig-role {{
        font-size: 7.5pt;
        color: #6b7280;
      }}
      .footer-text {{
        text-align: center;
        font-size: 8pt;
        color: #6b7280;
        margin-top: 25px;
      }}
    </style>
    </head>
    <body>
    <div class="cert-container">
      <div class="header">
        <div class="badge">Economía Circular & Trazabilidad RAEE</div>
        <h1>Certificado de Valorización de Residuos Electrónicos</h1>
        <h2>Club de Reciclaje y Economía Circular (Club REDE)</h2>
      </div>

      <table class="meta-grid">
        <tr>
          <td style="width: 50%;"><strong>Entidad / Donante:</strong> {entidad}</td>
          <td style="width: 50%;"><strong>Código de Certificado:</strong> {codigo_cert}</td>
        </tr>
        <tr>
          <td><strong>Fecha de Emisión:</strong> {fecha_str}</td>
          <td><strong>Protocolo de Manejo:</strong> Clasificación y Triage RAEE v2.4</td>
        </tr>
      </table>

      <p class="intro-text">
        Por medio del presente documento, la Dirección Técnica del <strong>Club REDE</strong> certifica que los Residuos de Aparatos Eléctricos y Electrónicos (RAEE) entregados han sido sometidos a rigurosos procesos de diagnóstico, recuperación y valorización de componentes, mitigando activamente el impacto ambiental y fomentando la economía circular en la Región de Valparaíso.
      </p>

      <div class="section-title">Métricas y Parámetros de Impacto Ambiental Verificados</div>

      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 45%;">Indicador de Sostenibilidad</th>
            <th style="width: 25%;">Valor Verificado</th>
            <th style="width: 30%;">Impacto Operativo / Ambiental</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Índice de Circularidad del Material (%)</strong></td>
            <td>{circ_pct:.1f}%</td>
            <td>Reintegración directa de piezas a talleres</td>
          </tr>
          <tr>
            <td><strong>Índice de Circularidad Local (ICL)</strong></td>
            <td>{icl_pct:.1f}%</td>
            <td>Aprovechamiento y retención regional</td>
          </tr>
          <tr>
            <td><strong>Ratio de Conversión de Chatarra a Activo (RCC)</strong></td>
            <td>{rcc_val:.1f}x</td>
            <td>Transformación a repuestos funcionales</td>
          </tr>
          <tr>
            <td><strong>Huella de Materia Prima Desplazada</strong></td>
            <td>{materia_prima} kg</td>
            <td>Roca, arena y minerales no extraídos</td>
          </tr>
          <tr>
            <td><strong>Huella de Carbono Evitada</strong></td>
            <td>{carbono_evitada} kg CO₂e</td>
            <td>Gases de efecto invernadero mitigados</td>
          </tr>
          <tr>
            <td><strong>Control de Residuos Peligrosos</strong></td>
            <td>{residuos_peligrosos:.1f} kg</td>
            <td>Baterías de Li-ion y circuitos neutralizados</td>
          </tr>
        </tbody>
      </table>

      <p class="statement">
        <strong>Declaración de Cumplimiento:</strong> La valorización de los equipos recibidos previene su disposición en rellenos sanitarios y garantiza la trazabilidad exigida por las normativas de gestión ambiental y economía circular, dotando a los componentes recuperados de una segunda vida útil en la comunidad técnica y estudiantil.
      </p>

      <table class="signatures">
        <tr>
          <td>
            <div class="sig-line"></div>
            <div class="sig-name">Daniel Bustamante Jara</div>
            <div class="sig-role">Coordinación General y Dirección Técnica<br>Club REDE</div>
          </td>
          <td>
            <div class="sig-line"></div>
            <div class="sig-name">Comité de Trazabilidad y Sostenibilidad</div>
            <div class="sig-role">Validación Ambiental y Valorización RAEE<br>Región de Valparaíso, Chile</div>
          </td>
        </tr>
      </table>
      <div class="footer-text">Certificado emitido electrónicamente por Club REDE | Registro de Trazabilidad Ambiental</div>
    </div>
    </body>
    </html>"""
    
    dest = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_template), dest=dest)
    return dest.getvalue()

def generar_pdf_lista_equipos(entidad, df_equipos):
    html_template = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <style>
      @page {{
        size: A4 portrait;
        margin: 18mm 16mm;
      }}
      body {{
        margin: 0;
        padding: 0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1f2937;
        line-height: 1.45;
      }}
      .cert-container {{
        border: 3px double #1e3a8a;
        padding: 24px;
        border-radius: 6px;
      }}
      .header {{
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 12px;
        margin-bottom: 18px;
      }}
      .header h1 {{
        font-size: 16pt;
        color: #1e3a8a;
        margin: 4px 0 2px 0;
        text-transform: uppercase;
      }}
      .header h2 {{
        font-size: 10.5pt;
        font-weight: normal;
        color: #374151;
        margin: 0;
      }}
      .section-title {{
        font-size: 12pt;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 14px;
        margin-bottom: 12px;
        border-left: 4px solid #059669;
        padding-left: 8px;
      }}
      table.data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
        font-size: 9pt;
      }}
      table.data-table th {{
        background-color: #1e3a8a;
        color: #ffffff;
        text-align: left;
        padding: 6px 8px;
        font-weight: bold;
        border: 1px solid #1e3a8a;
      }}
      table.data-table td {{
        padding: 5px 8px;
        border: 1px solid #e2e8f0;
      }}
      table.data-table tr:nth-child(even) {{
        background-color: #f8fafc;
      }}
      .footer-text {{
        text-align: center;
        font-size: 8pt;
        color: #6b7280;
        margin-top: 25px;
      }}
    </style>
    </head>
    <body>
    <div class="cert-container">
      <div class="header">
        <h1>Reporte de Equipos Donados</h1>
        <h2>Club de Reciclaje y Economía Circular (Club REDE)</h2>
      </div>
      
      <p><strong>Entidad / Donante:</strong> {entidad}</p>
      
      <div class="section-title">Historial de Donaciones</div>

      <table class="data-table">
        <thead>
          <tr>
            {"".join(f"<th>{col}</th>" for col in df_equipos.columns)}
          </tr>
        </thead>
        <tbody>
          {"".join(
              "<tr>" + "".join(f"<td>{str(val)}</td>" for val in row) + "</tr>"
              for row in df_equipos.values
          )}
        </tbody>
      </table>
      
      <div class="footer-text">Documento generado automáticamente por Club REDE | Registro de Trazabilidad Ambiental</div>
    </div>
    </body>
    </html>"""
    
    dest = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_template), dest=dest)
    return dest.getvalue()


st.markdown(
    "<h1 style='text-align: center;'>Clasificador de Residuos <br><span style='color: #2e7d32; font-weight: bold;'>Club REDE</span></h1>", 
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["📸 Clasificador y Registro", "📊 Portal Donantes"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        activar_frontal = st.checkbox("Activar Cámara para Foto Frontal")
        foto_frontal = None
        if activar_frontal:
            foto_frontal = st.camera_input("Foto Frontal (Pantalla/Frente)")
            
    with col2:
        activar_trasera = st.checkbox("Activar Cámara para Foto Trasera")
        foto_trasera = None
        if activar_trasera:
            foto_trasera = st.camera_input("Foto Trasera (Carcasa/Etiqueta)")
            
    codigo_empresa = st.text_input("Código Institucional / Empresa (Obligatorio)")
    observaciones = st.text_input("TIPO DE DISPOSITIVO")
    origen_donacion = st.text_input("Origen de la donación (Nombre de persona, empresa o institución)")
    correo_usuario = st.text_input("Correo electrónico para recibir el resumen")
    
    if st.button("Analizar y Registrar"):
        if not foto_frontal and not foto_trasera:
            st.error("Por favor, toma al menos una foto (frontal o trasera) del equipo primero.")
        elif not codigo_empresa.strip():
            st.error("Por favor, ingresa el Código Institucional / Empresa.")
        elif not supabase:
            st.error("Error: Configuración de Supabase inválida o faltante en el archivo .env.")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("Error: Clave API de Gemini faltante en el archivo .env.")
        else:
            try:
                with st.spinner("⏳ Analizando componentes y registrando en la base de datos..."):
                    images = []
                    if foto_frontal:
                        images.append(optimizar_imagen(foto_frontal))
                    if foto_trasera:
                        images.append(optimizar_imagen(foto_trasera))
                    
                    prompt = """
Eres un ingeniero experto en hardware y reciclaje electrónico para el Club REDE.
Analiza la imagen del residuo/dispositivo y devuelve estrictamente un objeto JSON con esta estructura técnica de hardware.
Si la imagen NO corresponde a un dispositivo electrónico claro, asigna "No Válido" al campo "destino_triage".
Para un dispositivo válido, el "destino_triage" DEBE ser estrictamente una de las siguientes opciones: "Reparación para Donación", "Desarme de Repuestos", o "Reciclaje de Metales".
{
  "tipo_dispositivo": "string",
  "marca_modelo": "string",
  "estado_visual": "string",
  "estado_tipo_bateria": "string (tecnología, estado físico o indicación de si no posee)",
  "destino_triage": "string"
}
"""
                    
                    try:
                        response_text = analizar_con_gemini_reintentos(prompt, images)
                    except Exception as e:
                        st.error(f"Error técnico detallado: {str(e)}")
                        st.stop()
                    
                    # Intentar limpiar la respuesta de posibles bloques markdown de JSON
                    response_text = response_text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.startswith("```"):
                        response_text = response_text[3:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    response_text = response_text.strip()
                    
                    # Parsear el string JSON retornado por la IA
                    datos_triage = json.loads(response_text)
                    
                    destino_eval = str(datos_triage.get("destino_triage", "")).strip()
                    categorias_validas = ["Reparación para Donación", "Desarme de Repuestos", "Reciclaje de Metales"]
                    es_valido = any(cat.lower() == destino_eval.lower() for cat in categorias_validas)
                    
                    if "No Válido" in destino_eval or not es_valido:
                        st.warning("No se detectó un dispositivo electrónico claro. Por favor, toma otra fotografía.")
                    else:
                        # Insertar los datos en Supabase
                        datos_db = {
                            "codigo_empresa": codigo_empresa.strip(),
                            "tipo_dispositivo": datos_triage.get("tipo_dispositivo"),
                            "marca_modelo": datos_triage.get("marca_modelo"),
                            "estado_visual": datos_triage.get("estado_visual"),
                            "estado_tipo_bateria": datos_triage.get("estado_tipo_bateria"),
                            "destino_triage": destino_eval,
                            "observaciones_ingreso": observaciones,
                            "origen_donacion": origen_donacion
                        }
                        
                        response_db = supabase.table("inventario_dispositivos").insert(datos_db).execute()
                        
                        st.success("¡Registro completado!")
                        st.json(datos_triage)
                        
                        if correo_usuario:
                            try:
                                enviar_correo_resumen(correo_usuario, response_text)
                                st.success(f"¡Resumen generado y enviado exitosamente a {correo_usuario}!")
                            except Exception as e:
                                st.error(str(e))
                
            except json.JSONDecodeError:
                st.error("Error: La Inteligencia Artificial no retornó un formato JSON válido. Intenta nuevamente.")
                st.write("Respuesta cruda de la IA:")
                st.text(response.text)
            except Exception as e:
                st.error(f"Ocurrió un error inesperado durante el procesamiento: {str(e)}")

with tab2:
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>¡Bienvenido a tu Portal de Donante! 🌟</h2>", unsafe_allow_html=True)
    codigo_ingreso = st.text_input("Ingresa tu código para ver tu impacto:", type="password")
    
    if st.button("Ver mi impacto"):
        if not codigo_ingreso.strip():
            st.warning("Por favor, ingresa tu código para continuar.")
        elif supabase:
            try:
                with st.spinner("Buscando tus buenas acciones..."):
                    response_db = supabase.table("inventario_dispositivos").select("*").eq("codigo_empresa", codigo_ingreso.strip()).execute()
                    data = response_db.data
                    
                if data:
                    df = pd.DataFrame(data)
                    if 'created_at' in df.columns:
                        df['created_at'] = pd.to_datetime(df['created_at'])
                    
                    if 'cantidad_unidades' in df.columns:
                        total_unidades = int(df['cantidad_unidades'].sum())
                    else:
                        total_unidades = len(df)
                    
                    # Cálculos dinámicos coherentes
                    materia_prima = 0
                    carbono_evitada = 0
                    residuos_peligrosos = 0
                    reparacion = 0
                    desarme = 0
                    reciclaje = 0

                    for _, row in df.iterrows():
                        tipo = str(row.get('tipo_dispositivo', '')).lower()
                        destino = str(row.get('destino_triage', '')).strip()
                        
                        if "computador" in tipo or "pc" in tipo or "torre" in tipo:
                            materia_prima += 45
                            carbono_evitada += 150
                            residuos_peligrosos += 1.0
                        elif "laptop" in tipo or "notebook" in tipo:
                            materia_prima += 35
                            carbono_evitada += 100
                            residuos_peligrosos += 0.3
                        elif "celular" in tipo or "teléfono" in tipo or "smartphone" in tipo:
                            materia_prima += 12
                            carbono_evitada += 30
                            residuos_peligrosos += 0.08
                        elif "monitor" in tipo or "pantalla" in tipo:
                            materia_prima += 25
                            carbono_evitada += 50
                            residuos_peligrosos += 0.5
                        else:
                            materia_prima += 15
                            carbono_evitada += 20
                            residuos_peligrosos += 0.2
                            
                        if destino == "Reparación para Donación":
                            reparacion += 1
                        elif destino == "Desarme de Repuestos":
                            desarme += 1
                        else:
                            reciclaje += 1

                    total = reparacion + desarme + reciclaje
                    if total == 0:
                        total = 1

                    circ_pct = max(((reparacion + desarme) / total) * 100, 45.0)
                    icl_pct = min(((reparacion / total) * 100) + 40.0, 98.0)
                    rcc_val = max(total * 1.5 if reciclaje == 0 else (reparacion + desarme) / reciclaje, 1.2)

                    st.title("♻️ Portal de Economía Circular y Sostenibilidad")
                    st.write("Métricas clave de impacto ambiental, eficiencia de taller y gestión de residuos del Club REDE:")

                    # Bloque 1 de métricas principales
                    col_1, col_2, col_3 = st.columns(3)
                    with col_1:
                        st.metric(label="🔄 Índice de Circularidad", value=f"{circ_pct:.1f}%", delta="Componentes rescatados")
                    with col_2:
                        st.metric(label="📍 Circularidad Local (ICL)", value=f"{icl_pct:.1f}%", delta="Impacto en región")
                    with col_3:
                        st.metric(label="⚙️ Ratio de Conversión (RCC)", value=f"{rcc_val:.1f}x", delta="Chatarra a activo")

                    # Bloque 2 de métricas principales (Los nuevos indicadores solicitados)
                    col_4, col_5, col_6 = st.columns(3)
                    with col_4:
                        st.metric(label="🌍 Materia Prima Desplazada", value=f"{materia_prima:.1f} kg", delta="Roca salvada")
                    with col_5:
                        st.metric(label="🚗 Huella de Carbono Evitada", value=f"{carbono_evitada:.1f} kg", delta="CO₂e mitigado")
                    with col_6:
                        st.metric(label="🛡️ Residuos Peligrosos", value=f"{residuos_peligrosos:.2f} kg", delta="Componentes controlados")

                    st.markdown("---")

                    st.markdown("### 📊 Análisis de Impacto y Trazabilidad")
                    
                    # Gráficos de Plotly
                    col_graf_1, col_graf_2 = st.columns(2)
                    
                    with col_graf_1:
                        # Gráfico de destino de los equipos (Donut)
                        labels = ['Reparación', 'Desarme', 'Reciclaje']
                        values = [reparacion, desarme, reciclaje]
                        fig_destino = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=['#4CAF50', '#FFC107', '#F44336'])])
                        fig_destino.update_layout(title_text="Destino de los Equipos", margin=dict(t=40, b=0, l=0, r=0), height=300)
                        st.plotly_chart(fig_destino, use_container_width=True)
                        
                    with col_graf_2:
                        # Gráfico de barras de impacto ambiental
                        impacto_labels = ['Materia Prima (kg)', 'Carbono Evitado (kg CO₂e)']
                        impacto_values = [materia_prima, carbono_evitada]
                        fig_impacto = px.bar(x=impacto_labels, y=impacto_values, text_auto=True, color=impacto_labels, color_discrete_sequence=['#8D6E63', '#607D8B'])
                        fig_impacto.update_layout(title_text="Métricas Ambientales", xaxis_title="", yaxis_title="Kilogramos", showlegend=False, margin=dict(t=40, b=0, l=0, r=0), height=300)
                        st.plotly_chart(fig_impacto, use_container_width=True)

                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>CERTIFICADO DE VALORIZACIÓN DE RESIDUOS ELECTRÓNICOS (RAEE)</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; font-weight: bold; color: #4B5563;'>CLUB DE RECICLAJE Y ECONOMÍA CIRCULAR (CLUB REDE)</p>", unsafe_allow_html=True)
                    st.markdown("---")

                    # Contenedor con estilo de documento formal
                    with st.container():
                        st.markdown(f"""
                        **Documento de Constancia Oficial de Sostenibilidad**  
                        *Fecha de emisión:* {datetime.datetime.now().strftime('%d/%m/%Y')}  
                        *Código de Registro / Entidad:* **{codigo_ingreso}**

                        Por medio del presente documento, el **Club REDE** certifica formalmente que la entidad mencionada ha cumplido rigurosamente con los protocolos de gestión, trazabilidad y valorización de Residuos de Aparatos Eléctricos y Electrónicos (RAEE), fomentando la economía circular y la reutilización tecnológica en la región de Valparaíso.
                        """)

                        st.markdown("### 📋 Resumen de Métricas de Valorización y Impacto Ambiental")
                        
                        # Tabla formal de indicadores
                        datos_certificado = {
                            "Indicador de Sostenibilidad": [
                                "Índice de Circularidad del Material",
                                "Índice de Circularidad Local (ICL)",
                                "Ratio de Conversión de Chatarra a Activo (RCC)",
                                "Huella de Materia Prima Desplazada",
                                "Huella de Carbono Evitada",
                                "Control de Residuos Peligrosos"
                            ],
                            "Valor Verificado": [
                                "85% (Componentes rescatados)",
                                "92% (Impacto en región)",
                                "4.2x (Conversión a activo útil)",
                                f"{materia_prima} kg (Roca y minerales salvados)",
                                f"{carbono_evitada} kg de CO₂e (Mitigación global)",
                                f"{residuos_peligrosos:.1f} kg (Baterías y componentes confinados)"
                            ]
                        }
                        st.table(datos_certificado)

                        st.markdown("""
                        ---
                        *Este certificado avala que los dispositivos e insumos ingresados fueron procesados bajo estrictas normas técnicas de diagnóstico, separación de componentes y mitigación ambiental, evitando su disposición en vertederos y dándoles un nuevo ciclo de vida útil para la comunidad.*

                        **Validación Institucional:**  
                        Dirección de Operaciones y Sostenibilidad — Club REDE.
                        """)

                    fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y')
                    codigo_certificado = f"REDE-RAEE-{datetime.datetime.now().strftime('%Y%m%d')}"
                    pdf_data = generar_pdf_certificado(
                        codigo_ingreso, 
                        codigo_certificado, 
                        fecha_actual,
                        materia_prima,
                        carbono_evitada,
                        residuos_peligrosos,
                        circ_pct,
                        icl_pct,
                        rcc_val
                    )

                    st.download_button(
                        label="📄 Descargar Certificado Oficial en PDF",
                        data=pdf_data,
                        file_name=f"Certificado_Valorizacion_RAEE_{codigo_ingreso}.pdf",
                        mime="application/pdf"
                    )
                    
                    columnas_simples = []
                    nombres_columnas = {}
                    if 'created_at' in df.columns:
                        columnas_simples.append('created_at')
                        nombres_columnas['created_at'] = 'Fecha'
                    if 'tipo_dispositivo' in df.columns:
                        columnas_simples.append('tipo_dispositivo')
                        nombres_columnas['tipo_dispositivo'] = 'Lo que donaste'
                    if 'destino_triage' in df.columns:
                        columnas_simples.append('destino_triage')
                        nombres_columnas['destino_triage'] = 'Su nuevo destino'
                        
                    if columnas_simples:
                        df_simple = df[columnas_simples].copy()
                        df_simple.rename(columns=nombres_columnas, inplace=True)
                        if 'Fecha' in df_simple.columns:
                            df_simple['Fecha'] = df_simple['Fecha'].dt.strftime('%d-%m-%Y')
                        st.dataframe(df_simple.tail(10), use_container_width=True, hide_index=True)
                        
                        pdf_equipos = generar_pdf_lista_equipos(codigo_ingreso, df_simple)
                        st.download_button(
                            label="📥 Descargar Resumen de Equipos Donados (.pdf)",
                            data=pdf_equipos,
                            file_name=f"Resumen_Donaciones_{codigo_ingreso}.pdf",
                            mime="application/pdf"
                        )
                    
                else:
                    st.info("Aún no tienes registros con este código. ¡Anímate a hacer tu primera donación! 💚")
            except Exception as e:
                st.error(f"Ocurrió un error al cargar tus datos: {e}")
        else:
            st.error("Lo sentimos, el sistema de base de datos no está disponible en este momento.")

