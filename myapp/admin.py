from django.contrib import admin
from .models import Fondo, Local, Concepto, CajaChica, Rendicion, Gasto, Ingreso,Proveedor,CuentaBancaria,Banco,Prestamo,SaldoInicial,Pago,Personal

class PersonalAdmin(admin.ModelAdmin):
    list_display = ('dni','contraseña_creada', 'apellidos_nombres', 'celular', 'correo_personal', 'correo_corporativo')
    search_fields = ('dni', 'apellidos_nombres', 'correo_personal', 'correo_corporativo', 'celular', 'ocupacion')
    list_filter = ('tipo_trabajador', 'tipo_pago', 'regimen_salud', 'regimen_pensionario', 'situacion_educativa')
    ordering = ('apellidos_nombres',)
    list_per_page = 20  # Número de registros por página

admin.site.register(Personal, PersonalAdmin)

class PagoAdmin(admin.ModelAdmin):
    list_display = ('prestamo', 'cuota', 'monto_pagado', 'fecha_pago')
    list_filter = ('prestamo', 'cuota', 'fecha_pago')
    search_fields = ('prestamo__id', 'cuota')

admin.site.register(Pago, PagoAdmin)

@admin.register(SaldoInicial)
class SaldoInicialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'monto_saldo_inicial')  # Campos a mostrar en la lista
    list_filter = ('usuario',)  # Filtro por usuario
    search_fields = ('usuario__username',)  # Búsqueda por nombre de usuario

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'banco', 'monto', 'estado', 'cuota_actual', 'numero_cuotas', 'dia_pago', 'fecha_prestamo', 'fecha_vencimiento')
    list_filter = ('estado', 'banco', 'proveedor', 'local')
    search_fields = ('analista', 'proveedor__nombre', 'banco__nombre')


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Muestra ID y nombre en la lista
    search_fields = ('nombre',)  # Agrega una barra de b¨²squeda por nombre
    ordering = ('nombre',)  # Ordena alfab¨¦ticamente los bancos

# Registro del modelo Fondo
@admin.register(Fondo)
class FondoAdmin(admin.ModelAdmin):
    list_display = ('nombre_fondo',)
    search_fields = ('nombre_fondo',)

# Registro del modelo Local
@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('nombre_local',)
    search_fields = ('nombre_local',)

# Registro del modelo Concepto
@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    list_display = ('concepto_nombre', 'nivel', 'id_concepto_padre')
    search_fields = ('concepto_nombre',)
    list_filter = ('nivel',)

# Registro del modelo CajaChica
@admin.register(CajaChica)
class CajaChicaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'saldo_inicial', 'ingresos_totales', 'gastos_totales', 'saldo_final', 'cerrado')
    list_filter = ('cerrado',)
    search_fields = ('fecha',)
    actions = ['marcar_como_cerrado']

    # AcciÃ³n personalizada para marcar como cerrado
    def marcar_como_cerrado(self, request, queryset):
        queryset.update(cerrado=True)
    marcar_como_cerrado.short_description = 'Marcar como cerrado'

# Registro del modelo Rendicion
@admin.register(Rendicion)
class RendicionAdmin(admin.ModelAdmin):
    list_display = (
        'numero_requerimiento',
        'usuario_creador',
        'fecha_operacion',
        'importe',
        'concepto_nivel_1',
        'concepto_nivel_2',
        'concepto_nivel_3',
        'gasto'
    )

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha_gasto',
        'proveedor',  # Muestra la razón social del proveedor
        'usuario_creador',
        'importe',
        'rendido',
        'local',
        'tipo_comprobante',
        'tipo_pago',
        'observacion'
    )
    list_filter = ('local', 'tipo_comprobante', 'tipo_pago', 'rendido')

    def proveedor(self, obj):
        return obj.nombre_proveedor.razon_social if obj.nombre_proveedor else "-"

    proveedor.short_description = "Proveedor"  # Nombre de la columna en el admin


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_ingreso','usuario_creador', 'importe', 'id_fondo', 'metodo_pago', 'moneda', 'local')
    list_filter = ('fecha_ingreso', 'metodo_pago', 'moneda', 'local')
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'ruc_dni', 'razon_social', 'nombre_comercial')
    search_fields = ('ruc_dni', 'razon_social', 'nombre_comercial')
    list_filter = ('razon_social',)  # Agrega un filtro opcional para facilitar la b¨²squeda por raz¨®n social.


# Registro del modelo CuentaBancaria
@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'nombre_banco', 'numero_cuenta')
    search_fields = ('nombre_banco', 'numero_cuenta', 'proveedor__razon_social')
    list_filter = ('nombre_banco',)