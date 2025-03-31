from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    recurrencia = models.CharField(
        max_length=20,
        choices=(
            ('none', 'No se repite'),
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensual'),
        ),
        default='none'
    )

    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prestamo = models.BooleanField(default=False, verbose_name="Prestamo")  # Nuevo campo
    evento_pagado = models.BooleanField(default=False, verbose_name="Evento Pagado")  # Nuevo campo

    def __str__(self):
        return self.titulo

class OcurrenciaEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='ocurrencias')
    fecha = models.DateField()
    pagado = models.BooleanField(default=False)
    # Puedes agregar otros campos, como observaciones específicas de la ocurrencia
    def __str__(self):
        return f"{self.evento.titulo} - {self.fecha}"





class SaldoInicial(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="saldo_inicial")
    monto_saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, help_text="Saldo inicial del usuario")
    monto_saldo_inicial_yape = models.DecimalField(max_digits=15, decimal_places=2, help_text="Saldo inicial del usuario yape")
    caja_cerrada = models.BooleanField(default=False, help_text="Indica si la caja del usuario está cerrada")
    fecha_cierre = models.DateField(null=True, blank=True, help_text="Fecha en la que se cerró la caja")

    def __str__(self):
        return f"{self.usuario.username} - Saldo Inicial: {self.monto_saldo_inicial}"

class Fondo(models.Model):
    nombre_fondo = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_fondo


class Banco(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    ruc_dni = models.CharField(max_length=13, unique=True)
    razon_social = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    nombre_contacto = models.CharField(max_length=255, null=True, blank=True)  # Nombre del contacto principal

    def __str__(self):
        return self.nombre_comercial or self.razon_social

class CuentaBancaria(models.Model):
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,  # Si se elimina un proveedor, se eliminan sus cuentas bancarias
        related_name="cuentas_bancarias"
    )
    nombre_banco = models.CharField(max_length=255)  # Nombre del banco
    numero_cuenta = models.CharField(max_length=50)  # Número de cuenta bancaria
    tipo_cuenta = models.CharField(
        max_length=50,
        choices=[
            ('ahorros', 'Cuenta de Ahorros'),
            ('corriente', 'Cuenta Corriente'),
            ('otro', 'Otro')
        ],
        default='ahorros'
    )
    cci = models.CharField(max_length=50, blank=True, null=True)  # Código de Cuenta Interbancaria (CCI)

    def __str__(self):
        return f"{self.nombre_banco} - {self.numero_cuenta}"

# Modelo para la tabla "Local"
class Local(models.Model):
    nombre_local = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_local


# Modelo para la tabla "Concepto"
class Concepto(models.Model):
    concepto_nombre = models.CharField(max_length=255)
    nivel = models.IntegerField(choices=[(1, 'Nivel 1'), (2, 'Nivel 2'), (3, 'Nivel 3')])
    id_concepto_padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subconceptos')

    def __str__(self):
        return self.concepto_nombre

class Pago(models.Model):
    prestamo = models.ForeignKey('Prestamo', on_delete=models.CASCADE, related_name="pagos")
    cuota = models.PositiveIntegerField()  # Número de la cuota (ej. 1, 2, 3...)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    notas = models.TextField(blank=True, null=True)  # Nuevo campo agregado

    def __str__(self):
        return f"Pago {self.id} - Cuota {self.cuota} - Monto: {self.monto_pagado}"


# Modelo para la tabla "CajaChica"
class CajaChica(models.Model):
    fecha = models.DateField()
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gastos_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    cerrado = models.BooleanField(default=False)

    def calcular_saldo_final(self):
        self.saldo_final = self.saldo_inicial + self.ingresos_totales - self.gastos_totales

    def save(self, *args, **kwargs):
        self.calcular_saldo_final()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Caja Chica {self.id} - Fecha: {self.fecha}"

from datetime import date

class Gasto(models.Model):
    usuario_creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='gastos_creados')
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta l¨ªnea agregar¨¢ la fecha autom¨¢tica
    fecha_gasto = models.DateField(blank=True, null=True)
    concepto_nivel_1 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_1', on_delete=models.CASCADE)
    concepto_nivel_2 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_2', on_delete=models.CASCADE)
    concepto_nivel_3 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_3', on_delete=models.CASCADE)
    nombre_proveedor = models.ForeignKey(Proveedor,on_delete=models.SET_NULL,null=True,blank=True,related_name='gastos')
    local = models.ForeignKey(Local, null=True, blank=True, on_delete=models.SET_NULL, related_name='gastos_local')
    tipo_comprobante = models.CharField(max_length=50, null=True, blank=True)
    num_comprobante = models.CharField(max_length=80, null=True, blank=True)  # Campo agregado
    fecha_emision_comprobante = models.DateField(null=True, blank=True)  # Campo agregado
    numero_comprobante = models.CharField(max_length=80, null=True, blank=True)
    tipo_pago = models.CharField(max_length=50, null=True, blank=True)
    fecha_operacion = models.DateField(null=True, blank=True)
    codigo_operacion = models.CharField(max_length=50, null=True, blank=True)
    observacion = models.TextField(null=True, blank=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=50)
    rendido = models.BooleanField(default=False, null=True, blank=True)  # Nuevo campo agregado
    fecha_rendido = models.DateField(null=True, blank=True)

    # Nuevos campos
    id_requerimiento = models.CharField(max_length=100, null=True, blank=True)  # Campo nuevo para identificar el requerimiento
    num_requerimiento = models.CharField(max_length=100, null=True, blank=True)  # Campo nuevo para identificar el requerimiento
    campo_area = models.CharField(
        max_length=50,
        choices=[
            ('Sistemas', 'Sistemas'),
            ('Academico', 'Academico'),
            ('Imagen', 'Imagen'),
            ('Gerencia', 'Gerencia'),
            ('Administracion', 'Administracion'),
            ('Marketing', 'Marketing'),
            ('Ventas', 'Ventas'),
        ],
        null=True,
        blank=True
    )
    campo_mes = models.CharField(
        max_length=20,
        choices=[
            ('Enero', 'Enero'),
            ('Febrero', 'Febrero'),
            ('Marzo', 'Marzo'),
            ('Abril', 'Abril'),
            ('Mayo', 'Mayo'),
            ('Junio', 'Junio'),
            ('Julio', 'Julio'),
            ('Agosto', 'Agosto'),
            ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'),
            ('Noviembre', 'Noviembre'),
            ('Diciembre', 'Diciembre'),
        ],
        null=True,
        blank=True
    )
    banco = models.ForeignKey(Banco,on_delete=models.SET_NULL,null=True,blank=True,related_name='gastos_banco')
    # Relación con el préstamo
    prestamo = models.ForeignKey('Prestamo', null=True, blank=True, on_delete=models.SET_NULL, related_name='gastos')
    gasto_origen = models.ForeignKey(
        'self',  # Relación consigo mismo
        null=True,
        blank=True,
        on_delete=models.CASCADE,  # Si se borra el gasto original, se borran los generados
        related_name='gastos_generados'
    )

    def concepto_mayor_nivel(self):
        """
        Retorna el concepto de mayor nivel disponible (3, 2 o 1).
        """
        return self.concepto_nivel_3 or self.concepto_nivel_2 or self.concepto_nivel_1
    def __str__(self):
        return f"Gasto {self.id} - Proveedor: {self.nombre_proveedor or 'Sin proveedor'}"



class Rendicion(models.Model):
    usuario_creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendiciones_creadas'
    )
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta linea agregar la fecha autom¨¢tica
    fecha_operacion = models.DateField(blank=True, null=True)  # Fecha de la operacion
    descripcion = models.TextField(blank=True, null=True)  # Descripcion
    numero_requerimiento = models.CharField(max_length=150,blank=True, null=True)  # Numero de Requerimiento
    importe = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)  # Importe
    tipo_comprobante = models.CharField(max_length=50, null=True, blank=True)

    concepto_nivel_1 = models.ForeignKey(
        'Concepto', null=True, blank=True, related_name='nivel_1_rendicion', on_delete=models.CASCADE
    )
    concepto_nivel_2 = models.ForeignKey(
        'Concepto', null=True, blank=True, related_name='nivel_2_rendicion', on_delete=models.CASCADE
    )
    concepto_nivel_3 = models.ForeignKey(
        'Concepto', null=True, blank=True, related_name='nivel_3_rendicion', on_delete=models.CASCADE
    )

    gasto = models.ForeignKey(
        'Gasto', null=True, blank=True, on_delete=models.CASCADE, related_name='rendiciones_gasto'
    )
    proveedor = models.ForeignKey(
        'Proveedor', null=True, blank=True, on_delete=models.CASCADE, related_name='rendiciones_proveedor'
    )

    def __str__(self):
        return f"Rendicion {self.numero_requerimiento} - Importe: {self.importe}"

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('proceso', 'En proceso'),
        ('terminado', 'Terminado'),
    ]
    fecha_prestamo = models.DateField()
    fecha_vencimiento = models.DateField(blank=True, null=True)
    numero_cuotas = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    tea = models.DecimalField(max_digits=5, decimal_places=2)
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE)
    analista = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True) #opcional
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='terminado')  # <-- Aquí se agregan los choices
    cuota_actual = models.PositiveIntegerField()
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    dia_pago = models.PositiveIntegerField(default=1,blank=True,null=True)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, default=0,blank=True, null=True)  # Nuevo campo
    notas = models.TextField(blank=True, null=True)  # Nuevo campo agregado


class Ingreso(models.Model):
    usuario_creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='ingresos_creados')
    prestamo = models.ForeignKey('Prestamo',on_delete=models.SET_NULL,null=True,blank=True,related_name='ingresos')
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta l¨ªnea agregar¨¢ la fecha autom¨¢tica
    fecha_ingreso = models.DateField(blank=True, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    id_fondo = models.ForeignKey(Fondo, on_delete=models.CASCADE, null=True, blank=True)  # Permitir valores nulos
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    moneda = models.CharField(max_length=50)
    fecha_operacion = models.DateField(null=True, blank=True)
    codigo_operacion = models.CharField(max_length=50, blank=True, null=True)  # Ahora opcional
    observacion = models.TextField(blank=True, null=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, related_name='ingresos_local',null=True, blank=True)
    # Nuevo campo 'extorno' por defecto a False
    extorno = models.BooleanField(default=False, null=True, blank=True)
    importe_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Nuevo campo, NOT NULL y NOT BLANK
    importe_yape = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Nuevo campo, NOT NULL y NOT BLANK
    banco = models.ForeignKey(Banco,on_delete=models.SET_NULL,null=True,blank=True,related_name='ingresos_banco')
    gasto_origen = models.ForeignKey(
        Gasto,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='ingreso_generado'
    )
    def __str__(self):
        return f"Ingreso {self.id}"

class Personal(models.Model):
    # Datos del trabajador
    dni = models.CharField(max_length=20, blank=True, null=True)
    apellidos_nombres = models.CharField(max_length=255, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    correo_personal = models.EmailField(blank=True, null=True)
    correo_corporativo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    # Datos laborales
    periodo_inicio = models.DateField(blank=True, null=True)
    periodo_fin = models.DateField(null=True, blank=True)
    tipo_trabajador = models.CharField(max_length=50, blank=True, null=True)
    tipo_contrato = models.CharField(max_length=50, blank=True, null=True)
    tipo_pago = models.CharField(max_length=50, choices=[('efectivo', 'Efectivo'), ('deposito', 'Depósito')], blank=True, null=True)
    nombre_cuenta = models.CharField(max_length=100, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=30, blank=True, null=True)
    cci = models.CharField(max_length=20, blank=True, null=True)  # Código de Cuenta Interbancario
    asignacion_familiar = models.BooleanField(default=False, blank=True, null=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, related_name='local_trabajo',null=True, blank=True)

    # Nuevos campos agregados
    ocupacion = models.CharField(max_length=100, blank=True, null=True)  # Ocupación
    remuneracion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0.00)  # Remuneración

    # Datos de seguridad social
    regimen_salud = models.CharField(max_length=50, choices=[('ninguno', 'Ninguno'), ('essalud', 'EsSalud'), ('sis', 'SIS')], blank=True, null=True)
    regimen_pensionario = models.CharField(max_length=50, choices=[('ninguno', 'Ninguno'),('onp', 'ONP'), ('afp', 'AFP')], blank=True, null=True)
    regimen_pensionario_details = models.CharField(max_length=255, blank=True, null=True)

    # Datos de la situación educativa
    situacion_educativa = models.CharField(max_length=255, blank=True, null=True)
    tipo_instruccion = models.CharField(max_length=255, blank=True, null=True)
    institucion = models.CharField(max_length=255, blank=True, null=True)
    carrera_estudio = models.CharField(max_length=255, blank=True, null=True)
    ano_egreso = models.CharField(max_length=4, blank=True, null=True)
    contraseña_creada = models.BooleanField(default=False)
    # Horario de Trabajo
    turno_manana_inicio = models.TimeField(null=True, blank=True)
    turno_manana_fin = models.TimeField(null=True, blank=True)
    turno_tarde_inicio = models.TimeField(null=True, blank=True)
    turno_tarde_fin = models.TimeField(null=True, blank=True)

    observacion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.apellidos_nombres} - {self.dni}"






