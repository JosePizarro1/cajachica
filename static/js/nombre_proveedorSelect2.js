$(document).ready(function () {


  // Referencias a los elementos de los contenedores
  const metodoPagoSelect = document.getElementById('metodo_pago');
  const codigoOperacionContainer = document.getElementById('codigo-operacion-container');
  const fechaOperacionContainer = document.getElementById('fecha-operacion-container');
  const TipoSelect = document.getElementById('tipo_comprobante');
  const codigoComprobanteContainer = document.getElementById('codigo-comprobante-container');
  const fechaComprobanteContainer = document.getElementById('fecha-emision-comprobante-container');
  const conceptoNivel1 = document.getElementById('concepto_nivel_1_results');
  const conceptoNivel2 = document.getElementById('concepto_nivel_2_results');
  const conceptoNivel3 = document.getElementById('concepto_nivel_3_results');
  const idRequerimientoContainer = document.getElementById('id-requerimiento-container');
  const numRequerimientoContainer = document.getElementById('num-requerimiento-container');
  const campoContainer = document.getElementById('campo-area-container');
  const campoMesContainer = document.getElementById('campo-mes-container');
  const bancoContainer = document.getElementById('banco-container');
  const btnGuardar = document.getElementById('btn-guardar');

  // Mostrar/Ocultar campos dinámicos para Factura, Boleta o RHE
  $('#tipo_comprobante').on('select2:select', function () {
      if (TipoSelect.value === 'Boleta' || TipoSelect.value === 'RHE' || TipoSelect.value === 'Factura' || TipoSelect.value === 'Nota' || TipoSelect.value === 'Proforma') {
          codigoComprobanteContainer.style.display = 'block';
          fechaComprobanteContainer.style.display = 'block';
      } else {
          codigoComprobanteContainer.style.display = 'none';
          fechaComprobanteContainer.style.display = 'none';
      }

      // Primero, verifica "Sin Requerimiento"
      if (TipoSelect.value === 'Sin Requerimiento') {
          // Bloquear y limpiar los campos de Conceptos
          conceptoNivel1.disabled = true;
          conceptoNivel2.disabled = true;
          conceptoNivel3.disabled = true;

          conceptoNivel1.value = '';
          conceptoNivel2.value = '';
          conceptoNivel3.value = '';

          // Ocultar los campos de ID Requerimiento y demás relacionados
          idRequerimientoContainer.style.display = 'none';
          numRequerimientoContainer.style.display = 'none';
          campoContainer.style.display = 'none';
      } else if (TipoSelect.value === 'Requerimiento') {
          // Bloquear y limpiar los campos de Conceptos
          conceptoNivel1.disabled = true;
          conceptoNivel2.disabled = true;
          conceptoNivel3.disabled = true;

          conceptoNivel1.value = '';
          conceptoNivel2.value = '';
          conceptoNivel3.value = '';

          // Mostrar el campo ID Requerimiento
          idRequerimientoContainer.style.display = 'block';
          numRequerimientoContainer.style.display = 'block';
          campoContainer.style.display = 'block';
      } else {
          // Habilitar los campos de Conceptos
          conceptoNivel1.disabled = false;
          conceptoNivel2.disabled = false;
          conceptoNivel3.disabled = false;

          // Ocultar el campo ID Requerimiento
          idRequerimientoContainer.style.display = 'none';
          numRequerimientoContainer.style.display = 'none';
          campoContainer.style.display = 'none';
      }

      if (TipoSelect.value === 'Boleta de pago') {
          campoMesContainer.style.display = 'block';
      } else {
          campoMesContainer.style.display = 'none';
      }

      if (TipoSelect.value === 'Deposito en cuenta') {
        // Mostrar campos relacionados
        codigoOperacionContainer.style.display = 'block';
        fechaOperacionContainer.style.display = 'block';
        bancoContainer.style.display = 'block';
    
        // Cambiar método de pago a "Transferencia" y hacerlo readonly
        $('#metodo_pago').val('transferencia').trigger('change'); // Esto actualiza Select2
        $('#metodo_pago').prop('disabled', true); // Mejor que readonly para Select2
    } else {
        // Ocultar campos relacionados
        codigoOperacionContainer.style.display = 'none';
        fechaOperacionContainer.style.display = 'none';
        bancoContainer.style.display = 'none';
    
        // Restablecer método de pago a "Efectivo" y hacerlo editable
        $('#metodo_pago').val('efectivo').trigger('change'); // Esto actualiza Select2
        $('#metodo_pago').prop('disabled', false);
    }
  });

  // Mostrar/Ocultar campo Codigo de Operacion
  $('#metodo_pago').on('select2:select', function () {
      if (metodoPagoSelect.value !== 'efectivo') {
          codigoOperacionContainer.style.display = 'block';
          fechaOperacionContainer.style.display = 'block';
          bancoContainer.style.display='block';
      } else {
          codigoOperacionContainer.style.display = 'none';
          fechaOperacionContainer.style.display = 'none';
          bancoContainer.style.display='none';
      }
  });
});
