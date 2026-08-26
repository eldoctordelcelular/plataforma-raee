import sys
import io
import datetime
from xhtml2pdf import pisa
import traceback

def generar_pdf_certificado(entidad, codigo_cert, fecha_str, materia_prima, carbono_evitada, residuos_peligrosos):
    html_template = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <style>
      @page {{
        size: A4 portrait;
        margin: 18mm 16mm;
        @bottom-center {{
          content: "Certificado emitido electrónicamente por Club REDE - INACAP Sede Valparaíso | Registro de Trazabilidad Ambiental";
          font-size: 8pt;
          color: #6b7280;
          font-family: Arial, Helvetica, sans-serif;
        }}
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
    </style>
    </head>
    <body>
    <div class="cert-container">
      <div class="header">
        <div class="badge">Economía Circular & Trazabilidad RAEE</div>
        <h1>Certificado de Valorización de Residuos Electrónicos</h1>
        <h2>Club de Reciclaje y Economía Circular (Club REDE) &bull; INACAP Valparaíso</h2>
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
            <td>85.0%</td>
            <td>Reintegración directa de piezas a talleres</td>
          </tr>
          <tr>
            <td><strong>Índice de Circularidad Local (ICL)</strong></td>
            <td>92.0%</td>
            <td>Aprovechamiento y retención regional</td>
          </tr>
          <tr>
            <td><strong>Ratio de Conversión de Chatarra a Activo (RCC)</strong></td>
            <td>4.2x</td>
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
            <div class="sig-role">Coordinación General y Dirección Técnica<br>Club REDE &bull; INACAP Valparaíso</div>
          </td>
          <td>
            <div class="sig-line"></div>
            <div class="sig-name">Comité de Trazabilidad y Sostenibilidad</div>
            <div class="sig-role">Validación Ambiental y Valorización RAEE<br>Región de Valparaíso, Chile</div>
          </td>
        </tr>
      </table>
    </div>
    </body>
    </html>"""
    
    dest = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_template), dest=dest)
    return dest.getvalue()

try:
    generar_pdf_certificado("Test", "REDE-123", "24/08/2026", 100, 50, 5.5)
    print("Success generating full certificate!")
except Exception as e:
    traceback.print_exc()
