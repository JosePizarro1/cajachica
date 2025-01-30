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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from django.utils.timezone import now

def ficha_ingreso_view(request):
    if request.method == "POST":
        ficha = FichaIngreso(
            dni=request.POST.get("dni"),
            nombres=request.POST.get("nombres"),
            fecha_nacimiento=request.POST.get("fecha_nacimiento"),
            celular=request.POST.get("celular"),
            correo_personal=request.POST.get("correo_personal"),
            correo_corporativo=request.POST.get("correo_corporativo"),
            direccion=request.POST.get("direccion"),
            fecha_inicio=request.POST.get("fecha_inicio"),
            fecha_fin=request.POST.get("fecha_fin"),
            tipo_trabajador=request.POST.get("tipo_trabajador"),
            tipo_contrato=request.POST.get("tipo_contrato"),
            tipo_pago=request.POST.get("tipo_pago"),
            nombre_cuenta=request.POST.get("nombre_cuenta"),
            numero_cuenta=request.POST.get("numero_cuenta"),
            asignacion_familiar=bool(request.POST.get("asignacion_familiar")),
            regimen_salud=request.POST.get("regimen_salud"),
            regimen_pensionario=request.POST.get("regimen_pensionario"),
            situacion_educativa=request.POST.get("situacion_educativa"),
            tipo_instruccion=request.POST.get("tipo_instruccion"),
            institucion=request.POST.get("institucion"),
            carrera=request.POST.get("carrera"),
            anio_egreso=request.POST.get("anio_egreso"),
        )
        ficha.save()
        messages.success(request, "Ficha guardada correctamente.")
        return redirect("ficha_ingreso")

    return render(request, "ficha_ingreso.html")
    
    
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

            # Filtrar los gastos según los parámetros
            gastos = Gasto.objects.filter(fecha_gasto__gte=fecha_inicio_dt, fecha_gasto__lte=fecha_final_dt)

            if concepto_nivel_1 != 'todos':
                gastos = gastos.filter(concepto_nivel_1=concepto_nivel_1)
            if concepto_nivel_2 != 'todos':
                gastos = gastos.filter(concepto_nivel_2=concepto_nivel_2)

            # Verificar si hay gastos para mostrar
            if not gastos.exists():
                return JsonResponse({'error': 'No se encontraron gastos con los parámetros seleccionados'}, status=404)

            # Agrupar los gastos por concepto_nivel_2
            grouped_gastos = {}
            total_importe = 0

            for gasto in gastos:
                concepto_2 = gasto.concepto_nivel_2.concepto_nombre if gasto.concepto_nivel_2 else "Sin Nivel 2"
                if concepto_2 not in grouped_gastos:
                    grouped_gastos[concepto_2] = []

                grouped_gastos[concepto_2].append({
                    'proveedor': gasto.nombre_proveedor.nombre_comercial or gasto.nombre_proveedor.razon_social,
                    'concepto': gasto.concepto_nivel_1.concepto_nombre,
                    'forma_pago': gasto.tipo_pago,
                    'importe': gasto.importe,
                    'fecha': gasto.fecha_gasto.strftime("%d/%m/%Y") if gasto.fecha_gasto else 'Sin Fecha',
                })
                total_importe += gasto.importe

            # Generar la fecha actual para el reporte
            fecha_actual = datetime.now().strftime("%d/%m/%Y")

            # Preparar los datos que se enviarán
            response_data = {
                'fecha': fecha_actual,
                'gastos_por_grupo': [
                    {'nivel_2': nivel_2, 'gastos': gastos_data}
                    for nivel_2, gastos_data in grouped_gastos.items()
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



from datetime import date
from decimal import Decimal
from django.shortcuts import render

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

    # Obtener las fechas de los parámetros GET, si no están presentes usar la fecha de hoy
    fecha_inicio = request.GET.get('fecha_inicio', hoy)
    fecha_fin = request.GET.get('fecha_fin', hoy)

    # Convertir las fechas a tipo date
    fecha_inicio = date.fromisoformat(fecha_inicio)
    fecha_fin = date.fromisoformat(fecha_fin)

    # Calcular el saldo base según el username del usuario autenticado
    saldo_base = Decimal(0)
    if request.user.username == 'vianca':
        saldo_base = Decimal('2008.65')
    elif request.user.username == 'mary':
        saldo_base = Decimal('30047.28')

    # Calcular el saldo inicial usando la función personalizada
    saldo_inicial = obtener_saldo_inicial_manual(fecha_inicio, usuario=request.user if not request.user.is_staff else None)
    # Sumar el saldo base al saldo inicial
    saldo_inicial += saldo_base

    # Verificar si el usuario es staff
    if request.user.is_staff:
        # Staff puede ver todos los ingresos y gastos
        ingresos = Ingreso.objects.filter(fecha_ingreso__range=[fecha_inicio, fecha_fin])
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

    # Crear la respuesta HTTP para descargar el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="movimientos_{fecha_inicio}_a_{fecha_fin}.xlsx"'

    # Crear el archivo Excel y agregar datos
    wb = Workbook()
    ws = wb.active
    
    # Escribir el título en negrita
    titulo = f"Movimientos de {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
    ws.append([titulo])
    ws.append([])  # Línea vacía
    
    # Escribir el saldo inicial antes de la tabla
    ws.append([f'Saldo inicial: {saldo_inicial:,.2f}'])
    ws.append([])  # Línea vacía

    # Definir los encabezados
    encabezados = ['Tipo', 'Fecha', 'Método de Pago', 'Concepto', 'Proveedor', 'Banco', 'Código de Operación', 'Fecha de Operación', 'Monto', 'Notas']
    
    # Escribir encabezados en la primera fila (negrita), empezando desde la columna A
    for col_num, header in enumerate(encabezados, 1):  # Comienza en la columna A
        cell = ws.cell(row=5, column=col_num, value=header)
        cell.font = Font(bold=True)
    
    # Escribir los movimientos en las filas siguientes
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

    # Escribir el saldo final en la fila siguiente después de los movimientos
    ws.append([])  # Línea vacía
    ws.append([f'Saldo final: {saldo_inicial + sum([m["monto"] for m in movimientos]):,.2f}'])

    # Ajustar el ancho de las columnas
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
    
    # Guardar el archivo
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
    if request.user.username == 'vianca':
        saldo_base = Decimal('2008.65')
    elif request.user.username == 'mary':
        saldo_base = Decimal('30047.28')

    # Calcular el saldo inicial usando la función personalizada
    saldo_inicial = obtener_saldo_inicial_manual(fecha_inicio, usuario=request.user if not request.user.is_staff else None)
    # Sumar el saldo base al saldo inicial
    saldo_inicial += saldo_base
    # Verificar si el usuario es staff
    if request.user.is_staff:
        # Staff puede ver todos los ingresos y gastos
        ingresos = Ingreso.objects.filter(fecha_ingreso__range=[fecha_inicio, fecha_fin])
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
            'concepto': nombre_fondo,
            'notas': ingreso.observacion or '',
            'monto': Decimal(ingreso.importe),
            'moneda': ingreso.moneda,
            'proveedor':ingreso.id_fondo.nombre_fondo,
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
@login_required
def editar_ingreso(request, id):
    # Obtener el ingreso correspondiente al ID
    ingreso = get_object_or_404(Ingreso, id=id)

    if request.method == "POST":
        # Obtener datos enviados en el formulario
        id_fondo = request.POST.get('id_fondo')
        metodo_pago = request.POST.get('metodo_pago')
        codigo_operacion = request.POST.get('codigo_operacion', '').strip()
        fecha_operacion = request.POST.get('fecha_operacion', '').strip()
        observacion = request.POST.get('observacion')
        fondo = get_object_or_404(Fondo, id=id_fondo)

        # Validación si el método de pago es "yape" o "transferencia"
        if metodo_pago in ["yape", "transferencia"]:
            if not codigo_operacion:
                messages.error(request, "El código de operación es obligatorio para métodos de pago Yape o Transferencia.")
                return redirect('editar_ingreso', id=id)
            if not fecha_operacion:
                messages.error(request, "La fecha de operación es obligatoria para métodos de pago Yape o Transferencia.")
                return redirect('editar_ingreso', id=id)

            # Validar y convertir fecha_operacion
            try:
                fecha_operacion_obj = datetime.strptime(fecha_operacion, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "El formato de la fecha de operación es inválido. Debe estar en el formato YYYY-MM-DD.")
                return redirect('editar_ingreso', id=id)
        else:
            # Limpiar valores si no se usan
            codigo_operacion = None
            fecha_operacion_obj = None

        # Actualizar los campos del modelo
        ingreso.id_fondo = fondo
        ingreso.metodo_pago = metodo_pago
        ingreso.codigo_operacion = codigo_operacion
        ingreso.fecha_operacion = fecha_operacion_obj
        ingreso.observacion = observacion

        # Guardar cambios
        ingreso.save()

        # Enviar mensaje de éxito y redirigir
        messages.success(request, "El ingreso ha sido actualizado exitosamente.")
        return redirect('caja_chica')  # Ajusta el nombre de esta vista si es necesario

    # Renderizar la página con los datos existentes del ingreso
    context = {
        'ingreso': ingreso,
        'fondos': Fondo.objects.all()  # Asegúrate de pasar los fondos al contexto si se usan en el formulario
    }
    return render(request, 'edit_ingreso.html', context)

@login_required
def edit_item(request, id, tipo):
    nivel_1_conceptos = Concepto.objects.filter(nivel=1)
    nivel_2_conceptos = Concepto.objects.filter(nivel=2)
    nivel_3_conceptos = Concepto.objects.filter(nivel=3)
    fondos = Fondo.objects.all()
    locales = Local.objects.all()
    if tipo == 'Extorno':
        ingreso = get_object_or_404(Ingreso, id=id)
                # Convertir importe a cadena con punto decimal
        if ingreso.importe is not None:
            ingreso.importe = f"{float(ingreso.importe):.2f}"
        return render(request, 'edit_ingreso.html', {'ingreso': ingreso,
                    'fondos': fondos,
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
                    tipo_comprobante="Exhorto",
                    nombre_proveedor=gasto.nombre_proveedor,  # Asignar el proveedor original
                    local=gasto.local,
                    tipo_pago="efectivo",
                    
                    
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
                    metodo_pago="Pendiente",
                    moneda=gasto.moneda,  # Moneda por defecto del gasto asociado
                    extorno=True,
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

def calcular_gastos_por_metodo_pago():
    """
    Calcula la suma de los gastos agrupados por método de pago.
    Retorna un diccionario con etiquetas (métodos de pago) y valores (totales).
    """
    gastos_por_metodo = (
        Gasto.objects
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
        
        # Obtener los 5 conceptos con más gasto
        top_conceptos = (
            Gasto.objects
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
        
        # Obtener ingresos por mes para el gráfico de barras (solo mes actual)
        ingresos_mes_actual = Ingreso.objects.filter(fecha_ingreso__year=current_year, fecha_ingreso__month=current_month)
        ingresos_mes_actual_total = ingresos_mes_actual.aggregate(total_ingresos=Sum('importe'))['total_ingresos'] or Decimal('0.00')

        # Obtener gastos por mes para el gráfico de barras (solo mes actual)
        gastos_mes_actual = Gasto.objects.filter(fecha_gasto__year=current_year, fecha_gasto__month=current_month)
        gastos_mes_actual_total = gastos_mes_actual.aggregate(total_gastos=Sum('importe'))['total_gastos'] or Decimal('0.00')

        # Obtener ingresos por mes para el gráfico de líneas (todo el año actual)
        ingresos_anuales = Ingreso.objects.filter(fecha_ingreso__year=current_year).annotate(month=TruncMonth('fecha_ingreso')).values('month').annotate(total_ingresos=Sum('importe')).order_by('month')

        # Obtener gastos por mes para el gráfico de líneas (todo el año actual)
        gastos_anuales = Gasto.objects.filter(fecha_gasto__year=current_year).annotate(month=TruncMonth('fecha_gasto')).values('month').annotate(total_gastos=Sum('importe')).order_by('month')

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
        datos_gastos_metodo_pago = calcular_gastos_por_metodo_pago()


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
            prestamo_nuevo = request.POST.get('prestamo_nuevo') == 'on'  # Checkbox
            cuota_actual = request.POST.get('cuota_actual') if not prestamo_nuevo else 1

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
                prestamo_nuevo=prestamo_nuevo,
                cuota_actual=cuota_actual,
                local=local,
                dia_pago=dia_pago  # Guardamos el día de pago
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
                moneda="soles",
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
        codigo_operacion = request.POST.get('codigo_operacion') if metodo_pago == ['transferencia', 'yape'] else None
        fecha_operacion  =request.POST.get('fecha_operacion') if metodo_pago in ['transferencia', 'yape'] else None
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
    if tipo_comprobante != 'Requerimiento':
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
            codigo_operacion = data.get('codigo_operacion') if metodo_pago in ['transferencia', 'yape'] else None
            fecha_operacion = data.get('fecha_operacion') if metodo_pago in ['transferencia', 'yape'] else None
            concepto_nivel_1 = data.get('concepto_nivel_1')
            concepto_nivel_2 = data.get('concepto_nivel_2')
            concepto_nivel_3 = data.get('concepto_nivel_3')
            numero_comprobante = data.get('num_comprobante')
            fecha_emision_comprobante = data.get('fecha_emision_comprobante') if tipo_comprobante  in ['RHE', 'Factura', 'Boleta'] else None # Nuevo campo
            campo_area=data.get('campo_area')
            campo_mes=data.get('campo_mes') if tipo_comprobante  in ['Boleta de pago'] else None
            id_requerimiento = data.get('id_requerimiento')  # Nuevo campo
            num_requerimiento = data.get('num_requerimiento')  # Nuevo campo
            
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
                num_requerimiento=num_requerimiento if tipo_comprobante == 'Requerimiento' else None
                
                
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
    })


    
    
def get_nivel_2_conceptos(request):
    id_concepto_padre = request.GET.get('id_concepto_padre')
    conceptos_nivel_2 = Concepto.objects.filter(id_concepto_padre=id_concepto_padre)
    return JsonResponse(list(conceptos_nivel_2.values('id', 'concepto_nombre')), safe=False)
    
def get_nivel_3_conceptos(request):
    id_concepto_padre = request.GET.get('id_concepto_padre')
    conceptos_nivel_3 = Concepto.objects.filter(id_concepto_padre=id_concepto_padre)
    return JsonResponse(list(conceptos_nivel_3.values('id', 'concepto_nombre')), safe=False)
 
    
    
from django.shortcuts import get_object_or_404

def rendicion(request):
    # Obtener la fecha actual
    today = date.today().isoformat()

    if request.user.is_superuser:
        # Obtener usuarios inactivos
        usuarios_inactivos = User.objects.filter(is_active=False)
        # Combinar gastos del superusuario y de usuarios inactivos
        gastos_requerimientos = Gasto.objects.filter(
            tipo_comprobante="Requerimiento", 
            rendido=False
        ).filter(
            usuario_creador__in=[request.user] + list(usuarios_inactivos)
        )
    else:
        # Filtrar por usuario autenticado
        gastos_requerimientos = Gasto.objects.filter(
            tipo_comprobante="Requerimiento", 
            rendido=False, 
            usuario_creador=request.user
        )

    # Renderizar la plantilla con los gastos filtrados
    return render(request, "rendicion.html", {"today": today, "gastos": gastos_requerimientos})
    
    
    
    
    
    
    
    
    
    
    
    