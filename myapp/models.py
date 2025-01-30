from django.db import models
from django.contrib.auth.models import User

# Modelo para la tabla "Fondos"
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
    numero_cuenta = models.CharField(max_length=50, unique=True)  # N�mero de cuenta bancaria
    tipo_cuenta = models.CharField(
        max_length=50,
        choices=[
            ('ahorros', 'Cuenta de Ahorros'),
            ('corriente', 'Cuenta Corriente'),
            ('otro', 'Otro')
        ],
        default='ahorros'
    )
    cci = models.CharField(max_length=50, blank=True, null=True)  # C�digo de Cuenta Interbancaria (CCI)

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
# Modelo para la tabla "Gastos"
class Gasto(models.Model):
    
    usuario_creador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='gastos_creados'
    )
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta l��nea agregar�� la fecha autom��tica
    fecha_gasto = models.DateField(blank=True, null=True)
    concepto_nivel_1 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_1', on_delete=models.CASCADE)
    concepto_nivel_2 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_2', on_delete=models.CASCADE)
    concepto_nivel_3 = models.ForeignKey(Concepto, null=True, blank=True, related_name='nivel_3', on_delete=models.CASCADE)
    nombre_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gastos'
    )
    local = models.ForeignKey(Local, null=True, blank=True, on_delete=models.CASCADE, related_name='gastos_local')
    
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
    banco = models.ForeignKey(
        Banco, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='gastos_banco'
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
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta l��nea agregar�� la fecha autom��tica
    fecha_operacion = models.DateField(blank=True, null=True)  # Fecha de la operaci��n
    descripcion = models.TextField(blank=True, null=True)  # Descripci��n
    numero_requerimiento = models.CharField(max_length=150,blank=True, null=True)  # N��mero de Requerimiento
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
        'Gasto', null=True, blank=True, on_delete=models.SET_NULL, related_name='rendiciones_gasto'
    )
    proveedor = models.ForeignKey(
        'Proveedor', null=True, blank=True, on_delete=models.SET_NULL, related_name='rendiciones_proveedor'
    )
    
    def __str__(self):
        return f"Rendicion {self.numero_requerimiento} - Importe: {self.importe}"
class Prestamo(models.Model):
    fecha_prestamo = models.DateField()
    fecha_vencimiento = models.DateField()
    numero_cuotas = models.PositiveIntegerField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    tea = models.DecimalField(max_digits=5, decimal_places=2)
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE)
    analista = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50)
    prestamo_nuevo = models.BooleanField()
    cuota_actual = models.PositiveIntegerField()
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    dia_pago = models.PositiveIntegerField(default=1)


class Ingreso(models.Model):
    usuario_creador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ingresos_creados'
    )
    prestamo = models.ForeignKey(
        'Prestamo',  
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ingresos'
    )
    fecha_registro = models.DateField(auto_now_add=True,blank=True, null=True)  # Esta l��nea agregar�� la fecha autom��tica
    fecha_ingreso = models.DateField(blank=True, null=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    id_fondo = models.ForeignKey(Fondo, on_delete=models.CASCADE, null=True, blank=True)  # Permitir valores nulos
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    moneda = models.CharField(max_length=50)
    fecha_operacion = models.DateField(null=True, blank=True)
    codigo_operacion = models.CharField(max_length=50, blank=True, null=True)  # Ahora opcional
    observacion = models.TextField(blank=True, null=True)
    local = models.ForeignKey(Local, on_delete=models.CASCADE, related_name='ingresos_local',null=True, blank=True)
    # Nuevo campo 'extorno' por defecto a False
    extorno = models.BooleanField(default=False, null=True, blank=True)
    # Nuevo campo 'banco' relacionado con el modelo Banco
    banco = models.ForeignKey(
        Banco, 
        on_delete=models.SET_NULL,  # Si el banco es eliminado, no elimina el ingreso, sino que pone el campo a null
        null=True, 
        blank=True,
        related_name='ingresos_banco'  # Nombre de relaci�n inversa (opcional)
    )

    def __str__(self):
        return f"Ingreso {self.id}"

