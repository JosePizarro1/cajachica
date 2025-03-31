
from django.contrib import admin
from django.urls import path
from myapp.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('reiniciar-secuencia/', reiniciar_secuencia, name='reiniciar_secuencia'),
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
    path('ver_prestamos/', ver_prestamos, name='ver_prestamos'),
    path('realizar_pago/', realizar_pago, name='realizar_pago'),
    path('reporte-anual/', reporte_anual, name='reporte_anual'),
    path('guardar_datos/', guardar_datos1, name='guardar_datos'),
    path('ver_personal/', ver_personal, name='ver_personal'),
    path('editar_personal/<int:id>/', editar_personal, name='editar_personal'),
    path('crear_contraseña/<int:personal_id>/', crear_contraseña, name='crear_contraseña'),
    path('generar_pdf/<int:persona_id>/', generar_pdf, name='generar_pdf'),
    path('editar-ficha/<int:id_personal>/', guardar_datos_editados, name="guardar_datos_editados"),
    path('reporte-mensual/', reporte_mensual, name='reporte_mensual'),
    path('reporte-diario/', generar_reporte_diario, name='reporte_diario'),
    path('cerrar-caja/', cerrar_caja, name='cerrar_caja'),
    path("cerrar-caja-usuario/<int:user_id>/", cerrar_caja_usuario, name="cerrar_caja_usuario"),
    path("reactivar-caja-usuario/<int:user_id>/", reactivar_caja_usuario, name="reactivar_caja_usuario"),
    path("registrar-usuario/", registrar_usuario, name="registrar_usuario"),
    path('transferir-yape/', transferir_yape, name='transferir_yape'),
    path('proveedores/verificar_gastos/<int:proveedor_id>/', verificar_gastos, name='verificar_gastos'),
    path('reporte_proveedor_pdf/', reporte_proveedor_pdf, name='reporte_proveedor_pdf'),
    path('reporte_proveedor_excel/', reporte_proveedor_excel, name='reporte_proveedor_excel'),
    path('trigger-error/', trigger_error, name='trigger_error'),
    path('eliminar-item/<int:item_id>/<str:item_tipo>/', eliminar_item, name='eliminar_item'),
    path('reporte-concepto-proveedor-pdf/', reporte_concepto_proveedor_pdf, name='reporte_concepto_proveedor_pdf'),
    path('generar-pdf-personal/', generar_pdf_personal, name='generar_pdf_personal'),
    path('ver-rendidos/', ver_rendidos, name='ver_rendidos'),
    path('gasto/<int:gasto_id>/rendiciones/', ver_rendiciones_asociadas, name='ver_rendiciones_asociadas'),
    path('crear_pdf_rendicion/<int:gasto_id>/', crear_pdf_rendicion, name='crear_pdf_rendicion'),
    path("generar-pdf-rendiciones/", generar_pdf_rendiciones, name="generar_pdf_rendiciones"),
    path('ver_pagos/<int:prestamo_id>/', ver_pagos, name='ver_pagos'),
    path('finalizar_cuota/<int:prestamo_id>/', finalizar_cuota, name='finalizar_cuota'),
    path('reporte-diario-conceptos/', reporte_diario_conceptos, name='reporte_diario_conceptos'),

        #Calendario
    path('calendario/', ver_calendar, name='ver_calendar'),
    path('crear-evento/', crear_evento, name='crear_evento'),
    path('obtener-eventos/', obtener_eventos, name='obtener_eventos'),
    path('eliminar-evento/', eliminar_evento, name='eliminar_evento'),
    path('eliminar-ocurrencia-evento/', eliminar_ocurrencia_evento, name='eliminar_ocurrencia_evento'),
    path('pagar-evento/', pagar_evento, name='pagar_evento'),
    path('obtener-eventos-pagados/', obtener_eventos_pagados, name='obtener_eventos_pagados'),
    path('actualizar_evento/', actualizar_evento, name='actualizar_evento'),
    path('gasto_calendario/', gasto_calendario, name='gasto_calendario'),
    path('obtener-total-mes/', obtener_total_mes, name='obtener_total_mes'),
    path('generar_reporte_pdf_calendario/', generar_reporte_pdf_calendario, name='generar_reporte_pdf_calendario'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Agrega los handlers de error aquí:
handler404 = 'myapp.views.custom_404'
handler500 = 'myapp.views.custom_500'