import streamlit as st
import pandas as pd
import requests
import base64
import threading
import os
import json
import smtplib
import math
import random
import datetime
import qrcode
from io import BytesIO
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
from streamlit_geolocation import streamlit_geolocation

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Club REDE • Trazabilidad y Reciclaje RAEE",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE DISEÑO VISUAL ELABORADO (CSS MODERNO HIGH-TECH ECO) ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Variables de Color e Identidad */
    :root {
        --bg-main: #0a0f1d;
        --card-bg: rgba(16, 26, 48, 0.75);
        --card-border: rgba(0, 214, 143, 0.25);
        --accent-emerald: #00D68F;
        --accent-cyan: #00B4D8;
        --accent-gold: #FFB703;
        --accent-coral: #EF233C;
        --text-white: #FFFFFF;
        --text-muted: #94A3B8;
    }

    /* Ocultar elementos nativos de Streamlit */
    #MainMenu, footer, header, [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    div[style*="position: fixed"][style*="bottom:"] { display: none !important; }

    /* Estilo General del Cuerpo */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f1c34 0%, #080d1a 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #F8FAFC !important;
    }

    /* Tarjetas de Contenedor con Efecto Glassmorphism */
    .rede-card {
        background: rgba(18, 30, 56, 0.65);
        border: 1px solid rgba(0, 214, 143, 0.2);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .rede-card:hover {
        border-color: rgba(0, 214, 143, 0.45);
        transform: translateY(-2px);
    }

    /* Cabecera Principal Hero */
    .hero-container {
        text-align: center;
        padding: 30px 15px 20px 15px;
        margin-bottom: 25px;
        background: linear-gradient(180deg, rgba(0, 214, 143, 0.08) 0%, rgba(10, 15, 29, 0) 100%);
        border-bottom: 1px solid rgba(0, 214, 143, 0.15);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(0, 214, 143, 0.15);
        border: 1px solid #00D68F;
        color: #00D68F;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        padding: 6px 14px;
        border-radius: 50px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #00D68F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 8px;
        font-weight: 400;
    }

    /* Estilo de los Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        justify-content: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        padding: 0 24px !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 214, 143, 0.2) 0%, rgba(0, 180, 216, 0.2) 100%) !important;
        border: 1px solid #00D68F !important;
        color: #00D68F !important;
        box-shadow: 0 0 15px rgba(0, 214, 143, 0.3) !important;
    }

    /* Inputs y Campos de Texto */
    .stTextInput>div>div>input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-size: 0.95rem !important;
        padding: 12px 14px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00D68F !important;
        box-shadow: 0 0 10px rgba(0, 214, 143, 0.3) !important;
    }

    /* Botones de Acción Primarios */
    .stButton>button {
        background: linear-gradient(135deg, #00D68F 0%, #057A55 100%) !important;
        color: #0A0F1D !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(0, 214, 143, 0.3) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 214, 143, 0.5) !important;
        color: #FFFFFF !important;
    }

    /* Botones de Descarga */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        width: 100% !important;
    }

    /* Métricas Personalizadas */
    [data-testid="stMetricValue"] {
        color: #00D68F !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- INICIALIZACIÓN SUPABASE Y GEMINI ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Error al inicializar cliente Supabase: {e}")

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
if api_key:
    genai.configure(api_key=api_key)

# --- FUNCIONES DE CÁLCULO Y OPTIMIZACIÓN ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def optimizar_imagen(imagen_subida):
    img = Image.open(imagen_subida)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.thumbnail((320, 320))
    return img

def analizar_con_gemini_reintentos(prompt, imagenes_pil):
    if not api_key:
        raise Exception("Falta configurar la variable GEMINI_API_KEY.")

    parts = [{"text": prompt}]
    for img in imagenes_pil:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=45)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    headers = {"Content-Type": "application/json"}
    modelos_fallback = ["gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-2.0-flash"]
    
    errores = []
    for modelo in modelos_fallback:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        try:
            res = requests.post(endpoint, headers=headers, json=payload, timeout=45)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                errores.append(f"{modelo}: {res.status_code}")
                continue
        except requests.exceptions.RequestException:
            errores.append(f"{modelo}: Timeout")
            continue
            
    raise Exception(f"Saturación de modelos. Detalles: {', '.join(errores)}")

def enviar_correo_resumen(destinatario, datos_triage, cod_donacion="No generado", codigo_empresa="General", imagen_pil=None, origen_donacion="No especificado"):
    try:
        remitente = st.secrets.get("SMTP_EMAIL")
        password = st.secrets.get("SMTP_PASSWORD")
    except Exception:
        remitente = os.getenv("SMTP_EMAIL")
        password = os.getenv("SMTP_PASSWORD")
        
    if not remitente or not password:
        remitente = "contactoclubrede@gmail.com"
        password = os.getenv("SMTP_PASSWORD", "")
    
    if not password:
        print("Aviso: Falta configurar SMTP_PASSWORD para enviar correos.")
        return

    msg = MIMEMultipart('related')
    msg['From'] = f"Club REDE <{remitente}>"
    msg['To'] = destinatario
    msg['Subject'] = f"Constancia de Pre-Registro [{cod_donacion}] • Club REDE"

    msg_alt = MIMEMultipart('alternative')
    msg.attach(msg_alt)

    html = f"""
    <html>
      <body style='font-family: Arial, sans-serif; background-color: #f1f5f9; padding: 25px; margin: 0;'>
        <div style='max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 12px; padding: 28px; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.06);'>
          <div style='text-align: center; border-bottom: 2px solid #00D68F; padding-bottom: 16px; margin-bottom: 20px;'>
            <h1 style='color: #0f172a; margin: 0; font-size: 22px;'>Club REDE • Minería Urbana</h1>
            <p style='color: #059669; font-weight: bold; margin: 4px 0 0 0; text-transform: uppercase; font-size: 13px;'>Constancia Oficial de Pre-Registro RAEE</p>
          </div>
          
          <p style='font-size: 15px; color: #334155;'>Hola,</p>
          <p style='font-size: 14px; color: #475569;'>
            Muchas gracias por sumarte a la red comunitaria de valorización de residuos electrónicos de la Región de Valparaíso.
          </p>
          
          <div style='background-color: #f8fafc; border-left: 4px solid #00D68F; padding: 14px; border-radius: 6px; margin: 20px 0;'>
            <div style='font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: bold;'>Tu Código Único de Donación</div>
            <div style='font-size: 24px; color: #0f172a; font-weight: 800; letter-spacing: 1px; margin-top: 2px;'>{cod_donacion}</div>
            <div style='font-size: 12px; color: #059669; margin-top: 4px;'>Presenta o valida este código en el punto de acopio</div>
          </div>

          <h3 style='color: #1e293b; font-size: 16px; margin-top: 22px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;'>📋 Resumen Técnico del Dispositivo</h3>
          <table style='width: 100%; border-collapse: collapse; font-size: 13.5px; color: #334155; margin-top: 10px;'>
            <tr style='border-bottom: 1px solid #f1f5f9;'>
              <td style='padding: 8px 0; font-weight: bold; width: 40%; color: #64748b;'>Entidad / Empresa:</td>
              <td style='padding: 8px 0; color: #0f172a; font-weight: 600;'>{codigo_empresa}</td>
            </tr>
            <tr style='border-bottom: 1px solid #f1f5f9;'>
              <td style='padding: 8px 0; font-weight: bold; color: #64748b;'>Dispositivo:</td>
              <td style='padding: 8px 0;'>{datos_triage.get('tipo_dispositivo', 'No identificado')}</td>
            </tr>
            <tr style='border-bottom: 1px solid #f1f5f9;'>
              <td style='padding: 8px 0; font-weight: bold; color: #64748b;'>Marca / Modelo:</td>
              <td style='padding: 8px 0;'>{datos_triage.get('marca_modelo', 'No identificado')}</td>
            </tr>
            <tr style='border-bottom: 1px solid #f1f5f9;'>
              <td style='padding: 8px 0; font-weight: bold; color: #64748b;'>Estado Visual:</td>
              <td style='padding: 8px 0;'>{datos_triage.get('estado_visual', 'Sin observaciones')}</td>
            </tr>
            <tr style='border-bottom: 1px solid #f1f5f9;'>
              <td style='padding: 8px 0; font-weight: bold; color: #64748b;'>Destino Sugerido:</td>
              <td style='padding: 8px 0; color: #059669; font-weight: bold;'>{datos_triage.get('destino_triage', 'Reciclaje')}</td>
            </tr>
            <tr>
              <td style='padding: 8px 0; font-weight: bold; color: #64748b;'>Donante:</td>
              <td style='padding: 8px 0;'>{origen_donacion}</td>
            </tr>
          </table>

          {"<div style='margin-top: 20px; text-align: center;'><p style='font-size: 12px; color: #64748b; margin-bottom: 6px;'>Fotografía Registrada:</p><img src='cid:img_equipo' style='max-width: 100%; max-height: 260px; border-radius: 8px; border: 1px solid #e2e8f0;'></div>" if imagen_pil else ""}

          <div style='margin-top: 25px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center;'>
            Club REDE • Circuito de Minería Urbana y Trazabilidad RAEE<br>
            Plataforma REDE-Trace | Valparaíso, Chile
          </div>
        </div>
      </body>
    </html>
    """
    msg_alt.attach(MIMEText(html, 'html'))

    if imagen_pil:
        try:
            buf_img = io.BytesIO()
            imagen_pil.save(buf_img, format='JPEG', quality=65)
            mime_img = MIMEImage(buf_img.getvalue(), name="dispositivo.jpg")
            mime_img.add_header('Content-ID', '<img_equipo>')
            msg.attach(mime_img)
        except Exception as e_att:
            print(f"No se pudo adjuntar la imagen al correo: {e_att}")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        print(f"Correo enviado exitosamente a {destinatario}")
    except Exception as e_send:
        print(f"Error al enviar correo por SMTP: {e_send}")

# ==============================================================================
# --- FLUJO 1: CONFIRMACIÓN DE ENTREGA EN PUNTO FÍSICO (VÍA QR) ---
# ==============================================================================
query_params = st.query_params
if "punto_id" in query_params:
    punto_param = query_params["punto_id"]
    # En versiones recientes de Streamlit, query_params puede devolver una lista o string
    punto_id = punto_param[0] if isinstance(punto_param, list) else str(punto_param)
    
    st.markdown("""
    <div class='hero-container'>
        <div class='hero-badge'>VALIDACIÓN FÍSICA EN TERRENO</div>
        <h1 class='hero-title'>Punto de Acopio REDE</h1>
        <p class='hero-subtitle'>Escaneo verificado en local comercial afiliado</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        st.markdown(f"""
        <div class='rede-card' style='text-align: center;'>
            <h3 style='color: #00D68F; margin-top: 0;'>Punto de Acopio #{punto_id}</h3>
            <p style='color: #94A3B8;'>Ingresa el código que generaste al tomar la foto del equipo en tu casa:</p>
        </div>
        """, unsafe_allow_html=True)
        
        codigo_pre = st.text_input("Código de Pre-Registro (Ej: REDE-12345)", placeholder="REDE-XXXXX").strip().upper()
        
        if st.button("✅ Confirmar Entrega y Obtener Certificado"):
            if not codigo_pre:
                st.warning("Ingresa tu código de donación.")
            elif supabase:
                try:
                    res = supabase.table("inventario_dispositivos").select("*").eq("codigo_donacion", codigo_pre).execute()
                    if res.data and len(res.data) > 0:
                        item = res.data[0]
                        estado_actual = item.get("estado_entrega", "Pendiente")
                        if estado_actual == "Entregado":
                            st.info("ℹ️ Esta donación ya había sido confirmada previamente.")
                        else:
                            supabase.table("inventario_dispositivos").update({
                                "estado_entrega": "Entregado",
                                "origen_donacion": f"Entregado en Punto ID: {punto_id}"
                            }).eq("codigo_donacion", codigo_pre).execute()
                            
                            st.balloons()
                            st.success(f"🎉 ¡Dispositivo '{item.get('tipo_dispositivo', 'Equipo')}' recibido exitosamente! Ha ingresado a la red de minería urbana.")
                            st.info("Ya puedes revisar tus métricas de carbono y circularidad en el Portal de Donantes.")
                    else:
                        st.error(f"Código '{codigo_pre}' no encontrado en la base de datos.")
                except Exception as e_conf:
                    st.error(f"Error al verificar en base de datos: {e_conf}")
            else:
                st.error("No hay conexión con la base de datos.")
    st.stop()

# ==============================================================================
# --- FLUJO 2: APLICACIÓN PRINCIPAL (PORTAL REDE) ---
# ==============================================================================
st.markdown("""
<div class='hero-container'>
    <div class='hero-badge'>CIRCUITO DE MINERÍA URBANA Y LEY REP</div>
    <h1 class='hero-title'>Club REDE • Valparaíso</h1>
    <p class='hero-subtitle'>Plataforma inteligente de clasificación, geolocalización y trazabilidad comunitaria</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "  📸 Clasificador y Pre-Registro  ",
    "  📊 Portal Donantes e Impacto  ",
    "  ⚙️ Administración y Puntos  "
])

# ------------------------------------------------------------------------------
# TAB 1: CLASIFICADOR Y PRE-REGISTRO
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("""
    <div class='rede-card'>
        <h3 style='color: #00B4D8; margin-top: 0;'>📍 1. Localiza tu Punto de Acopio Más Cercano</h3>
        <p style='color: #94A3B8; font-size: 0.95rem;'>Activa el GPS de tu dispositivo para identificar el negocio de barrio donde puedes entregar tu equipo.</p>
    </div>
    """, unsafe_allow_html=True)
    
    ubicacion = streamlit_geolocation()
    lat_usuario = ubicacion.get('latitude')
    lon_usuario = ubicacion.get('longitude')
    
    if lat_usuario and lon_usuario and supabase:
        try:
            res_puntos = supabase.table("puntos_reciclaje").select("*").execute()
            if res_puntos.data:
                distancia_minima = float('inf')
                punto_cercano = None
                for p in res_puntos.data:
                    try:
                        d = calcular_distancia(lat_usuario, lon_usuario, float(p['latitud']), float(p['longitud']))
                        if d < distancia_minima:
                            distancia_minima = d
                            punto_cercano = p
                    except Exception:
                        continue
                if punto_cercano:
                    foto_local = punto_cercano.get('foto_url') or "https://tb-static.uber.com/prod/image-proc/processed_images/23f9535d70a993de06e57e8ca3ba3d2c/a19bb09692310dfd41e49a96c424b3a6.jpeg"
                    st.markdown(f"""
                    <div style='background: rgba(18, 30, 56, 0.85); border: 1px solid rgba(0, 214, 143, 0.35); border-radius: 14px; padding: 18px; margin-bottom: 22px; display: flex; flex-wrap: wrap; gap: 16px; align-items: center;'>
                        <img src='{foto_local}' style='width: 140px; height: 110px; object-fit: cover; border-radius: 10px; border: 1px solid rgba(0, 214, 143, 0.4);' alt='Local'>
                        <div style='flex: 1; min-width: 200px;'>
                            <div style='color: #00D68F; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>Punto de Acopio Afiliado</div>
                            <h3 style='margin: 4px 0; color: #FFFFFF; font-size: 1.35rem;'>🍕 {punto_cercano.get('nombre_negocio', '')}</h3>
                            <p style='margin: 2px 0; color: #94A3B8; font-size: 0.95rem;'>📍 {punto_cercano.get('direccion', '')}</p>
                            <span style='display: inline-block; background: rgba(0, 214, 143, 0.15); color: #00D68F; font-size: 0.85rem; padding: 4px 10px; border-radius: 6px; font-weight: 600; margin-top: 6px;'>
                                Distancia: {distancia_minima:.1f} km de tu ubicación
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e_puntos:
            st.caption(f"No fue posible cargar los puntos de acopio en este momento: {e_puntos}")

    st.markdown("""
    <div class='rede-card'>
        <h3 style='color: #00D68F; margin-top: 0;'>📷 2. Diagnóstico Visual con Inteligencia Artificial</h3>
        <p style='color: #94A3B8; font-size: 0.95rem;'>Toma fotografías claras de las placas o del dispositivo para evaluar su potencial de minería urbana.</p>
    </div>
    """, unsafe_allow_html=True)

    if "registro_key" not in st.session_state:
        st.session_state.registro_key = 0
    rk = st.session_state.registro_key

    c_cam1, c_cam2 = st.columns(2)
    with c_cam1:
        st.markdown("<h5 style='color: #00B4D8;'>Vista Frontal</h5>", unsafe_allow_html=True)
        if st.checkbox("Encender Cámara Frontal", key=f"chk_f_{rk}"):
            f_front = st.camera_input("Capturar", key=f"cam_f_{rk}")
            if f_front:
                st.session_state[f"img_f_{rk}"] = optimizar_imagen(f_front)
            if f"img_f_{rk}" in st.session_state:
                st.image(st.session_state[f"img_f_{rk}"], width=220, caption="Frontal OK")

    with c_cam2:
        st.markdown("<h5 style='color: #00B4D8;'>Vista Trasera / Placa</h5>", unsafe_allow_html=True)
        if st.checkbox("Encender Cámara Trasera", key=f"chk_t_{rk}"):
            f_back = st.camera_input("Capturar", key=f"cam_t_{rk}")
            if f_back:
                st.session_state[f"img_t_{rk}"] = optimizar_imagen(f_back)
            if f"img_t_{rk}" in st.session_state:
                st.image(st.session_state[f"img_t_{rk}"], width=220, caption="Trasera OK")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        codigo_empresa = st.text_input("Código de Entidad / Empresa", placeholder="Ej: INACAP, COLEGIO-ALBORADA", key=f"cod_{rk}")
        origen_donacion = st.text_input("Nombre del Donante / Institución", placeholder="Ej: Daniel Bustamante", key=f"org_{rk}")
    with c_in2:
        observaciones = st.text_input("Observación del Equipo", placeholder="Ej: Router dañado, no enciende", key=f"obs_{rk}")
        correo_usuario = st.text_input("Correo para Recibir Constancia", placeholder="ejemplo@correo.cl", key=f"mail_{rk}")

    if st.button("🚀 Analizar Dispositivo y Generar Pre-Registro"):
        tiene_foto = f"img_f_{rk}" in st.session_state or f"img_t_{rk}" in st.session_state
        if not tiene_foto:
            st.warning("⚠️ Debes capturar al menos una fotografía del aparato.")
        elif not codigo_empresa.strip():
            st.warning("⚠️ El código de entidad es obligatorio para asignar las métricas.")
        else:
            with st.spinner("⚡ Procesando con redes convolucionales y catalogando componentes..."):
                imgs = []
                if f"img_f_{rk}" in st.session_state: imgs.append(st.session_state[f"img_f_{rk}"])
                if f"img_t_{rk}" in st.session_state: imgs.append(st.session_state[f"img_t_{rk}"])
                
                prompt = """
                Analiza el residuo electrónico y responde en estricto formato JSON:
                {
                  "tipo_dispositivo": "string",
                  "marca_modelo": "string",
                  "estado_visual": "string",
                  "destino_triage": "string (Reparación para Donación, Desarme de Repuestos, o Reciclaje de Metales)"
                }
                """
                try:
                    resp = analizar_con_gemini_reintentos(prompt, imgs)
                    resp = resp.replace("```json", "").replace("```", "").strip()
                    datos = json.loads(resp)
                    
                    cod_donacion = f"REDE-{random.randint(10000, 99999)}"
                    
                    datos_db = {
                        "codigo_empresa": codigo_empresa.strip(),
                        "codigo_donacion": cod_donacion,
                        "estado_entrega": "Pendiente",
                        "tipo_dispositivo": datos.get("tipo_dispositivo"),
                        "marca_modelo": datos.get("marca_modelo"),
                        "estado_visual": datos.get("estado_visual"),
                        "destino_triage": datos.get("destino_triage"),
                        "observaciones_ingreso": observaciones,
                        "origen_donacion": origen_donacion
                    }
                    if supabase:
                        try:
                            supabase.table("inventario_dispositivos").insert(datos_db).execute()
                        except Exception as e_db:
                            # Si la base de datos no tiene aún las columnas nuevas, insertar con esquema base
                            if "codigo_donacion" in str(e_db):
                                datos_db_compat = {
                                    "codigo_empresa": codigo_empresa.strip(),
                                    "tipo_dispositivo": datos.get("tipo_dispositivo"),
                                    "marca_modelo": datos.get("marca_modelo"),
                                    "estado_visual": datos.get("estado_visual"),
                                    "destino_triage": datos.get("destino_triage")
                                }
                                supabase.table("inventario_dispositivos").insert(datos_db_compat).execute()
                            else:
                                raise e_db
                    
                    st.markdown(f"""
                    <div style='background: rgba(255, 183, 3, 0.12); border: 2px dashed #FFB703; padding: 20px; border-radius: 12px; text-align: center; margin-top: 20px; margin-bottom: 20px;'>
                        <h2 style='color: #FFB703; margin: 0;'>Código de Entrega: {cod_donacion}</h2>
                        <p style='color: #E2E8F0; font-size: 1rem; margin-top: 8px;'>
                            Lleva tu aparato al punto de acopio y escanea el código QR para validar tu entrega física.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # --- TARJETA DE ANÁLISIS DETALLADO DE IA ---
                    destino_triage_val = datos.get("destino_triage", "Reciclaje de Metales")
                    color_destino = "#00D68F" if "Reparación" in destino_triage_val else ("#00B4D8" if "Desarme" in destino_triage_val else "#FFB703")

                    st.markdown(f"""
                    <div class='rede-card' style='border-color: rgba(0, 214, 143, 0.4);'>
                        <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 15px;'>
                            <h3 style='color: #00D68F; margin: 0;'>🔍 Resultado del Análisis Técnico (IA)</h3>
                            <span style='background: rgba(0, 214, 143, 0.15); border: 1px solid {color_destino}; color: {color_destino}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;'>
                                {destino_triage_val}
                            </span>
                        </div>
                        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;'>
                            <div style='background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);'>
                                <span style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;'>Dispositivo</span>
                                <div style='color: #FFFFFF; font-weight: 700; font-size: 1.05rem;'>{datos.get("tipo_dispositivo", "No identificado")}</div>
                            </div>
                            <div style='background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);'>
                                <span style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;'>Marca / Modelo</span>
                                <div style='color: #FFFFFF; font-weight: 700; font-size: 1.05rem;'>{datos.get("marca_modelo", "No especificado")}</div>
                            </div>
                            <div style='background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);'>
                                <span style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;'>Estado Visual</span>
                                <div style='color: #FFFFFF; font-weight: 600; font-size: 0.95rem;'>{datos.get("estado_visual", "Sin observaciones")}</div>
                            </div>
                            <div style='background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);'>
                                <span style='color: #94A3B8; font-size: 0.8rem; text-transform: uppercase;'>Entidad Donante</span>
                                <div style='color: #00D68F; font-weight: 700; font-size: 1.05rem;'>{codigo_empresa.strip()}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if correo_usuario.strip():
                        threading.Thread(
                            target=enviar_correo_resumen, 
                            args=(
                                correo_usuario.strip(), 
                                datos, 
                                cod_donacion, 
                                codigo_empresa.strip(), 
                                imgs[0] if imgs else None, 
                                origen_donacion
                            )
                        ).start()
                        st.success(f"📧 Se ha enviado la constancia oficial a: {correo_usuario.strip()}")
                except Exception as e:
                    st.error(f"Error en el proceso técnico: {e}")

# ------------------------------------------------------------------------------
# TAB 2: PORTAL DONANTES E IMPACTO AMBIENTAL
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("""
    <div class='rede-card'>
        <h3 style='color: #00D68F; margin-top: 0;'>📊 Consulta de Impacto Comunitario y Certificados Ley REP</h3>
        <p style='color: #94A3B8; font-size: 0.95rem;'>Ingresa tu código institucional para cuantificar el impacto ambiental y social de tus donaciones entregadas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        cod_check = st.text_input("Código de Entidad / Empresa", placeholder="Ej: COLEGIO-ALBORADA", type="password")
    with col_d2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        btn_check = st.button("Consultar Métricas")
        
    if btn_check and cod_check.strip() and supabase:
        res = supabase.table("inventario_dispositivos").select("*").eq("codigo_empresa", cod_check.strip()).eq("estado_entrega", "Entregado").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Cálculo de variables
            rep = len(df[df['destino_triage'] == "Reparación para Donación"])
            des = len(df[df['destino_triage'] == "Desarme de Repuestos"])
            rec = len(df[df['destino_triage'] == "Reciclaje de Metales"])
            total = len(df)
            
            co2 = total * 45.5
            mat = total * 14.2
            circ = ((rep + des) / total) * 100 if total > 0 else 0
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Equipos Entregados", f"{total} uds")
            m2.metric("Índice de Circularidad", f"{circ:.1f}%")
            m3.metric("CO₂e Evitado", f"{co2:.1f} kg")
            m4.metric("Minerales Salvados", f"{mat:.1f} kg")
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            g1, g2 = st.columns(2)
            with g1:
                fig_pie = px.pie(
                    names=['Reparación', 'Desarme', 'Reciclaje'],
                    values=[rep, des, rec],
                    title="Destino de los Equipos en Taller",
                    color_discrete_sequence=['#00D68F', '#00B4D8', '#FFB703'],
                    hole=0.45
                )
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
                st.plotly_chart(fig_pie, use_container_width=True)
            with g2:
                fig_bar = px.bar(
                    x=['Materia Prima (kg)', 'CO₂ Mitigado (kg)'],
                    y=[mat, co2],
                    title="Balance Ambiental Acumulado",
                    color_discrete_sequence=['#00D68F'],
                    text_auto=True
                )
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.dataframe(df[['created_at', 'tipo_dispositivo', 'marca_modelo', 'destino_triage']], use_container_width=True)
        else:
            st.info("No se registran donaciones validadas físicamente para este código aún.")

# ------------------------------------------------------------------------------
# TAB 3: ADMINISTRACIÓN Y EMISIÓN DE PUNTOS QR
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("""
    <div class='rede-card'>
        <h3 style='color: #FFB703; margin-top: 0;'>⚙️ Panel de Control de Red de Acopio</h3>
        <p style='color: #94A3B8; font-size: 0.95rem;'>Acceso restringido para administración de puntos y generación de señalética QR.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Credenciales por defecto configurables desde Secrets o variables de entorno
    try:
        ADMIN_USER = st.secrets.get("ADMIN_USER", "admin")
        ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", "admin123")
    except Exception:
        ADMIN_USER = os.getenv("ADMIN_USER", "admin")
        ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "admin123")

    if "admin_logueado" not in st.session_state:
        st.session_state.admin_logueado = False

    if not st.session_state.admin_logueado:
        st.markdown("<h4 style='color: #00D68F;'>🔐 Iniciar Sesión de Administrador</h4>", unsafe_allow_html=True)
        col_u, col_p = st.columns(2)
        with col_u:
            user_input = st.text_input("Usuario Administrador", placeholder="Ej: admin", key="input_admin_user")
        with col_p:
            pass_input = st.text_input("Contraseña", placeholder="••••••••", type="password", key="input_admin_pass")
            
        if st.button("Ingresar al Panel"):
            if user_input.strip() == ADMIN_USER and pass_input == ADMIN_PASS:
                st.session_state.admin_logueado = True
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
    else:
        col_hdr1, col_hdr2 = st.columns([4, 1])
        with col_hdr1:
            st.success(" Sesión de Administrador activa")
        with col_hdr2:
            if st.button("Cerrar Sesión"):
                st.session_state.admin_logueado = False
                st.rerun()

        st.markdown("---")
        st.markdown("### 🏪 Crear Nuevo Punto de Acopio")
        c_pt1, c_pt2 = st.columns(2)
        with c_pt1:
            n_nombre = st.text_input("Nombre del Local Comercial / Almacén", value="Pizzería Ciudad de Pie")
            n_dir = st.text_input("Dirección Completa", value="Plazuela Ecuador 623, Valparaíso")
            n_foto = st.text_input("URL de Fotografía del Local (Google / Web)", value="https://tb-static.uber.com/prod/image-proc/processed_images/23f9535d70a993de06e57e8ca3ba3d2c/a19bb09692310dfd41e49a96c424b3a6.jpeg")
        with c_pt2:
            n_lat = st.number_input("Latitud GPS", format="%.6f", value=-33.045754)
            n_lon = st.number_input("Longitud GPS", format="%.6f", value=-71.626331)
            url_base = st.text_input("URL Pública de la Aplicación", value="https://plataforma-raee.streamlit.app/")
        
        if st.button("📦 Guardar Punto y Generar Señalética QR"):
            if not n_nombre.strip() or not n_dir.strip():
                st.warning("Por favor completa el nombre y la dirección del local.")
            else:
                nuevo_id = str(random.randint(100, 999))
                if supabase:
                    try:
                        supabase.table("puntos_reciclaje").insert({
                            "id": nuevo_id, 
                            "nombre_negocio": n_nombre.strip(),
                            "direccion": n_dir.strip(), 
                            "latitud": n_lat, 
                            "longitud": n_lon,
                            "foto_url": n_foto.strip()
                        }).execute()
                    except Exception as e_ins:
                        st.error(f"Error al guardar en base de datos: {e_ins}")
                    
                url_qr = f"{url_base.strip().rstrip('/')}/?punto_id={nuevo_id}"
                qr = qrcode.QRCode(version=1, box_size=10, border=3)
                qr.add_data(url_qr)
                qr.make(fit=True)
                img_qr = qr.make_image(fill_color="#0A0F1D", back_color="#00D68F")
                
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                
                st.success(f"Punto #{nuevo_id} dado de alta con éxito.")
                st.image(buf.getvalue(), caption=f"Código QR oficial para {n_nombre} ({url_qr})", width=260)
                st.download_button("⬇️ Descargar Señalética QR (PNG)", buf.getvalue(), file_name=f"QR_{nuevo_id}.png", mime="image/png")