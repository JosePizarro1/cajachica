from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.http import HttpResponse
from datetime import date,timedelta
from .models import *
from decimal import Decimal
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date
from django.contrib import messages
from .models import Gasto, Concepto, Rendicion
from django.db import IntegrityError
import json
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Q
import requests
from requests.exceptions import Timeout, TooManyRedirects, RequestException, HTTPError
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Personal
from django.shortcuts import get_object_or_404
from datetime import date
from decimal import Decimal
from django.shortcuts import render
import urllib.parse


def editar_personal(request, id):
    personal = get_object_or_404(Personal, id=id)
    # Convertir remuneración a string con dos decimales si no es None
    if personal.remuneracion is not None:
        personal.remuneracion = f"{float(personal.remuneracion):.2f}"
    return render(request, 'editar_personal.html', {'personal': personal})

def crear_contraseña(request, personal_id):
    personal = get_object_or_404(Personal, id=personal_id)

    # Datos a enviar al otro sistema
    nombre = personal.apellidos_nombres
    telefono = personal.celular

    # URL del otro sistema que recibe los datos
    url_crear_cliente = "http://cafeteria.egatur.edu.pe/crear-cliente/"

    # Parámetros para la petición GET
    params = {
        "nombre": nombre,
        "telefono": telefono
    }

    try:
        response = requests.get(url_crear_cliente, params=params, timeout=5)

        # Verifica si la respuesta tiene contenido
        if response.status_code == 201:
            messages.success(request, "Cliente creado exitosamente en el otro sistema.")
        elif response.status_code == 204:
            # Si la respuesta es 204 (sin contenido), se puede mostrar un mensaje
            messages.warning(request, "La respuesta del sistema está vacía, pero el cliente no presentó errores.")
        else:
            # Verifica si la respuesta tiene un cuerpo JSON
            try:
                response_data = response.json()
                error_message = response_data.get("mensaje", "No se pudo crear el cliente.")
                messages.warning(request, f"Error al crear el cliente: {error_message} (Código de estado: {response.status_code})")
            except ValueError:
                # Si la respuesta no es un JSON válido, muestra el contenido de la respuesta como texto
                messages.error(request, f"Error al procesar la respuesta del sistema: {response.text} (Código de estado: {response.status_code})")

    # Manejo de diferentes excepciones
    except Timeout:
        messages.error(request, "Error: Tiempo de espera agotado al conectar con el otro sistema.")

    except TooManyRedirects:
        messages.error(request, "Error: Demasiados redireccionamientos al conectar con el otro sistema.")

    except HTTPError as http_err:
        messages.error(request, f"Error HTTP al conectar con el otro sistema: {http_err}")

    except RequestException as e:
        # Cualquier otra excepción genérica de requests
        messages.error(request, f"Error inesperado al conectar con el otro sistema: {str(e)}")

    return redirect("ver_personal")
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from django.conf import settings

def draw_centered_text(p, text, y_position, font="Helvetica-Bold", size=16, page_width=letter[0]):
    p.setFont(font, size)
    text_width = p.stringWidth(text, font, size)
    x_position = (page_width - text_width) / 2  # Centrar el texto
    p.drawString(x_position, y_position, text)

def draw_logo(p, image_name, x=490, y=690, width=75, height=75):
    image_path = os.path.join(settings.BASE_DIR, "static/images", image_name)

    if os.path.exists(image_path):  # Verifica si la imagen existe
        p.drawImage(image_path, x, y, width, height, mask='auto')
    else:
        print(f"⚠️ Error: No se encontró la imagen en {image_path}")


def generar_pdf(request, persona_id):
    try:
        persona = Personal.objects.get(id=persona_id)

        # Crear la respuesta como un archivo PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f'Ficha_{persona.apellidos_nombres}.pdf'.replace(" ", "_")  # Reemplaza espacios por guiones bajos
        filename = urllib.parse.quote(filename)  # Codifica caracteres especiales

        response['Content-Disposition'] = f'attachment; filename={filename}'
        # Crear el PDF
        p = canvas.Canvas(response, pagesize=letter)
        # Dibujar el logo en la esquina superior derecha
        draw_logo(p, "egatur_logo.png")


        # Título
        p.setFont("Helvetica-Bold", 16)
        draw_centered_text(p, "FICHA DE INGRESO DE PERSONAL", 740)
        # Posición inicial para el contenido
        y_position = 700

        # Sección I - Datos del Trabajador
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "I. DATOS DEL TRABAJADOR")
        y_position -= 20  # Ajustar la posición después del título de la sección

        y_position = draw_label_value(p, "Nº DE DNI :", persona.dni or "-", y_position)
        y_position = draw_label_value(p, "APELLIDOS Y NOMBRES:", persona.apellidos_nombres or "-", y_position)
        y_position = draw_label_value(p, "FECHA DE NACIMIENTO:", persona.fecha_nacimiento.strftime('%d/%m/%Y') if persona.fecha_nacimiento else "-", y_position)
        y_position = draw_label_value(p, "Nº DE CELULAR:", persona.celular or "-", y_position)
        y_position = draw_label_value(p, "CORREO ELECTRÓNICO:", persona.correo_personal or "-", y_position)
        y_position = draw_label_value(p, "DIRECCION:", persona.direccion or "-", y_position)
        # Línea de separación
        draw_line(p, y_position)
        y_position -= 10
        # Sección II - Datos Laborales
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "II. DATOS LABORALES")
        y_position -= 20  # Ajustar la posición después del título de la sección
        y_position = draw_label_value(p, "PERIODO DE INICIO:", persona.periodo_inicio.strftime('%d/%m/%Y') if persona.periodo_inicio else "-", y_position)
        y_position = draw_label_value(p, "PERIODO DE FIN:", persona.periodo_fin.strftime('%d/%m/%Y') if persona.periodo_fin else "-", y_position)
        y_position = draw_label_value(p, "TIPO DE TRABAJADOR:", persona.tipo_trabajador or "-", y_position)
        y_position = draw_label_value(p, "TIPO DE CONTRATO:", persona.tipo_contrato or "-", y_position)
        y_position = draw_label_value(p, "TIPO DE PAGO:", persona.tipo_pago or "-", y_position)
        # NUEVA LÍNEA: PERIODICIDAD DE INGRESO
        y_position = draw_label_value(p, "PERIODICIDAD DE INGRESO:", "MENSUAL", y_position)

        # NUEVA LÍNEA: REMUNERACIÓN
        y_position = draw_label_value(p, "REMUNERACIÓN:", f"S/. {persona.remuneracion:.2f}" if persona.remuneracion else "S/. 0.00", y_position)

        y_position = draw_label_value(p, "ASIGNACIÓN FAMILIAR:", "Sí" if persona.asignacion_familiar else "No", y_position)

        # Línea de separación
        draw_line(p, y_position)
        y_position -= 10

        # Sección III - Datos de Seguridad Social
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "III. DATOS DE SEGURIDAD SOCIAL")
        y_position -= 20

        y_position = draw_label_value(p, "RÉGIMEN DE SALUD:", (persona.regimen_salud or "-").upper(), y_position)
        # RÉGIMEN PENSIONARIO Y SUS DETALLES EN LA MISMA LÍNEA
        p.setFont("Helvetica-Bold", 10)
        p.drawString(100, y_position, "RÉGIMEN PENSIONARIO:")

        p.setFont("Helvetica", 10)
        p.drawString(280, y_position, (persona.regimen_pensionario or "-").upper())

        # Agregar DETALLES RÉGIMEN PENSIONARIO al costado
        p.setFont("Helvetica-Bold", 10)
        p.drawString(400, y_position, "DETALLES:")

        p.setFont("Helvetica", 10)
        p.drawString(460, y_position, persona.regimen_pensionario_details or "-")
        # Línea de separación
        draw_line(p, y_position-13)
        y_position -= 20

        # Sección IV - Datos de la Situación Educativa
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "IV. DATOS DE LA SITUACIÓN EDUCATIVA")
        y_position -= 20

        y_position = draw_label_value(p, "SITUACIÓN EDUCATIVA:", persona.situacion_educativa or "-", y_position)
        y_position = draw_label_value(p, "TIPO DE INSTRUCCIÓN:", persona.tipo_instruccion or "-", y_position)
        y_position = draw_label_value(p, "INSTITUCIÓN:", persona.institucion or "-", y_position)
        y_position = draw_label_value(p, "CARRERA DE ESTUDIO:", persona.carrera_estudio or "-", y_position)
        y_position = draw_label_value(p, "AÑO DE EGRESO:", persona.ano_egreso or "-", y_position)

        # Agregar líneas para firma al final del PDF
        y_position -= 40  # Espacio antes de las firmas

        # Línea izquierda (firma vacía)
        p.line(100, y_position, 300, y_position)  # Línea
        # Línea derecha (Firma del trabajador)
        p.line(350, y_position, 550, y_position)

        # Nombre del trabajador a la derecha
        p.setFont("Helvetica", 10)
        p.drawString(380, y_position - 15, persona.apellidos_nombres)
        # Finalizar el PDF
        p.showPage()
        p.save()

        return response
    except Exception as e:
        messages.error(request, f"Error al generar el PDF: {str(e)}")
        return redirect("ver_personal")


def draw_label_value(p, label, value, y_position):
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, y_position, label)  # Escribir la etiqueta en su posición

    p.setFont("Helvetica", 10)
    x_position = 280  # Aumentamos la posición X para dar más espacio a la etiqueta
    p.drawString(x_position, y_position, value)  # Escribir el valor más a la derecha

    y_position -= 20  # Bajar la posición para la siguiente línea

    return y_position


def draw_line(p, y_position):
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(100, y_position +8, 500, y_position + 8)

def guardar_datos(request):
    if request.method == "POST":

        return redirect("ver_personal")

    return render(request, "ficha_ingreso.html")



def guardar_datos_editados(request, id_personal):
    if request.method == "POST":
        def get_value(field):
            """Devuelve un string vacío ("") si el campo está vacío."""
            value = request.POST.get(field, "").strip()
            return value if value else ""

        def get_date(field):
            """Convierte la fecha a formato correcto o devuelve None si está vacía."""
            date_value = request.POST.get(field, "").strip()
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").date() if date_value else None
            except ValueError:
                return None  # Evita errores si la fecha no es válida

        ficha = get_object_or_404(Personal, id=id_personal)

        # Actualizar los valores
        ficha.dni = get_value("dni")
        ficha.nombres = get_value("nombres")
        ficha.fecha_nacimiento = get_date("fecha_nacimiento")
        ficha.celular = get_value("celular")
        ficha.correo_personal = get_value("correo_personal")
        ficha.correo_corporativo = get_value("correo_corporativo")
        ficha.direccion = get_value("direccion")
        ficha.fecha_inicio = get_date("fecha_inicio")
        ficha.fecha_fin = get_date("fecha_fin")
        ficha.tipo_trabajador = get_value("tipo_trabajador")
        ficha.tipo_contrato = get_value("tipo_contrato")
        ficha.tipo_pago = get_value("tipo_pago")
        ficha.asignacion_familiar = bool(request.POST.get("asignacion_familiar"))
        ficha.regimen_salud = get_value("regimen_salud")
        ficha.regimen_pensionario = get_value("regimen_pensionario")
        ficha.regimen_pensionario_details=get_value("regimen_pensionario_details")  # Agregar el campo de detalles
        ficha.situacion_educativa = get_value("situacion_educativa")
        ficha.tipo_instruccion = get_value("tipo_instruccion")
        ficha.institucion = get_value("institucion")
        ficha.carrera_estudio = get_value("carrera_estudio")
        ficha.ocupacion = get_value("ocupacion")
        ficha.remuneracion = get_value("remuneracion")
        ficha.ano_egreso=get_value("ano_egreso")

        ficha.save()
        messages.success(request, "Ficha actualizada correctamente.")
        return redirect("ver_personal")


@csrf_exempt
def eliminar_concepto(request, id):
    if request.method == 'POST':
        try:
            concepto = Concepto.objects.get(id=id)
            concepto.delete()
            return JsonResponse({'status': 'success'})
        except Concepto.DoesNotExist:
            return JsonResponse({'error': 'El concepto no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def crear_concepto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nivel = int(request.POST.get('nivel'))
        id_padre = request.POST.get('id_padre')

        if nivel != 1 and not id_padre:
            return JsonResponse({'error': 'El nivel 2 y 3 requieren un concepto padre.'}, status=400)

        id_concepto_padre = Concepto.objects.get(id=id_padre) if id_padre else None
        Concepto.objects.create(
            concepto_nombre=nombre,
            nivel=nivel,
            id_concepto_padre=id_concepto_padre,
        )
        return JsonResponse({'status': 'success'})


@csrf_exempt
def editar_concepto(request, id):
    if request.method == 'POST':
        concepto = Concepto.objects.get(id=id)
        concepto.concepto_nombre = request.POST.get('nombre')
        concepto.save()
        return JsonResponse({'status': 'success'})


def build_concepto_hierarchy(conceptos):
    """Crea una jerarquía de conceptos basada en sus niveles."""
    hierarchy = []

    # Agrupar conceptos por nivel
    nivel1 = conceptos.filter(nivel=1)
    nivel2 = conceptos.filter(nivel=2)
    nivel3 = conceptos.filter(nivel=3)

    for nivel1_item in nivel1:
        nivel1_dict = {
            "concepto": nivel1_item,
            "subconceptos": []
        }
        for nivel2_item in nivel2.filter(id_concepto_padre=nivel1_item):
            nivel2_dict = {
                "concepto": nivel2_item,
                "subconceptos": []
            }
            for nivel3_item in nivel3.filter(id_concepto_padre=nivel2_item):
                nivel2_dict["subconceptos"].append({
                    "concepto": nivel3_item,
                    "subconceptos": []
                })
            nivel1_dict["subconceptos"].append(nivel2_dict)
        hierarchy.append(nivel1_dict)

    return hierarchy

def conceptos(request):
    conceptos = Concepto.objects.all()
    conceptos_hierarchy = build_concepto_hierarchy(conceptos)

    return render(request, 'conceptos.html', {
        'conceptos_hierarchy': conceptos_hierarchy
    })
def reportes(request):
    # Filtrar los conceptos de nivel 1 y nivel 2
    conceptos_nivel_1 = Concepto.objects.filter(nivel=1)
    conceptos_nivel_2 = Concepto.objects.filter(nivel=2)

    # Pasa ambos conjuntos de conceptos al contexto
    return render(request, 'reportes.html', {
        'conceptos_nivel_1': conceptos_nivel_1,
        'conceptos_nivel_2': conceptos_nivel_2,
    })

def convertir_a_float(valor):
    """Convierte un string con coma o punto decimal a float correctamente."""
    if isinstance(valor, str):
        valor = valor.replace(',', '.')  # Reemplazar coma por punto
    try:
        return float(valor)
    except ValueError:
        return 0.00  # Si hay error, devolver 0.00

@login_required  # Asegurar que el usuario esté autenticado
def generar_reporte_diario(request):
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return HttpResponse("Error: Usuario no autenticado", status=403)

    hoy = date.today()

    # Obtener el saldo inicial desde la URL y convertirlo
    saldo_inicial_str = request.GET.get('saldo_inicial', '0.00')
    saldo_inicial = convertir_a_float(saldo_inicial_str)

    # Filtrar ingresos y gastos del usuario actual y de hoy
    ingresos = Ingreso.objects.filter(usuario_creador=request.user, fecha_ingreso=hoy)
    gastos = Gasto.objects.filter(usuario_creador=request.user, fecha_gasto=hoy)

    # Calcular totales asegurando que los valores sean floats
    total_ingresos = sum(convertir_a_float(i.importe) for i in ingresos)
    total_gastos = sum(convertir_a_float(g.importe) for g in gastos)

    # Crear el archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Diario"

    # Estilos
    bold_font = Font(bold=True)
    center_alignment = Alignment(horizontal="center", vertical="center")

    # Encabezado
    ws.append(["REPORTE DIARIO"])
    ws.append([f"Fecha: {hoy.strftime('%d de %B de %Y')}"])

    ws.append([])
    ws.append(["I. SALDO DE APERTURA DE CAJA"])
    ws.append([f"{saldo_inicial:.2f}"])  # Se coloca el saldo inicial con dos decimales

    # Sección II: Recepción de Efectivo
    ws.append([])
    ws.append(["II. RECEPCIÓN DE EFECTIVO"])
    ws.append(["ID", "Fecha", "Comentario", "Monto"])

    # Aplicar negrita a los encabezados de la tabla
    for col in range(1, 5):
        cell = ws.cell(row=ws.max_row, column=col)
        cell.font = bold_font
        cell.alignment = center_alignment

    # Agregar los ingresos a la tabla con el formato correcto
    for ingreso in ingresos:
        monto_formateado = f"{convertir_a_float(ingreso.importe):.2f}"  # Formatear monto correctamente
        ws.append([ingreso.id, ingreso.fecha_ingreso, ingreso.observacion or "", monto_formateado])

    # Agregar una fila vacía y luego el total de ingresos
    ws.append([])
    ws.append(["TOTAL INGRESOS", "", "", f"{total_ingresos:.2f}"])

    # Aplicar negrita al total de ingresos
    for cell in ws[ws.max_row]:
        cell.font = bold_font
        cell.alignment = center_alignment

    # Sección III: Gastos
    ws.append([])
    ws.append(["III. GASTOS"])
    ws.append(["Total Gastos", f"{total_gastos:.2f}"])

    # Aplicar negrita a los subtítulos de la sección de gastos
    for cell in ws["A"]:
        cell.font = bold_font

    # Crear respuesta HTTP con el archivo Excel
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="Reporte_Diario_{hoy}.xlsx"'
    wb.save(response)

    return response

def reporte_mensual(request):
    if request.method == "POST":
        mes_numero = request.POST.get("mes")
        if not mes_numero:
            return HttpResponse("Debe seleccionar un mes.", status=400)

        wb = Workbook()
        ws = wb.active
        ws.title = f"Reporte Mensual - {mes_numero}"

        # Estilos
        bold_font = Font(bold=True)
        bold_gray_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

        # Encabezado
        ws.append(["Concepto", "Total"])
        for cell in ws[1]:
            cell.font = bold_font

        # Variable para el total general de los conceptos nivel 1
        total_general = 0
        row = 2

        # Conceptos de nivel 1
        conceptos_nivel_1 = Concepto.objects.filter(nivel=1)
        for concepto1 in conceptos_nivel_1:
            total_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_1=concepto1)
                         .aggregate(total=Sum('importe'))['total'] or 0) \
                      + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_1=concepto1)
                         .aggregate(total=Sum('importe'))['total'] or 0)

            total_general += total_mes  # Solo sumar los totales de nivel 1
            ws.append([concepto1.concepto_nombre, total_mes])
            for cell in ws[row]:
                cell.font = bold_font
            ws[row - 1][0].fill = bold_gray_fill
            row += 1

            # Conceptos de nivel 2
            conceptos_nivel_2 = Concepto.objects.filter(id_concepto_padre=concepto1)
            for concepto2 in conceptos_nivel_2:
                total_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_2=concepto2)
                             .aggregate(total=Sum('importe'))['total'] or 0) \
                          + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_2=concepto2)
                             .aggregate(total=Sum('importe'))['total'] or 0)

                ws.append(["   " + concepto2.concepto_nombre, total_mes])
                ws[row - 1][0].font = bold_font
                row += 1

                # Conceptos de nivel 3
                conceptos_nivel_3 = Concepto.objects.filter(id_concepto_padre=concepto2)
                for concepto3 in conceptos_nivel_3:
                    total_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_3=concepto3)
                                 .aggregate(total=Sum('importe'))['total'] or 0) \
                              + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_3=concepto3)
                                 .aggregate(total=Sum('importe'))['total'] or 0)

                    ws.append(["      " + concepto3.concepto_nombre, total_mes])
                    row += 1

        # Agregar total general solo de los conceptos de nivel 1
        ws.append(["TOTAL GENERAL", total_general])
        for cell in ws[row]:
            cell.font = bold_font
            cell.fill = bold_gray_fill

        # Generar respuesta HTTP con el archivo Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Reporte_Mensual_{mes_numero}_{date.today().year}.xlsx"'
        wb.save(response)
        return response

    return HttpResponse("Método no permitido", status=405)
def reporte_anual(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Anual"

    # Estilos
    bold_font = Font(bold=True)  # Negrita
    bold_gray_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")  # Fondo gris claro

    # Nombres de los meses
    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    # Encabezado
    ws.append(['Concepto'] + meses + ['Total Anual'])
    for cell in ws[1]:
        cell.font = bold_font

    # Conceptos de nivel 1
    conceptos_nivel_1 = Concepto.objects.filter(nivel=1)
    row = 2
    for concepto1 in conceptos_nivel_1:
        valores_mensuales = []
        total_anual = 0  # Inicializar el total anual
        total_mes = [0] * 12  # Inicializar la lista para los totales de cada mes

        for mes in meses:
            mes_numero = meses.index(mes) + 1
            total_mes_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_1=concepto1)
                             .aggregate(total=Sum('importe'))['total'] or 0) \
                              + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_1=concepto1)
                             .aggregate(total=Sum('importe'))['total'] or 0)
            valores_mensuales.append(total_mes_mes)
            total_anual += total_mes_mes  # Acumular el total anual
            total_mes[mes_numero - 1] += total_mes_mes  # Acumular total por mes

        # Insertar los datos del concepto de nivel 1
        ws.append([concepto1.concepto_nombre] + valores_mensuales + [total_anual])
        row += 1

        # Aplicar formato de negrita y fondo gris para nivel 1
        for cell in ws[row - 1]:
            cell.font = bold_font
        ws[row - 1][0].fill = bold_gray_fill

        # Conceptos de nivel 2
        conceptos_nivel_2 = Concepto.objects.filter(id_concepto_padre=concepto1)
        for concepto2 in conceptos_nivel_2:
            valores_mensuales = []
            total_anual = 0  # Inicializar el total anual
            for mes in meses:
                mes_numero = meses.index(mes) + 1
                total_mes_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_2=concepto2)
                                 .aggregate(total=Sum('importe'))['total'] or 0) \
                                  + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_2=concepto2)
                                 .aggregate(total=Sum('importe'))['total'] or 0)
                valores_mensuales.append(total_mes_mes)
                total_anual += total_mes_mes  # Acumular el total anual

            ws.append(["   " + concepto2.concepto_nombre] + valores_mensuales + [total_anual])
            row += 1

            # Aplicar formato de negrita para nivel 2
            ws[row - 1][0].font = bold_font

            # Conceptos de nivel 3
            conceptos_nivel_3 = Concepto.objects.filter(id_concepto_padre=concepto2)
            for concepto3 in conceptos_nivel_3:
                valores_mensuales = []
                total_anual = 0  # Inicializar el total anual
                for mes in meses:
                    mes_numero = meses.index(mes) + 1
                    total_mes_mes = (Gasto.objects.filter(fecha_gasto__month=mes_numero, concepto_nivel_3=concepto3)
                                     .aggregate(total=Sum('importe'))['total'] or 0) \
                                      + (Rendicion.objects.filter(fecha_operacion__month=mes_numero, concepto_nivel_3=concepto3)
                                     .aggregate(total=Sum('importe'))['total'] or 0)
                    valores_mensuales.append(total_mes_mes)
                    total_anual += total_mes_mes  # Acumular el total anual

                ws.append(["      " + concepto3.concepto_nombre] + valores_mensuales + [total_anual])
                row += 1

        # Agregar el total de la suma por cada mes de los conceptos de nivel 1
        ws.append(['Total por Mes'] + total_mes + [sum(total_mes)])
        for cell in ws[row]:
            cell.font = bold_font
        ws[row][0].fill = bold_gray_fill

    # Generar respuesta HTTP para la descarga del archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Reporte_Anual_{date.today().year}.xlsx"'
    wb.save(response)
    return response


@login_required
def ver_personal(request):
    # Obtener todos los registros del modelo Personal
    personal = Personal.objects.all()

    return render(request, 'ver_personal.html', {'personal': personal})


def guardar_datos1(request):
    if request.method == 'POST':
        # Funciones para manejar los valores y las fechas
        def get_value(field):
            """Devuelve un string vacío ("") si el campo está vacío."""
            value = request.POST.get(field, "").strip()
            return value if value else ""

        def get_date(field):
            """Convierte la fecha a formato correcto o devuelve None si está vacía."""
            date_value = request.POST.get(field, "").strip()
            try:
                return datetime.strptime(date_value, "%Y-%m-%d").date() if date_value else None
            except ValueError:
                return None  # Evita errores si la fecha no es válida

        # Verificar si ya existe un proveedor con el mismo DNI
        if Proveedor.objects.filter(ruc_dni=request.POST['dni']).exists():
            return JsonResponse({'error': 'Ya existe un proveedor con ese DNI. Elimine el proveedor antes de continuar.'}, status=400)

        # Guardar los datos del Personal
        personal = Personal(
            dni=get_value('dni'),
            apellidos_nombres=get_value('apellidos_nombres'),
            fecha_nacimiento=get_date('fecha_nacimiento'),
            celular=get_value('celular'),
            correo_personal=get_value('correo_personal'),
            correo_corporativo=get_value('correo_corporativo'),
            direccion=get_value('direccion'),
            periodo_inicio=get_date('periodo_inicio'),
            periodo_fin=get_date('periodo_fin'),
            tipo_trabajador=get_value('tipo_trabajador'),
            tipo_contrato=get_value('tipo_contrato'),
            tipo_pago=get_value('tipo_pago'),
            nombre_cuenta=get_value('nombre_cuenta'),
            numero_cuenta=get_value('numero_cuenta'),
            asignacion_familiar=request.POST.get('asignacion_familiar') == 'on',
            ocupacion=get_value('ocupacion'),
            remuneracion=get_value('remuneracion'),
            regimen_salud=get_value('regimen_salud'),
            regimen_pensionario=get_value('regimen_pensionario'),
            situacion_educativa=get_value('situacion_educativa'),
            tipo_instruccion=get_value('tipo_instruccion'),
            institucion=get_value('institucion'),
            carrera_estudio=get_value('carrera_estudio'),
            ano_egreso=get_value('ano_egreso'),
            cci=get_value('cci'),
        )
        personal.save()

        # Crear un Proveedor con los datos del Personal
        proveedor = Proveedor(
            ruc_dni=personal.dni,  # DNI como RUC_DNI
            razon_social=personal.apellidos_nombres,  # Apellidos y nombres como razón social
            telefono=personal.celular,  # Celular como teléfono
            nombre_contacto=""  # Nombre de contacto vacío
        )
        proveedor.save()  # Guardar el proveedor
        # Crear una cuenta bancaria asociada al proveedor
        cuenta_bancaria = CuentaBancaria(
            proveedor=proveedor,
            nombre_banco=personal.nombre_cuenta,  # Se iguala a nombre_cuenta del personal
            numero_cuenta=personal.numero_cuenta,  # Se iguala a numero_cuenta del personal
            cci=personal.cci  # Se iguala a cci del personal
        )
        cuenta_bancaria.save()  # Guardar la cuenta bancaria
        # Respuesta de éxito en formato JSON
        return JsonResponse({'success': 'Datos guardados correctamente y proveedor creado.'}, status=200)


def generar_reporte_json(request):
    try:
        if request.method == 'GET':
            # Obtener parámetros de la solicitud
            concepto_nivel_1 = request.GET.get('concepto_nivel_1', 'todos')
            concepto_nivel_2 = request.GET.get('concepto_nivel_2', 'todos')
            fecha_inicio = request.GET.get('fecha_inicio', None)
            fecha_final = request.GET.get('fecha_final', None)

            # Convertir las fechas a objetos datetime
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                fecha_final_dt = datetime.strptime(fecha_final, "%Y-%m-%d")
            except ValueError:
                return JsonResponse({'error': 'Las fechas proporcionadas no tienen el formato correcto (YYYY-MM-DD).'}, status=400)

            # Filtrar gastos y rendiciones según los parámetros
            gastos = Gasto.objects.filter(fecha_gasto__gte=fecha_inicio_dt, fecha_gasto__lte=fecha_final_dt)
            rendiciones = Rendicion.objects.filter(fecha_operacion__gte=fecha_inicio_dt, fecha_operacion__lte=fecha_final_dt)

            if concepto_nivel_1 != 'todos':
                gastos = gastos.filter(concepto_nivel_1=concepto_nivel_1)
                rendiciones = rendiciones.filter(concepto_nivel_1=concepto_nivel_1)
            if concepto_nivel_2 != 'todos':
                gastos = gastos.filter(concepto_nivel_2=concepto_nivel_2)
                rendiciones = rendiciones.filter(concepto_nivel_2=concepto_nivel_2)

            # Verificar si hay datos para mostrar
            if not gastos.exists() and not rendiciones.exists():
                return JsonResponse({'error': 'No se encontraron registros con los parámetros seleccionados'}, status=404)

            # Agrupar gastos y rendiciones por concepto_nivel_2
            grouped_data = {}
            total_importe = 0

            for item in list(gastos) + list(rendiciones):
                concepto_2 = item.concepto_nivel_2.concepto_nombre if item.concepto_nivel_2 else "Sin Nivel 2"
                if concepto_2 not in grouped_data:
                    grouped_data[concepto_2] = []

                grouped_data[concepto_2].append({
                    'proveedor': item.nombre_proveedor.razon_social if hasattr(item, 'nombre_proveedor') and item.nombre_proveedor else (
                        item.proveedor.razon_social if hasattr(item, 'proveedor') and item.proveedor else 'Sin proveedor'
                    ),
                    'concepto': item.concepto_nivel_1.concepto_nombre if item.concepto_nivel_1 else 'Sin concepto',
                    'forma_pago': item.tipo_comprobante,
                    'importe': item.importe,
                    'fecha': item.fecha_gasto.strftime("%d/%m/%Y") if hasattr(item, 'fecha_gasto') and item.fecha_gasto else (
                        item.fecha_operacion.strftime("%d/%m/%Y") if item.fecha_operacion else 'Sin Fecha'
                    ),
                })
                total_importe += item.importe if item.importe else 0

            # Generar la fecha actual para el reporte
            fecha_actual = datetime.now().strftime("%d/%m/%Y")

            # Preparar los datos que se enviarán
            response_data = {
                'fecha': fecha_actual,
                'gastos_por_grupo': [
                    {'nivel_2': nivel_2, 'gastos': data}
                    for nivel_2, data in grouped_data.items()
                ],
                'total_importe': total_importe
            }

            return JsonResponse(response_data)

    except Exception as e:
        # Si ocurre un error, captura la excepción y retorna un error 500 con detalles
        return JsonResponse({'error': f'Ocurrió un error al generar el reporte: {str(e)}'}, status=500)



def guardar_proveedor(request):
    if request.method == 'POST':
        ruc_dni = request.POST.get('ruc_dni')
        razon_social = request.POST.get('razon_social')
        nombre_comercial = request.POST.get('nombre_comercial', '').strip() or None
        telefono = request.POST.get('telefono')
        nombre_contacto = request.POST.get('nombre_contacto')

        # Validar campos obligatorios
        if not ruc_dni or not razon_social:
            messages.error(request, 'RUC/DNI y Razón Social son obligatorios.')
            return redirect('proveedores')

        try:
            Proveedor.objects.create(
                ruc_dni=ruc_dni,
                razon_social=razon_social,
                nombre_comercial=nombre_comercial,
                telefono=telefono,
                nombre_contacto=nombre_contacto,
            )
            messages.success(request, 'Proveedor agregado exitosamente.')
        except ValidationError as e:
            messages.error(request, f'Error al guardar el proveedor: {e}')
        except Exception as e:
            messages.error(request, 'Ocurrió un error inesperado al agregar el proveedor.')

    return redirect('proveedores')


def guardar_cuenta_bancaria(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        proveedor_id = request.POST.get('proveedor_id')
        nombre_banco = request.POST.get('nombre_banco')
        numero_cuenta = request.POST.get('numero_cuenta')
        tipo_cuenta = request.POST.get('tipo_cuenta')
        cci = request.POST.get('cci', '').strip() or None  # Obtener el CCI del formulario

        try:
            # Obtener el proveedor al que se asociará la cuenta bancaria
            proveedor = Proveedor.objects.get(id=proveedor_id)

            # Crear la nueva cuenta bancaria
            cuenta_bancaria = CuentaBancaria(
                proveedor=proveedor,
                nombre_banco=nombre_banco,
                numero_cuenta=numero_cuenta,
                tipo_cuenta=tipo_cuenta,
                cci=cci  # Guardar el CCI
            )
            cuenta_bancaria.save()

            # Mensaje de éxito
            messages.success(request, f'La cuenta bancaria para {proveedor.razon_social} se ha guardado correctamente.')

        except Proveedor.DoesNotExist:
            messages.error(request, 'El proveedor especificado no existe.')
        except Exception as e:
            messages.error(request, f'Error al guardar la cuenta bancaria: {e}')

        # Redirigir a la página de proveedores o a la lista que prefieras
        return redirect('proveedores')

    return HttpResponse(status=405)  # Método no permitido si no es un POST



def editar_proveedor(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('id')
        ruc_dni = request.POST.get('ruc_dni')
        razon_social = request.POST.get('razon_social')
        nombre_comercial = request.POST.get('nombre_comercial', '').strip() or None
        telefono = request.POST.get('telefono')
        nombre_contacto = request.POST.get('nombre_contacto')

        # Obtener el proveedor existente
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)

        # Validar campos obligatorios
        if not ruc_dni or not razon_social:
            messages.error(request, 'RUC/DNI y Razón Social son obligatorios.')
            return redirect('proveedores')

        try:
            proveedor.ruc_dni = ruc_dni
            proveedor.razon_social = razon_social
            proveedor.nombre_comercial = nombre_comercial
            proveedor.telefono = telefono
            proveedor.nombre_contacto = nombre_contacto
            proveedor.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
        except ValidationError as e:
            messages.error(request, f'Error al actualizar el proveedor: {e}')
        except Exception as e:
            messages.error(request, 'Ocurrió un error inesperado al actualizar el proveedor.')

    return redirect('proveedores')


def logout_view(request):
    logout(request)
    return redirect('login')

def registrar_rendiciones(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)
    concepto_nivel_1 = Concepto.objects.filter(nivel=1)
    concepto_nivel_2 = Concepto.objects.filter(nivel=2)
    concepto_nivel_3 = Concepto.objects.filter(nivel=3)
    proveedores = Proveedor.objects.all()  # Obtener todos los proveedores

    return render(request, 'gastosRendiciones.html', {
        'gasto': gasto,
        'conceptos_nivel_1': concepto_nivel_1,
        'conceptos_nivel_2': concepto_nivel_2,
        'conceptos_nivel_3': concepto_nivel_3,
        'proveedores': proveedores,  # Pasar proveedores al template
    })





def obtener_saldo_inicial_manual(fecha_inicio, usuario=None):
    dias_busqueda = 5  # Máximo de días para retroceder
    fecha_actual = fecha_inicio - timedelta(days=1)  # Comenzar con el día anterior al rango

    saldo_final = Decimal(0.00)

    for _ in range(dias_busqueda):
        # Filtrar los ingresos y gastos hasta la fecha actual
        ingresos = Ingreso.objects.filter(fecha_ingreso__lte=fecha_actual)
        gastos = Gasto.objects.filter(fecha_gasto__lte=fecha_actual)

        if usuario:  # Si se proporciona un usuario, filtrar por el creador
            ingresos = ingresos.filter(usuario_creador=usuario)
            gastos = gastos.filter(usuario_creador=usuario)

        # Calcular la suma total de ingresos y gastos
        total_ingresos = ingresos.aggregate(total=Sum('importe'))['total'] or Decimal(0.00)
        total_gastos = gastos.aggregate(total=Sum('importe'))['total'] or Decimal(0.00)

        saldo_final = total_ingresos - total_gastos

        # Si encontramos datos significativos (saldo no nulo), devolvemos el saldo calculado
        if saldo_final != 0:
            return saldo_final

        # Retroceder un día más
        fecha_actual -= timedelta(days=1)

    # Si no se encontró saldo en el rango permitido, retornar 0
    return Decimal(0.00)

def actualizar_movimiento(request):
    if request.method == 'POST':
        gasto_id = request.POST.get('id')
        observacion = request.POST.get('notas')

        # Buscar el gasto
        gasto = get_object_or_404(Gasto, id=gasto_id)

        # Actualizar la observación
        gasto.observacion = observacion
        gasto.save()

        # Mensaje de éxito con el ID del gasto actualizado
        messages.success(request, f"Se actualizó la observación del gasto con ID {gasto.id}.")

        return redirect('caja_chica')  # Cambia 'caja' por la vista a la que debe redirigir
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def descargar_excel(request):
    hoy = date.today().strftime('%Y-%m-%d')  # Formato para los campos de tipo date
    fecha_inicio = request.GET.get('fecha_inicio', hoy)
    fecha_fin = request.GET.get('fecha_fin', hoy)
    fecha_inicio = date.fromisoformat(fecha_inicio)
    fecha_fin = date.fromisoformat(fecha_fin)
    saldo_base = Decimal(0)
    try:
        saldo_inicial = SaldoInicial.objects.get(usuario=request.user)
        saldo_base = saldo_inicial.monto_saldo_inicial
    except SaldoInicial.DoesNotExist:
        saldo_base = Decimal('0.00')  # Si no tiene saldo inicial, asignar 0
    saldo_inicial = obtener_saldo_inicial_manual(fecha_inicio, usuario=request.user if not request.user.is_staff else None)
    # Sumar el saldo base al saldo inicial
    saldo_inicial += saldo_base
    if request.user.is_staff:
        # Staff puede ver todos los ingresos y gastos
        ingresos = Ingreso.objects.filter(
            fecha_ingreso__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user  # Filtra solo los ingresos creados por el usuario staff
        )
        gastos = Gasto.objects.filter(fecha_gasto__range=[fecha_inicio, fecha_fin])
    else:
        # No staff solo puede ver los ingresos y gastos que creó
        ingresos = Ingreso.objects.filter(
            fecha_ingreso__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user
        )
        gastos = Gasto.objects.filter(
            fecha_gasto__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user
        )
    movimientos = []
    for ingreso in ingresos:
        nombre_fondo = ingreso.id_fondo.nombre_fondo if ingreso.id_fondo else 'Sin nombre'
        tipo = 'Extorno' if ingreso.extorno else 'Ingreso'
        banco_nombre = ingreso.banco.nombre if ingreso.banco else ''
        codigo_operacion = ingreso.codigo_operacion or ''
        fecha_operacion = ingreso.fecha_operacion.strftime('%d/%m/%Y') if ingreso.fecha_operacion else ''

        movimientos.append({
            'tipo': tipo,
            'fecha': ingreso.fecha_ingreso.strftime('%-d/%-m/%Y'),
            'metodo_pago': ingreso.metodo_pago,
            'concepto': nombre_fondo,
            'proveedor': ingreso.id_fondo.nombre_fondo,
            'banco': banco_nombre,
            'codigo_operacion': codigo_operacion,
            'fecha_operacion': fecha_operacion,
            'notas': ingreso.observacion or '',
            'monto': Decimal(ingreso.importe)
        })
    for gasto in gastos:
        if gasto.concepto_nivel_3:
            concepto = gasto.concepto_nivel_3.concepto_nombre
        elif gasto.concepto_nivel_2:
            concepto = gasto.concepto_nivel_2.concepto_nombre
        elif gasto.concepto_nivel_1:
            concepto = gasto.concepto_nivel_1.concepto_nombre
        else:
            if gasto.id_requerimiento and gasto.num_requerimiento:
                concepto = f"REQ N°{gasto.num_requerimiento} (Id={gasto.id_requerimiento})"
            else:
                concepto = gasto.tipo_comprobante or ''
        banco_nombre = gasto.banco.nombre if gasto.banco else ''
        codigo_operacion = gasto.codigo_operacion or ''
        fecha_operacion = gasto.fecha_operacion.strftime('%d/%m/%Y') if gasto.fecha_operacion else ''
        movimientos.append({
            'tipo': 'Gasto',
            'fecha': gasto.fecha_gasto.strftime('%-d/%-m/%Y'),
            'metodo_pago': gasto.tipo_pago,
            'concepto': concepto,
            'proveedor': gasto.nombre_proveedor.razon_social,
            'banco': banco_nombre,
            'codigo_operacion': codigo_operacion,
            'fecha_operacion': fecha_operacion,
            'notas': gasto.observacion or '',
            'monto': Decimal(gasto.importe)
        })
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="movimientos_{fecha_inicio}_a_{fecha_fin}.xlsx"'
    wb = Workbook()
    ws = wb.active
    titulo = f"Movimientos de {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    ws.append([titulo])
    ws.append([])  # Línea vacía
    ws.append([f'Saldo inicial: {saldo_inicial:,.2f}'])
    ws.append([])  # Línea vacía
    encabezados = ['Tipo', 'Fecha', 'Método de Pago', 'Concepto', 'Proveedor', 'Banco', 'Código de Operación', 'Fecha de Operación', 'Monto', 'Notas']
    for col_num, header in enumerate(encabezados, 1):  # Comienza en la columna A
        cell = ws.cell(row=5, column=col_num, value=header)
        cell.font = Font(bold=True)
    row_num = 6
    for movimiento in movimientos:
        ws.cell(row=row_num, column=1, value=movimiento['tipo'])
        ws.cell(row=row_num, column=2, value=movimiento['fecha'])
        ws.cell(row=row_num, column=3, value=movimiento['metodo_pago'])
        ws.cell(row=row_num, column=4, value=movimiento['concepto'])
        ws.cell(row=row_num, column=5, value=movimiento['proveedor'])
        ws.cell(row=row_num, column=6, value=movimiento['banco'])
        ws.cell(row=row_num, column=7, value=movimiento['codigo_operacion'])
        ws.cell(row=row_num, column=8, value=movimiento['fecha_operacion'])
        ws.cell(row=row_num, column=9, value=movimiento['monto'])
        ws.cell(row=row_num, column=10, value=movimiento['notas'])
        row_num += 1
    ws.append([])  # Línea vacía
    saldo_final = saldo_inicial + sum(m["monto"] for m in movimientos if m["tipo"] in ["Ingreso", "Extorno"]) - sum(m["monto"] for m in movimientos if m["tipo"] == "Gasto")
    ws.append([f'Saldo final: {saldo_final:,.2f}'])

    for col in range(1, 11):  # Ajustamos para que empiece en la columna A
        max_length = 0
        for row in ws.iter_rows(min_col=col, max_col=col):
            for cell in row:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[chr(64 + col)].width = adjusted_width
    wb.save(response)
    return response

@login_required
def caja_chica(request):
    hoy = date.today().strftime('%Y-%m-%d')  # Formato para los campos de tipo date

    # Obtener las fechas de los parámetros GET, si no están presentes usar la fecha de hoy
    fecha_inicio = request.GET.get('fecha_inicio', hoy)
    fecha_fin = request.GET.get('fecha_fin', hoy)

    # Convertir las fechas a tipo date
    fecha_inicio = date.fromisoformat(fecha_inicio)
    fecha_fin = date.fromisoformat(fecha_fin)

    # Calcular el saldo base según el username del usuario autenticado
    saldo_base = Decimal(0)
    try:
        saldo_inicial = SaldoInicial.objects.get(usuario=request.user)
        saldo_base = saldo_inicial.monto_saldo_inicial
    except SaldoInicial.DoesNotExist:
        saldo_base = Decimal('0.00')  # Si no tiene saldo inicial, asignar 0

    # Calcular el saldo inicial usando la función personalizada
    saldo_inicial = obtener_saldo_inicial_manual(fecha_inicio, usuario=request.user if not request.user.is_staff else None)
    # Sumar el saldo base al saldo inicial
    saldo_inicial += saldo_base
    saldo_efectivo = 0
    saldo_banco = 0
    if not request.user.is_staff:
        # Filtrar los ingresos y gastos del usuario autenticado sin límite de fechas
        ingresos = Ingreso.objects.filter(usuario_creador=request.user)
        gastos = Gasto.objects.filter(usuario_creador=request.user)

        # Calcular saldo efectivo y saldo banco para el usuario no staff
        saldo_efectivo = sum(ingreso.importe for ingreso in ingresos if ingreso.metodo_pago == 'efectivo') - sum(gasto.importe for gasto in gastos if gasto.tipo_pago == 'efectivo')
        saldo_banco = sum(ingreso.importe for ingreso in ingresos if ingreso.metodo_pago != 'efectivo') - sum(gasto.importe for gasto in gastos if gasto.tipo_pago != 'efectivo')


    # Verificar si el usuario es staff
    if request.user.is_staff:
        # Staff puede ver todos los ingresos y gastos
        ingresos = Ingreso.objects.filter(
            fecha_ingreso__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user  # Filtra solo los ingresos creados por el usuario staff
        )
        gastos = Gasto.objects.filter(fecha_gasto__range=[fecha_inicio, fecha_fin])
    else:
        # No staff solo puede ver los ingresos y gastos que creó
        ingresos = Ingreso.objects.filter(
            fecha_ingreso__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user
        )
        gastos = Gasto.objects.filter(
            fecha_gasto__range=[fecha_inicio, fecha_fin],
            usuario_creador=request.user
        )

    # Preparar los movimientos para la tabla
    movimientos = []

    # Procesar ingresos
    for ingreso in ingresos:
        nombre_fondo = ingreso.id_fondo.nombre_fondo if ingreso.id_fondo else 'Sin nombre'
        tipo = 'Extorno' if ingreso.extorno else 'Ingreso'
        movimientos.append({
            'id': ingreso.id,
            'tipo': tipo,
            'fecha': ingreso.fecha_ingreso.strftime('%-d/%-m/%Y'),
            'metodo_pago': ingreso.metodo_pago,
            'concepto': ingreso.local.nombre_local if ingreso.local else "sin local asignado",
            'notas': ingreso.observacion or '',
            'monto': Decimal(ingreso.importe),
            'moneda': ingreso.moneda,
            'proveedor': ingreso.id_fondo.nombre_fondo if ingreso.id_fondo else "Sin fondo especifico",
            'usuario_creador': ingreso.usuario_creador.username if ingreso.usuario_creador else "Desconocido"
        })

    # Procesar gastos
    for gasto in gastos:
        if gasto.concepto_nivel_3:
            concepto = gasto.concepto_nivel_3.concepto_nombre
        elif gasto.concepto_nivel_2:
            concepto = gasto.concepto_nivel_2.concepto_nombre
        elif gasto.concepto_nivel_1:
            concepto = gasto.concepto_nivel_1.concepto_nombre
        else:
            if gasto.id_requerimiento and gasto.num_requerimiento:
                concepto = f"REQ N°{gasto.num_requerimiento} (Id={gasto.id_requerimiento})"
            else:
                concepto = gasto.tipo_comprobante or ''
        total_rendido = sum(rendicion.importe for rendicion in gasto.rendiciones_gasto.all())

        movimientos.append({
            'id': gasto.id,
            'tipo': 'Gasto',
            'fecha': gasto.fecha_gasto.strftime('%-d/%-m/%Y'),
            'metodo_pago': gasto.tipo_pago,
            'concepto': concepto,
            'notas': gasto.observacion or '',
            'monto': Decimal(gasto.importe),
            'rendido': gasto.rendido,
            'moneda': gasto.moneda,
            'proveedor': gasto.nombre_proveedor.razon_social,
            'rendiciones': list(gasto.rendiciones_gasto.all()),
            'total_rendido': total_rendido,  # ✅ Agregar el total de rendiciones
            'usuario_creador': gasto.usuario_creador.username
        })

    # Cálculos para los totales
    total_ingresos_soles = sum(m['monto'] for m in movimientos if m['tipo'] != 'Gasto' and m['moneda'] == 'Soles')
    total_egresos_soles = sum(m['monto'] for m in movimientos if m['tipo'] == 'Gasto' and m['moneda'] == 'Soles')
    saldo_final = saldo_inicial + total_ingresos_soles - total_egresos_soles

    # Generar el título para las fechas seleccionadas
    rango_fechas = f"{fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"

    # Contexto para la plantilla
    context = {
        'movimientos': movimientos,
        'fecha_hoy': hoy,  # Pasar la fecha actual
        'saldo_inicial': saldo_inicial,
        'total_ingresos_soles': total_ingresos_soles,
        'total_egresos_soles': total_egresos_soles,
        'saldo_final': saldo_final,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'rango_fechas': rango_fechas,
        'saldo_efectivo': saldo_efectivo,
        'saldo_banco': saldo_banco,
    }

    return render(request, 'caja.html', context)




def cuentas_bancarias(request, proveedor_id):
    proveedor = Proveedor.objects.get(id=proveedor_id)
    cuentas = CuentaBancaria.objects.filter(proveedor_id=proveedor_id)
    cuentas_data = [{
        'nombre_banco': cuenta.nombre_banco,
        'numero_cuenta': cuenta.numero_cuenta,
        'tipo_cuenta': cuenta.get_tipo_cuenta_display(),
        'cci': cuenta.cci,
    } for cuenta in cuentas]
    return JsonResponse({'proveedor': proveedor.razon_social, 'cuentas': cuentas_data})


def prueba(request):
    return render(request, 'prueba.html')
@login_required
def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores.html', {'proveedores': proveedores})
@login_required
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado exitosamente.')
    return redirect('proveedores')


def validar_campos(metodo_pago, data):
    if metodo_pago != "efectivo":
        if not data.get("codigo_operacion"):
            return "El código de operación es obligatorio."
        if not data.get("fecha_operacion"):
            return "La fecha de operación es obligatoria."
        if not data.get("banco_operacion"):
            return "El banco es obligatorio."
    return None

@login_required
@csrf_exempt
def editar_ingreso(request, id):
    ingreso = get_object_or_404(Ingreso, id=id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"message": "Datos JSON inválidos."}, status=400)

        metodo_pago = data.get("metodo_pago")
        error_msg = validar_campos(metodo_pago, data)
        if error_msg:
            return JsonResponse({"message": error_msg}, status=400)

        ingreso.id_fondo = get_object_or_404(Fondo, id=data['id_fondo'])
        ingreso.metodo_pago = metodo_pago
        ingreso.local = get_object_or_404(Local, id=data['local'])

        # Solo asignar codigo_operacion, fecha_operacion y banco si el metodo_pago no es "efectivo"
        if metodo_pago != "efectivo":
            ingreso.codigo_operacion = data.get('codigo_operacion')
            ingreso.fecha_operacion = data.get('fecha_operacion')
            ingreso.banco = get_object_or_404(Banco, id=data['banco_operacion']) if data.get('banco_operacion') else None

        ingreso.observacion = data['observacion']
        ingreso.save()

        return JsonResponse({"message": "El ingreso ha sido actualizado exitosamente."}, status=200)

    return JsonResponse({"message": "Método no permitido"}, status=405)


@login_required
def edit_item(request, id, tipo):
    nivel_1_conceptos = Concepto.objects.filter(nivel=1)
    nivel_2_conceptos = Concepto.objects.filter(nivel=2)
    nivel_3_conceptos = Concepto.objects.filter(nivel=3)
    fondos = Fondo.objects.all()
    locales = Local.objects.all()
    bancos = Banco.objects.all()
    if tipo == 'Extorno':
        ingreso = get_object_or_404(Ingreso, id=id)
                # Convertir importe a cadena con punto decimal
        if ingreso.importe is not None:
            ingreso.importe = f"{float(ingreso.importe):.2f}"
        return render(request, 'edit_ingreso.html', {'ingreso': ingreso,
                    'fondos': fondos,
                    'bancos':bancos,
        'locales': locales,
        })
    elif tipo == 'Gasto':
        gasto = get_object_or_404(Gasto, id=id)

        # Convertir importe a cadena con punto decimal
        if gasto.importe is not None:
            gasto.importe = f"{float(gasto.importe):.2f}"

        return render(request, 'edit_gasto.html', {'gasto': gasto,
                    'nivel_1_conceptos': nivel_1_conceptos,
        'nivel_2_conceptos': nivel_2_conceptos,
        'nivel_3_conceptos': nivel_3_conceptos,
        'fondos': fondos,
        'locales': locales,
        })
def buscar_proveedores(request):
    search_term = request.GET.get('search', '')
    proveedores = Proveedor.objects.filter(
        razon_social__icontains=search_term
    ) | Proveedor.objects.filter(
        nombre_comercial__icontains=search_term
    )
    data = [
        {
            "id": proveedor.id,
            "razon_social": proveedor.razon_social,
            "nombre_comercial": proveedor.nombre_comercial,
        }
        for proveedor in proveedores
    ]
    return JsonResponse(data, safe=False)

def registrar_gasto(request, id):
    gasto = get_object_or_404(Gasto, id=id)

    if request.method == "POST":
        try:
            # Actualizar los campos con los valores enviados por el formulario
            gasto.tipo_pago = request.POST.get('metodo_pago')
            gasto.concepto_nivel_1_id = request.POST.get('concepto_nivel_1_results') or None
            gasto.concepto_nivel_2_id = request.POST.get('concepto_nivel_2_results') or None
            gasto.concepto_nivel_3_id = request.POST.get('concepto_nivel_3_results') or None
            gasto.nombre_proveedor = request.POST.get('nombre_proveedor', '').strip()
            local_id = request.POST.get('local')

            gasto.importe = request.POST.get('importe') or 0
            gasto.observacion = request.POST.get('observacion', '')
            if gasto.tipo_pago in ['transferencia', 'yape']:
                gasto.codigo_operacion = request.POST.get('codigo_operacion', '').strip()
                gasto.fecha_operacion = request.POST.get('fecha_operacion') or None
            # Obtener y asignar el local seleccionado
            if local_id:
                gasto.local_id = local_id
            gasto.usuario_creador = request.user

            gasto.save()

            # Mensaje de éxito
            messages.success(request, "Gasto registrado correctamente.")
            return redirect('caja_chica')  # Redirigir a la URL caja_chica

        except Exception as e:
            messages.error(request, f"Ocurrió un error al registrar el gasto: {str(e)}")
            return redirect('gasto_edit', id=id)  # Redirige al formulario original en caso de error

    return redirect('gasto_edit', id=id)

def gasto_edit(request, id):
    gasto = get_object_or_404(Gasto, id=id)

    if request.method == "POST":
        try:
            # Actualizar los campos con los valores enviados por el formulario
            gasto.tipo_pago = request.POST.get('metodo_pago')
            gasto.concepto_nivel_1_id = request.POST.get('concepto_nivel_1_results') or None
            gasto.concepto_nivel_2_id = request.POST.get('concepto_nivel_2_results') or None
            gasto.concepto_nivel_3_id = request.POST.get('concepto_nivel_3_results') or None
            gasto.importe = request.POST.get('importe') or 0
            gasto.observacion = request.POST.get('observacion', '')
            gasto.fecha_operacion = request.POST.get('fecha_operacion') or None
            gasto.codigo_operacion = request.POST.get('codigo_operacion', '')

            # Guardar los cambios en la base de datos
            gasto.save()

            # Mensaje de éxito
            messages.success(request, "Gasto registrado correctamente.")
            return redirect('caja_chica')  # Redirigir a la URL caja_chica

        except Exception as e:
            # Mensaje de error
            messages.error(request, f"Ocurrió un error al registrar el gasto: {str(e)}")
            return redirect('gasto_edit', id=id)  # Redirige al mismo formulario en caso de error

    # Renderizar el formulario con los datos actuales del gasto
    return render(request, 'edit_gasto.html', {
        'gasto': gasto,
        'nivel_1_conceptos': Concepto.objects.filter(nivel=1),  # Asumiendo una estructura de niveles
        'nivel_2_conceptos': Concepto.objects.filter(nivel=2),
        'nivel_3_conceptos': Concepto.objects.filter(nivel=3),
        'locales': Local.objects.all(),
    })


from django.urls import reverse

def guardar_oficial(request):
    if request.method == "POST":
        try:
            # Parsear el cuerpo de la solicitud como JSON
            body = json.loads(request.body)
            rendiciones = body.get('rendiciones', [])
            gasto_id = body.get('gasto_id')  # ID del gasto recibido

            # Obtener el gasto asociado
            gasto = Gasto.objects.get(id=gasto_id)

            # Procesar los datos recibidos
            data_guardada = []
            suma_importes_rendiciones = Decimal(0)  # Acumulador para la suma de los importes de las rendiciones
            mensaje_creacion = None  # Variable para guardar el mensaje de creación

            for rendicion in rendiciones:
                fecha_operacion = rendicion.get('fecha_operacion')
                proveedor = rendicion.get('apellidos_nombres_proveedor')
                numero_requerimiento = rendicion.get('numero_requerimiento')
                descripcion=rendicion.get('descripcion')
                importe = Decimal(rendicion.get('importe', 0))
                concepto_nivel_1_id = rendicion.get('concepto_nivel_1')
                concepto_nivel_2_id = rendicion.get('concepto_nivel_2')
                concepto_nivel_3_id = rendicion.get('concepto_nivel_3')
                tipo_comprobante = rendicion.get('tipo_comprobante')  # Captura del tipo de comprobante

                proveedor = Proveedor.objects.get(id=proveedor)  # Buscar proveedor por ID

                # Crear y guardar objeto Rendicion
                nueva_rendicion = Rendicion(
                    fecha_operacion=fecha_operacion,
                    proveedor=proveedor ,
                    numero_requerimiento=numero_requerimiento,
                    importe=importe,
                    descripcion=descripcion,
                    concepto_nivel_1_id=concepto_nivel_1_id,
                    concepto_nivel_2_id=concepto_nivel_2_id,
                    concepto_nivel_3_id=concepto_nivel_3_id,
                    tipo_comprobante=tipo_comprobante,  # Guardar el tipo de comprobante
                    gasto_id=gasto_id  # Asociar el gasto
                )
                nueva_rendicion.usuario_creador = request.user
                nueva_rendicion.save()

                suma_importes_rendiciones += importe

                data_guardada.append({
                    "id": nueva_rendicion.id,
                    "fecha_operacion": nueva_rendicion.fecha_operacion,
                    "descripcion":nueva_rendicion.descripcion,
                    "proveedor": nueva_rendicion.proveedor,
                    "numero_requerimiento": nueva_rendicion.numero_requerimiento,
                    "importe": nueva_rendicion.importe,
                    "tipo_comprobante": nueva_rendicion.tipo_comprobante,  # Incluir en la respuesta

                })

            # Comparar la suma de los importes de las rendiciones con el importe del gasto
            if suma_importes_rendiciones > gasto.importe:
                # Crear un nuevo gasto por la diferencia
                diferencia = suma_importes_rendiciones - gasto.importe
                nuevo_gasto = Gasto(
                    importe=diferencia,
                    fecha_registro=date.today(),
                    fecha_gasto=date.today(),
                    moneda=gasto.moneda,  # Moneda por defecto del gasto asociado
                    tipo_comprobante=gasto.tipo_comprobante,
                    campo_area=gasto.campo_area,
                    num_requerimiento=gasto.num_requerimiento,
                    id_requerimiento=gasto.id_requerimiento,
                    nombre_proveedor=gasto.nombre_proveedor,
                    local=gasto.local,
                    tipo_pago="efectivo",
                    gasto_origen=gasto,  # Vincular con el gasto original


                )
                nuevo_gasto.usuario_creador = request.user

                nuevo_gasto.save()
                mensaje_creacion = f"Se creó un nuevo gasto con un importe de {diferencia} y moneda {gasto.moneda}."

            elif suma_importes_rendiciones < gasto.importe:
                # Crear un nuevo ingreso por la diferencia
                diferencia = gasto.importe - suma_importes_rendiciones
                nuevo_ingreso = Ingreso(
                    fecha_registro=date.today(),
                    fecha_ingreso=date.today(),
                    importe=diferencia,
                    metodo_pago="Sin especificar",
                    moneda=gasto.moneda,  # Moneda por defecto del gasto asociado
                    extorno=True,
                    observacion="gasto extra generado",
                    gasto_origen=gasto  # Vincular con el gasto original

                )
                nuevo_ingreso.usuario_creador=request.user
                nuevo_ingreso.save()
                mensaje_creacion = f"Se creó un nuevo ingreso con un importe de {diferencia} y moneda {gasto.moneda}."

            # Actualizar el campo 'rendido' del gasto asociado
            gasto.rendido = True
            gasto.save()

            # Responder con JSON
            response_data = {
                'status': 'success',
                'message': 'Rendiciones guardadas exitosamente.',
                'detalle': mensaje_creacion,
                'redirect_url': reverse('rendicion')
            }
            return JsonResponse(response_data)

        except Exception as e:
            response_data = {
                'status': 'error',
                'message': f"Error: {str(e)}"
            }
            return JsonResponse(response_data)
    else:
        return redirect('rendicion')




# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirige a la vista del dashboard
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'login.html')

from django.db.models.functions import TruncMonth


from django.http import JsonResponse
from django.db.models import Value
from django.db.models.functions import Coalesce

def calcular_gastos_por_metodo_pago(usuario):
    """
    Calcula la suma de los gastos agrupados por método de pago.
    Retorna un diccionario con etiquetas (métodos de pago) y valores (totales).
    Si el usuario es staff, se mostrarán todos los gastos.
    """
    # Si el usuario es staff, no filtramos por usuario_creador
    if usuario.is_staff:
        gastos_por_metodo = (
            Gasto.objects
            .values('tipo_pago')
            .annotate(total_gasto=Sum('importe'))
            .order_by('-total_gasto')
        )
    else:
        # Si no es staff, filtramos por usuario_creador
        gastos_por_metodo = (
            Gasto.objects
            .filter(usuario_creador=usuario)
            .values('tipo_pago')
            .annotate(total_gasto=Sum('importe'))
            .order_by('-total_gasto')
        )

    # Preparar datos para el gráfico
    etiquetas = [gasto['tipo_pago'] or 'Sin especificar' for gasto in gastos_por_metodo]
    valores = [float(gasto['total_gasto'] or 0) for gasto in gastos_por_metodo]

    return {
        'etiquetas': etiquetas,
        'valores': valores,
    }

@login_required
def dashboard_view(request):
    if request.user.is_authenticated:
        # Fecha actual
        today = date.today()
        current_year = today.year
        current_month = today.month

        # Si el usuario es staff, no filtramos los gastos por usuario_creador
        if request.user.is_staff:
            # Si es staff, no filtramos los gastos por usuario logueado
            gastos_filter = Gasto.objects
        else:
            # Si no es staff, filtramos los gastos por usuario_creador
            gastos_filter = Gasto.objects.filter(usuario_creador=request.user)

        # Los ingresos siempre se filtran por el usuario logueado, sin importar si es staff
        ingresos_filter = Ingreso.objects.filter(usuario_creador=request.user)

        # Obtener los 5 conceptos con más gasto (filtrar solo por los gastos, y si es staff ver todos)
        top_conceptos = (
            gastos_filter
            .annotate(concepto_nombre=Coalesce(
                'concepto_nivel_3__concepto_nombre',
                'concepto_nivel_2__concepto_nombre',
                'concepto_nivel_1__concepto_nombre',
                Value('Sin concepto'),
            ))
            .values('concepto_nombre')
            .annotate(total_gasto=Sum('importe'))
            .order_by('-total_gasto')[:5]
        )

        # Etiquetas y valores para el gráfico
        conceptos_labels = [entry['concepto_nombre'] for entry in top_conceptos]
        conceptos_data = [float(entry['total_gasto']) for entry in top_conceptos]

        # Obtener ingresos por mes para el gráfico de barras (solo mes actual) filtrado por usuario
        ingresos_mes_actual = ingresos_filter.filter(
            fecha_ingreso__year=current_year,
            fecha_ingreso__month=current_month
        )
        ingresos_mes_actual_total = ingresos_mes_actual.aggregate(total_ingresos=Sum('importe'))['total_ingresos'] or Decimal('0.00')

        # Obtener gastos por mes para el gráfico de barras (solo mes actual) filtrado por usuario o todos si es staff
        gastos_mes_actual = gastos_filter.filter(
            fecha_gasto__year=current_year,
            fecha_gasto__month=current_month
        )
        gastos_mes_actual_total = gastos_mes_actual.aggregate(total_gastos=Sum('importe'))['total_gastos'] or Decimal('0.00')

        # Obtener ingresos por mes para el gráfico de líneas (todo el año actual) filtrado por usuario
        ingresos_anuales = ingresos_filter.filter(
            fecha_ingreso__year=current_year
        ).annotate(month=TruncMonth('fecha_ingreso')).values('month').annotate(total_ingresos=Sum('importe')).order_by('month')

        # Obtener gastos por mes para el gráfico de líneas (todo el año actual) filtrado por usuario o todos si es staff
        gastos_anuales = gastos_filter.filter(
            fecha_gasto__year=current_year
        ).annotate(month=TruncMonth('fecha_gasto')).values('month').annotate(total_gastos=Sum('importe')).order_by('month')

        # Formatear los resultados para que sean más fáciles de usar en los gráficos
        ingresos_data = {entry['month'].strftime('%B %Y'): float(entry['total_ingresos'] or 0) for entry in ingresos_anuales}
        gastos_data = {entry['month'].strftime('%B %Y'): float(entry['total_gastos'] or 0) for entry in gastos_anuales}

        # Generar las etiquetas y los datos de los gráficos de líneas (para todo el año)
        labels_line = list(set(ingresos_data.keys()).union(gastos_data.keys()))
        ingresos_por_mes_line = [ingresos_data.get(label, 0) for label in labels_line]
        gastos_por_mes_line = [gastos_data.get(label, 0) for label in labels_line]

        # Para el gráfico de barras (solo mes actual)
        labels_bar = [today.strftime('%B %Y')]  # Solo el mes actual
        ingresos_por_mes_bar = [float(ingresos_mes_actual_total)]
        gastos_por_mes_bar = [float(gastos_mes_actual_total)]

        # Llamar a la función para calcular los gastos por método de pago (también filtrados por usuario)
        datos_gastos_metodo_pago = calcular_gastos_por_metodo_pago(request.user)

        # Enviar los datos a la plantilla
        data = {
            'labels_bar': labels_bar,
            'ingresos_por_mes_bar': ingresos_por_mes_bar,
            'gastos_por_mes_bar': gastos_por_mes_bar,
            'labels_line': labels_line,
            'ingresos_por_mes_line': ingresos_por_mes_line,
            'gastos_por_mes_line': gastos_por_mes_line,
            'conceptos_labels': conceptos_labels,
            'conceptos_data': conceptos_data,
            'datos_gastos_metodo_pago': datos_gastos_metodo_pago,
        }

        return render(request, 'dashboard.html', data)
    else:
        return redirect('login')





@login_required
def agregar_banco(request):
    if request.method == 'POST':
        nombre_banco = request.POST.get('nombre')

        # Verificar que se haya proporcionado un nombre
        if nombre_banco:
            # Crear un nuevo banco
            Banco.objects.create(nombre=nombre_banco)
            messages.success(request, 'Banco agregado exitosamente.')
        else:
            messages.error(request, 'El nombre del banco es obligatorio.')

        # Redirigir a la página de ingreso
        return redirect('ingreso')

def prestamos(request):
    if request.method == 'POST':
        try:
            fecha_prestamo = request.POST.get('fecha_prestamo')
            fecha_vencimiento = request.POST.get('fecha_vencimiento')
            numero_cuotas = request.POST.get('numero_cuotas')
            proveedor_id = request.POST.get('proveedor')
            tea = request.POST.get('tea')
            banco_id = request.POST.get('banco')
            analista = request.POST.get('analista')
            monto = request.POST.get('monto')
            estado = request.POST.get('estado')
            local_id = request.POST.get('local')
            dia_pago = request.POST.get('dia_pago')  # Recibimos el día de pago
            cuota_actual = request.POST.get('cuota_actual') if estado == "proceso" else None
            monto_cuota = request.POST.get('monto_cuota')

            # Validación de datos
            if not all([fecha_prestamo, fecha_vencimiento, numero_cuotas, tea, monto, estado, local_id, dia_pago]):
                messages.error(request, "Todos los campos son requeridos.")
                return redirect('crear_prestamo')

            numero_cuotas = int(numero_cuotas)
            tea = float(tea)
            monto = float(monto)
            cuota_actual = int(cuota_actual)
            dia_pago = int(dia_pago)  # Convertir a entero

            # Obtener proveedor, banco y local si existen
            proveedor = Proveedor.objects.get(id=proveedor_id) if proveedor_id else None
            banco = Banco.objects.get(id=banco_id) if banco_id else None
            local = Local.objects.get(id=local_id) if local_id else None

            # Crear el préstamo
            prestamo = Prestamo(
                fecha_prestamo=fecha_prestamo,
                fecha_vencimiento=fecha_vencimiento,
                numero_cuotas=numero_cuotas,
                proveedor=proveedor,
                tea=tea,
                banco=banco,
                analista=analista,
                monto=monto,
                estado=estado,
                cuota_actual=cuota_actual,
                local=local,
                dia_pago=dia_pago,  # Guardamos el día de pago
                monto_cuota=monto_cuota
            )
            prestamo.save()

            # Obtener el fondo con nombre 'Fondo Prestamo'
            fondo = Fondo.objects.filter(nombre_fondo="Fondo Prestamo").first()

            # Crear el ingreso automáticamente
            ingreso = Ingreso.objects.create(
                prestamo=prestamo,
                fecha_registro=now().date(),
                fecha_ingreso=now().date(),
                importe=monto,
                id_fondo=fondo,
                metodo_pago="efectivo",
                moneda="Soles",
                local=local,  # Se asigna el local
                observacion="Prestamo"
            )

            messages.success(request, "Préstamo e ingreso creados exitosamente.")
            return redirect('prestamos')  # Redirigir a la lista de préstamos

        except ValueError:
            messages.error(request, "Error en los datos ingresados. Verifica los valores numéricos.")
        except Proveedor.DoesNotExist:
            messages.error(request, "El proveedor seleccionado no existe.")
        except Banco.DoesNotExist:
            messages.error(request, "El banco seleccionado no existe.")
        except Local.DoesNotExist:
            messages.error(request, "El local seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

        return redirect('crear_prestamo')

    # Obtener proveedores, bancos y locales
    proveedores = Proveedor.objects.all()
    bancos = Banco.objects.all()
    locales = Local.objects.all()
    return render(request, 'crear_prestamos.html', {'proveedores': proveedores, 'bancos': bancos, 'locales': locales})

@login_required
def ingreso(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        importe = request.POST.get('importe')
        id_fondo = request.POST.get('id_fondo')
        metodo_pago = request.POST.get('metodo_pago')
        moneda = request.POST.get('moneda')
        local_id = request.POST.get('local')
        observacion = request.POST.get('observacion')
        codigo_operacion = request.POST.get('codigo_operacion') if metodo_pago != 'efectivo' else None
        fecha_operacion  = request.POST.get('fecha_operacion') if metodo_pago != 'efectivo' else None
        banco_id = request.POST.get('banco_operacion')  # Obtener el banco seleccionado

        banco = Banco.objects.get(id=banco_id) if banco_id else None

        # Validación básica
        if not (fecha and importe and id_fondo and metodo_pago and moneda):
            messages.error(request, "Todos los campos obligatorios deben completarse.")
            return redirect('ingreso')

        # Guardar el ingreso
        fondo = Fondo.objects.get(id=id_fondo)
        local = Local.objects.get(id=local_id) if local_id else None

        ingreso = Ingreso(
            fecha_ingreso=fecha,
            importe=importe,
            id_fondo=fondo,
            metodo_pago=metodo_pago,
            moneda=moneda,
            local=local,
            observacion=observacion,
            codigo_operacion=codigo_operacion,  # Ya está seguro para el caso de transferencia
            fecha_operacion=fecha_operacion,
            banco=banco  # Guardar el banco seleccionado

        )
        ingreso.usuario_creador=request.user
        ingreso.save()
        messages.success(request, "Ingreso registrado correctamente.")
        return redirect('ingreso')

    # Contexto para renderizar el formulario
    fondos = Fondo.objects.all()
    locales = Local.objects.all()
    bancos = Banco.objects.all()
    return render(request, 'ingreso.html', {'fondos': fondos, 'locales': locales,'bancos': bancos})

from datetime import datetime

def comprobar_conceptos(tipo_comprobante, concepto_nivel_1, concepto_nivel_2, concepto_nivel_3):
    # Validación jerárquica de los conceptos (excepto para tipo_comprobante "Requerimiento")
    if tipo_comprobante not in ['Requerimiento', 'Sin Requerimiento']:
        # Verifica si se proporcionó concepto_nivel_1
        if not concepto_nivel_1:
            return JsonResponse({'error': 'Debe seleccionar un concepto de nivel 1.'}, status=400)

        # Intenta obtener el concepto de nivel 1
        try:
            concepto_1 = Concepto.objects.get(id=concepto_nivel_1)
        except Concepto.DoesNotExist:
            return JsonResponse({'error': 'El concepto de nivel 1 especificado no existe.'}, status=404)

        # Si el nivel 1 tiene conceptos hijos, validar el nivel 2
        conceptos_nivel_2 = Concepto.objects.filter(id_concepto_padre=concepto_1)
        if conceptos_nivel_2.exists():
            # Verifica si se proporcionó concepto_nivel_2
            if not concepto_nivel_2:
                return JsonResponse({'error': 'Debe seleccionar un concepto de nivel 2 asociado al nivel 1.'}, status=400)

            try:
                concepto_2 = Concepto.objects.get(id=concepto_nivel_2)
            except Concepto.DoesNotExist:
                return JsonResponse({'error': 'El concepto de nivel 2 especificado no existe.'}, status=404)

            # Si el nivel 2 tiene conceptos hijos, validar el nivel 3
            conceptos_nivel_3 = Concepto.objects.filter(id_concepto_padre=concepto_2)
            if conceptos_nivel_3.exists():
                # Verifica si se proporcionó concepto_nivel_3
                if not concepto_nivel_3:
                    return JsonResponse({'error': 'Debe seleccionar un concepto de nivel 3 asociado al nivel 2.'}, status=400)

                try:
                    concepto_3 = Concepto.objects.get(id=concepto_nivel_3)
                except Concepto.DoesNotExist:
                    return JsonResponse({'error': 'El concepto de nivel 3 especificado no existe.'}, status=404)
            else:
                concepto_3 = None  # No hay nivel 3 asociado
        else:
            concepto_2 = None  # No hay nivel 2 asociado
            concepto_3 = None  # No hay nivel 3 asociado
    else:
        # Si el tipo de comprobante es "Requerimiento", los conceptos pueden ser vacíos
        concepto_1 = None
        concepto_2 = None
        concepto_3 = None

    # Retornar los conceptos validados
    return {
        'concepto_nivel_1': concepto_1,
        'concepto_nivel_2': concepto_2,
        'concepto_nivel_3': concepto_3,
    }

@login_required
def gasto(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Captura de datos del request
            fecha = data.get('fecha')
            importe = data.get('importe')
            metodo_pago = data.get('metodo_pago')
            moneda = data.get('moneda')
            local_id = data.get('local')
            tipo_comprobante = data.get('tipo_comprobante')
            nombre_proveedor = data.get('nombre_proveedor')
            observacion = data.get('observacion')
            codigo_operacion = data.get('codigo_operacion') if metodo_pago != 'efectivo' or tipo_comprobante == 'Deposito en cuenta' else None
            fecha_operacion = data.get('fecha_operacion') if metodo_pago != 'efectivo' or tipo_comprobante == 'Deposito en cuenta' else None
            concepto_nivel_1 = data.get('concepto_nivel_1')
            concepto_nivel_2 = data.get('concepto_nivel_2')
            concepto_nivel_3 = data.get('concepto_nivel_3')
            numero_comprobante = data.get('num_comprobante')
            fecha_emision_comprobante = data.get('fecha_emision_comprobante') if tipo_comprobante  in ['RHE', 'Factura', 'Boleta'] else None # Nuevo campo
            campo_area=data.get('campo_area')
            campo_mes=data.get('campo_mes') if tipo_comprobante  in ['Boleta de pago'] else None
            id_requerimiento = data.get('id_requerimiento')  # Nuevo campo
            num_requerimiento = data.get('num_requerimiento')  # Nuevo campo
            banco_id =data.get('banco_operacion') if tipo_comprobante == 'Deposito en cuenta' else None
            # Buscar la instancia del banco si 'banco_id' no es None
            if banco_id:
                try:
                    banco = Banco.objects.get(id=banco_id)  # Buscar la instancia del banco por ID
                except Banco.DoesNotExist:
                    return JsonResponse({'error': 'El banco especificado no existe.'}, status=404)
            else:
                banco = None

            if fecha:
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'error': 'El valor de "fecha" tiene un formato inválido. Debería estar en el formato YYYY-MM-DD.'}, status=400)

            # Validación y conversión de fechas

            # Validación básica de campos obligatorios
            if not (fecha and importe and metodo_pago and moneda):
                return JsonResponse({'error': 'Todos los campos obligatorios deben completarse.'}, status=400)

            # Validación adicional para tipo_comprobante específico
            if tipo_comprobante in ['RHE', 'Factura', 'Boleta']:
                if not numero_comprobante or not fecha_emision_comprobante:
                    return JsonResponse({
                        'error': 'Los campos "Número de Comprobante" y "Fecha de Emisión del Comprobante" son obligatorios para el tipo de comprobante seleccionado.'
                    }, status=400)
            if tipo_comprobante == 'Boleta de pago':
                if not campo_mes:
                    return JsonResponse({
                        'error': 'El campo "Mes" es obligatorio cuando el tipo de comprobante es "Boleta de pago".'
                    }, status=400)
            # Validación adicional para tipo_comprobante "Requerimiento"
            if tipo_comprobante == 'Requerimiento':
                if not id_requerimiento:
                    return JsonResponse({
                        'error': 'El campo "ID Requerimiento" es obligatorio cuando el tipo de comprobante es "Requerimiento".'
                    }, status=400)
            # Buscar el proveedor por nombre (asumido que es único)
            proveedor = Proveedor.objects.filter(id=nombre_proveedor).first()
            if not proveedor:
                return JsonResponse({'error': 'El proveedor especificado no existe.'}, status=404)

            # Obtener el local
            local = Local.objects.get(id=local_id) if local_id else None

            # Validar conceptos usando la función
            resultado_conceptos = comprobar_conceptos(tipo_comprobante, concepto_nivel_1, concepto_nivel_2, concepto_nivel_3)

            if 'error' in resultado_conceptos:
                return JsonResponse({'error': 'Revise los niveles de los conceptos, falta llenar algunos campos.'}, status=400)

            # Extraer los conceptos validados
            concepto_1 = resultado_conceptos['concepto_nivel_1']
            concepto_2 = resultado_conceptos['concepto_nivel_2']
            concepto_3 = resultado_conceptos['concepto_nivel_3']

            # Crear y guardar la instancia del gasto
            gasto = Gasto(
                fecha_gasto=fecha,
                concepto_nivel_1=concepto_1,
                concepto_nivel_2=concepto_2,
                concepto_nivel_3=concepto_3,
                importe=importe,
                nombre_proveedor=proveedor,
                local=local,
                tipo_comprobante=tipo_comprobante,
                tipo_pago=metodo_pago,
                codigo_operacion=codigo_operacion,
                observacion=observacion,
                fecha_operacion=fecha_operacion,
                moneda=moneda,
                numero_comprobante=numero_comprobante,
                fecha_emision_comprobante=fecha_emision_comprobante,
                campo_area=campo_area,
                campo_mes=campo_mes,
                id_requerimiento=id_requerimiento if tipo_comprobante == 'Requerimiento' else None ,
                num_requerimiento=num_requerimiento if tipo_comprobante == 'Requerimiento' else None,
                banco=banco  # Asignamos la instancia del banco si existe


            )
            gasto.usuario_creador = request.user

            gasto.save()

            return JsonResponse({'success': 'Gasto registrado correctamente.'}, status=200)

        except Local.DoesNotExist:
            return JsonResponse({'error': 'El local seleccionado no existe.'}, status=404)
        except Concepto.DoesNotExist:
            return JsonResponse({'error': 'Alguno de los conceptos seleccionados no existe.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)

    nivel_1_conceptos = Concepto.objects.filter(nivel=1)
    nivel_2_conceptos = Concepto.objects.filter(nivel=2)
    nivel_3_conceptos = Concepto.objects.filter(nivel=3)
    fondos = Fondo.objects.all()
    locales = Local.objects.all()
    bancos = Banco.objects.all()
    proveedores = Proveedor.objects.all()  # Obtener todos los proveedores
    nivel_1_conceptos_json = json.dumps(list(nivel_1_conceptos.values_list('id', 'concepto_nombre')), default=str)

    return render(request, 'gasto.html', {
        'nivel_1_conceptos_json': nivel_1_conceptos_json,
        'fondos': fondos,
        'locales': locales,
        'proveedores': proveedores,  # Pasar los proveedores al contexto
        'nivel_1_conceptos': nivel_1_conceptos,
        'nivel_2_conceptos': nivel_2_conceptos,
        'nivel_3_conceptos': nivel_3_conceptos,
        'bancos':bancos
    })

def ver_prestamos(request):
    # Obtener todos los préstamos
    prestamos = Prestamo.objects.all()

    # Agregar la fecha de vencimiento calculada y el estado de las cuotas
    prestamos_data = []

    for prestamo in prestamos:
        # Calcular la fecha de vencimiento y la cuota a pagar
        fecha_vencimiento = prestamo.fecha_vencimiento
        fecha_inicial = prestamo.fecha_prestamo  # Tomamos la fecha del préstamo como la fecha inicial
        numero_cuotas = prestamo.numero_cuotas
        cuota_actual = prestamo.cuota_actual
        dia_pago = prestamo.dia_pago
        proveedor = prestamo.proveedor  # Obtener el proveedor relacionado
        monto=prestamo.monto
        # Obtener la fecha actual
        fecha_actual = timezone.now().date()

        # Calcular la fecha de pago en base a la cuota actual
        mes_pago = fecha_inicial.month + cuota_actual
        año_pago = fecha_inicial.year

        # Si el mes supera 12, ajustar el año
        while mes_pago > 12:
            mes_pago -= 12
            año_pago += 1

        # Crear la fecha de pago con el día de pago asignado
        try:
            fecha_pago = fecha_inicial.replace(year=año_pago, month=mes_pago, day=dia_pago)
        except ValueError:
            # Manejo si el mes no tiene el día exacto (ejemplo: 30 de febrero)
            from calendar import monthrange
            ultimo_dia = monthrange(año_pago, mes_pago)[1]
            fecha_pago = fecha_inicial.replace(year=año_pago, month=mes_pago, day=ultimo_dia)

        # Asegurar que la fecha de pago no sea posterior a la fecha de vencimiento
        if fecha_pago > fecha_vencimiento:
            fecha_pago = fecha_vencimiento

        estado = prestamo.estado  # Puedes agregar lógica si el estado es "proceso" o algún otro valor
        prestamos_data.append({
            'id':prestamo.id,
            'prestamo': prestamo,
            'fecha_vencimiento': fecha_vencimiento,
            'fecha_inicial': fecha_inicial,
            'numero_cuotas': numero_cuotas,
            'cuota_actual': cuota_actual,
            'fecha_pago': fecha_pago,
            'proveedor': proveedor,
            'estado': estado,  # Agregar el estado aquí
            'monto':monto,
            'monto_cuota':prestamo.monto_cuota,
        })

    return render(request, 'ver_prestamos.html', {'prestamos_data': prestamos_data})
def ficha_ingreso_view(request):

    return render(request, "ficha_ingreso.html")

def realizar_pago(request):
    if request.method == 'POST':
        prestamo_id = request.POST.get('prestamo_id', '').strip()
        monto_pagado = request.POST.get('monto_pagado', '').strip()
        fecha_pago = request.POST.get('fecha_pago', '').strip()

        # Validación de datos
        if not prestamo_id.isdigit():
            messages.error(request, "❌ ID de préstamo inválido.")
            return redirect('ver_prestamos')

        if not monto_pagado:
            messages.error(request, "❌ Debe ingresar un monto de pago.")
            return redirect('ver_prestamos')

        try:
            monto_pagado = Decimal(monto_pagado)
            if monto_pagado <= 0:
                raise ValueError
        except:
            messages.error(request, "❌ Monto de pago no válido.")
            return redirect('ver_prestamos')

        # Obtener el préstamo
        prestamo = get_object_or_404(Prestamo, id=int(prestamo_id))

        # Datos del préstamo
        cuota_actual = prestamo.cuota_actual
        monto_cuota = prestamo.monto_cuota
        numero_cuotas = prestamo.numero_cuotas

        # Verificar si ya se pagaron todas las cuotas
        if cuota_actual > numero_cuotas:
            messages.warning(request, "⚠️ Este préstamo ya ha sido cancelado.")
            return redirect('ver_prestamos')

        # Calcular lo que se ha pagado en la cuota actual
        total_pagado = prestamo.pagos.filter(cuota=cuota_actual).aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or Decimal(0)

        # Registrar el nuevo pago
        Pago.objects.create(
            prestamo=prestamo,
            cuota=cuota_actual,
            monto_pagado=monto_pagado,
            fecha_pago=fecha_pago
        )

        total_pagado += monto_pagado  # Nuevo total de pagos en esta cuota

        # Verificar si la cuota se ha completado
        if total_pagado >= monto_cuota:
            prestamo.cuota_actual += 1  # Avanzar a la siguiente cuota
            if prestamo.cuota_actual > numero_cuotas:
                prestamo.estado = "terminado"  # Marcar como terminado si se pagaron todas las cuotas
                messages.success(request, f"✅ Pago registrado. ¡Préstamo completado! 🎉")
            else:
                messages.success(request, f"✅ Pago registrado. Cuota {cuota_actual} completada. Próxima cuota: {prestamo.dia_pago} del siguiente mes.")
        else:
            restante = monto_cuota - total_pagado
            messages.warning(request, f"⚠️ Pago parcial registrado. Falta cancelar S/{restante:.2f} para completar la cuota {cuota_actual}.")

        prestamo.save()
        return redirect('ver_prestamos')

    return HttpResponse(status=405)

def get_nivel_2_conceptos(request):
    id_concepto_padre = request.GET.get('id_concepto_padre')
    conceptos_nivel_2 = Concepto.objects.filter(id_concepto_padre=id_concepto_padre)
    return JsonResponse(list(conceptos_nivel_2.values('id', 'concepto_nombre')), safe=False)

def get_nivel_3_conceptos(request):
    id_concepto_padre = request.GET.get('id_concepto_padre')
    conceptos_nivel_3 = Concepto.objects.filter(id_concepto_padre=id_concepto_padre)
    return JsonResponse(list(conceptos_nivel_3.values('id', 'concepto_nombre')), safe=False)



from django.shortcuts import get_object_or_404
@login_required
def rendicion(request):
    # Obtener la fecha actual
    today = date.today().isoformat()

    if request.user.is_superuser:
        # Obtener usuarios inactivos
        usuarios_inactivos = User.objects.filter(is_active=False)
        # Combinar gastos del superusuario y de usuarios inactivos
        gastos_requerimientos = Gasto.objects.filter(
            Q(tipo_comprobante="Requerimiento") | Q(tipo_comprobante="Sin Requerimiento"),
            rendido=False,
            gasto_origen__isnull=True  # Filtrar por gasto_origen nulo
        ).filter(
            usuario_creador__in=[request.user] + list(usuarios_inactivos)
        )
    else:
        # Filtrar por usuario autenticado
        gastos_requerimientos = Gasto.objects.filter(
            tipo_comprobante="Requerimiento",
            rendido=False,
            gasto_origen__isnull=True,  # Filtrar por gasto_origen nulo
            usuario_creador=request.user
        )

    # Renderizar la plantilla con los gastos filtrados
    return render(request, "rendicion.html", {"today": today, "gastos": gastos_requerimientos})











