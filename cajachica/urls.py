
from django.contrib import admin
from django.urls import path
from myapp.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login_view, name='login'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('ingreso/', ingreso, name='ingreso'),
    path('gasto/', gasto, name='gasto'),
    path('rendicion/', rendicion, name='rendicion'),
    path('logout/',logout_view, name='logout'),
    path('cajachica/', caja_chica, name='caja_chica'),
    path('rendiciones/<int:gasto_id>/', registrar_rendiciones, name='registrar_rendiciones'),
    path('guardar_oficial/', guardar_oficial, name='guardar_oficial'),
    path('edit_item/<int:id>/<str:tipo>/', edit_item, name='edit_item'),
    path('edit_item/<int:id>/Gasto/', gasto_edit, name='gasto_edit'),
    path('registrar_gasto/<int:id>/', registrar_gasto, name='registrar_gasto'),
    path('editar_ingreso/<int:id>/', editar_ingreso, name='editar_ingreso'),
    path('proveedores/',proveedores, name='proveedores'),
    path('guardar-proveedor/', guardar_proveedor, name='guardar_proveedor'),
    path('proveedores/editar/', editar_proveedor, name='editar_proveedor'),
    path('api/proveedores/', buscar_proveedores, name='buscar_proveedores'),
    path('prueba/', prueba, name='prueba'),
    path('proveedores/eliminar/<int:proveedor_id>/', eliminar_proveedor, name='eliminar_proveedor'),
    path('get_nivel_2_conceptos/', get_nivel_2_conceptos, name='get_nivel_2_conceptos'),
    path('get_nivel_3_conceptos/', get_nivel_3_conceptos, name='get_nivel_3_conceptos'),
    path('reportes/', reportes, name='reportes'),
    path('generar_reporte_json/',generar_reporte_json, name='generar_reporte_json'),
    path('conceptos/', conceptos, name='conceptos'),
    path('crear_concepto/', crear_concepto, name='crear_concepto'),
    path('editar_concepto/<int:id>/', editar_concepto, name='editar_concepto'),
    path('eliminar_concepto/<int:id>/', eliminar_concepto, name='eliminar_concepto'),
    path('guardar_cuenta_bancaria/', guardar_cuenta_bancaria, name='guardar_cuenta_bancaria'),
    path('proveedores/<int:proveedor_id>/cuentas/', cuentas_bancarias, name='cuentas_bancarias'),
    path('actualizar-movimiento/', actualizar_movimiento, name='actualizar_movimiento'),
    path('ficha-ingreso/', ficha_ingreso_view, name='ficha_ingreso'),
    path('agregar_banco/', agregar_banco, name='agregar_banco'),
    path('descargarexcel/', descargar_excel, name='descargarexcel'),
    path('prestamos/', prestamos, name='prestamos'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)