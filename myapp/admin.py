from django.contrib import admin
from .models import Fondo, Local, Concepto, CajaChica, Rendicion, Gasto, Ingreso,Proveedor,CuentaBancaria,Banco


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Muestra ID y nombre en la lista
    search_fields = ('nombre',)  # Agrega una barra de b®≤squeda por nombre
    ordering = ('nombre',)  # Ordena alfab®¶ticamente los bancos
    
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

    # Acci√≥n personalizada para marcar como cerrado
    def marcar_como_cerrado(self, request, queryset):
        queryset.update(cerrado=True)
    marcar_como_cerrado.short_description = 'Marcar como cerrado'

# Registro del modelo Rendicion
@admin.register(Rendicion)
class RendicionAdmin(admin.ModelAdmin):
    list_display = (
        'numero_requerimiento', 
        'fecha_operacion', 
        'importe', 
        'concepto_nivel_1',
        'concepto_nivel_2',
        'concepto_nivel_3',
        'gasto'
    )

# Registro del modelo Gasto
@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('fecha_gasto', 'local', 'tipo_comprobante', 'tipo_pago', 'observacion')
    list_filter = ('local', 'tipo_comprobante', 'tipo_pago')
@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_ingreso', 'importe', 'id_fondo', 'metodo_pago', 'moneda', 'local')
    list_filter = ('fecha_ingreso', 'metodo_pago', 'moneda', 'local')
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'ruc_dni', 'razon_social', 'nombre_comercial')
    search_fields = ('ruc_dni', 'razon_social', 'nombre_comercial')
    list_filter = ('razon_social',)  # Agrega un filtro opcional para facilitar la b®≤squeda por raz®Æn social.
    
    
# Registro del modelo CuentaBancaria
@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'nombre_banco', 'numero_cuenta')
    search_fields = ('nombre_banco', 'numero_cuenta', 'proveedor__razon_social')
    list_filter = ('nombre_banco',)