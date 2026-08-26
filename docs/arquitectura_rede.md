# Especificación Técnica: MVP Triage REDE

## Objetivo
Crear una aplicación web en Python usando `streamlit` para registrar y clasificar dispositivos electrónicos.

## Stack Tecnológico
- Frontend/Backend: Streamlit
- Base de Datos: Supabase (PostgreSQL) usando la librería `supabase`
- Inteligencia Artificial: `google-generativeai` (Gemini Pro) para análisis multimodal de imágenes.

## Flujo Funcional
1. Mostrar un título: "REDE - Triage Inteligente de Dispositivos".
2. Proveer un cargador de archivos (`st.file_uploader`) para subir una imagen del equipo.
3. Proveer un campo de texto para "Observaciones iniciales".
4. Al presionar el botón "Analizar y Registrar":
   - Cargar variables de entorno (`dotenv`).
   - Enviar la imagen y las observaciones a la API de Gemini Pro.
   - Pedirle a Gemini que retorne un JSON estructurado con las claves: `tipo_dispositivo`, `marca_modelo`, `estado_visual`, `destino_triage` (este último debe ser estrictamente 'Reparación para Donación', 'Extracción de Repuestos' o 'Despacho a Reciclador Base').
   - Parsear el JSON recibido.
   - Insertar el registro en la tabla `inventario_dispositivos` de Supabase usando el cliente oficial.
5. Mostrar un mensaje de éxito y los datos extraídos en pantalla.

## Reglas de Implementación
- El código principal debe estar en `src/app.py`.
- Usar `python-dotenv` para cargar las credenciales desde el archivo `.env`.
- Manejar excepciones (bloques try/except) en caso de que la IA no retorne un JSON válido o falle la conexión a la base de datos.